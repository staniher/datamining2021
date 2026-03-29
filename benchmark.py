# ==========================================================
# ConSeU Cross-Model Benchmark (Qwen 3B + Mistral 7B, 4-bit)
# - Runs TriviaQA only (lighter)
# - Baselines (no logprobs):
#   ConSeU, H-only, Margin-only, Embedding dispersion
# - Metrics: AUROC/AUPRC/ECE/Brier/AURC
# - UI artifacts: risk–coverage arrays + keep mask
#
# FIXES:
#   (1) Explicit VRAM cleanup between models
#   (2) Per-model generation settings (Mistral lighter)
#   (3) Mistral: allow CPU offload with max_memory + offload_folder
#   (4) Robustness: CPU-only fallback and memory-efficient loading
# ==========================================================

import os
import re
import json
import time
import random
import gc
from dataclasses import dataclass
from typing import List, Dict, Any, Optional, Callable, Tuple

import numpy as np
from tqdm import tqdm
from datasets import load_dataset

from sklearn.metrics import roc_auc_score, average_precision_score
from sklearn.cluster import AgglomerativeClustering

from sentence_transformers import SentenceTransformer

import torch
from transformers import AutoTokenizer, AutoModelForCausalLM


# -----------------------------
# Reproducibility & text normalization
# -----------------------------

def set_seed(seed: int = 42) -> None:
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)

_ARTICLES = {"a", "an", "the"}

def normalize_answer(s: str) -> str:
    s = s.lower().strip()
    s = re.sub(r"[^a-z0-9\s]", " ", s)
    tokens = [t for t in s.split() if t not in _ARTICLES]
    return " ".join(tokens)

def extract_short_answer(s: str) -> str:
    s = s.strip()
    s = s.split("\n")[0].strip()
    s = re.sub(r"^(answer\s*:|a\s*:)\s*", "", s, flags=re.IGNORECASE).strip()
    return s

def em_any(pred: str, golds: List[str]) -> int:
    p = normalize_answer(pred)
    for g in golds:
        if p == normalize_answer(g):
            return 1
    return 0


# -----------------------------
# ConSeU core: clustering + uncertainty
# -----------------------------

def cosine_sim_matrix(X: np.ndarray) -> np.ndarray:
    Xn = X / (np.linalg.norm(X, axis=1, keepdims=True) + 1e-12)
    return Xn @ Xn.T

def semantic_clusters(E: np.ndarray, distance_threshold: float = 0.25) -> np.ndarray:
    S = cosine_sim_matrix(E)
    D = 1.0 - S
    model = AgglomerativeClustering(
        n_clusters=None,
        metric="precomputed",
        linkage="average",
        distance_threshold=distance_threshold,
    )
    return model.fit_predict(D)

def entropy_from_labels(labels: np.ndarray) -> Tuple[float, float]:
    M = len(labels)
    _, counts = np.unique(labels, return_counts=True)
    p = counts / float(M)
    H = -float(np.sum(p * np.log(p + 1e-12)))
    max_mass = float(np.max(p))
    return H, max_mass

def conseu_score(H: float, max_mass: float, lam: float = 1.0) -> float:
    return float(H + lam * (1.0 - max_mass))

def embedding_dispersion(E: np.ndarray) -> float:
    if E.shape[0] <= 1:
        return 0.0
    S = cosine_sim_matrix(E)
    D = 1.0 - S
    iu = np.triu_indices(D.shape[0], k=1)
    return float(np.mean(D[iu]))


# -----------------------------
# Calibration / selective metrics
# -----------------------------

def ece_score(conf: np.ndarray, correct: np.ndarray, n_bins: int = 15) -> float:
    conf = np.clip(conf, 0.0, 1.0)
    bins = np.linspace(0.0, 1.0, n_bins + 1)
    ece = 0.0
    for b0, b1 in zip(bins[:-1], bins[1:]):
        idx = (conf >= b0) & (conf < b1)
        if np.any(idx):
            acc = float(np.mean(correct[idx]))
            cbar = float(np.mean(conf[idx]))
            ece += (np.sum(idx) / len(conf)) * abs(acc - cbar)
    return float(ece)

def risk_coverage(correct: np.ndarray, scores: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
    order = np.argsort(scores)
    y = correct[order]
    N = len(y)
    risks, covers = [], []
    for k in range(1, N + 1):
        kept = y[:k]
        risks.append(1.0 - float(np.mean(kept)))
        covers.append(k / float(N))
    return np.array(risks), np.array(covers)

def aurc(risks: np.ndarray, covers: np.ndarray) -> float:
    if hasattr(np, "trapezoid"):
        return float(np.trapezoid(risks, covers))
    return float(np.trapz(risks, covers))

def selective_risk(y: np.ndarray, u: np.ndarray, thr: float) -> float:
    keep = (u <= thr)
    if keep.sum() == 0:
        return 1.0
    return 1.0 - float(np.mean(y[keep]))

def choose_threshold_for_risk(u_cal: np.ndarray, y_cal: np.ndarray, risk_target: float = 0.3) -> float:
    candidates = np.unique(u_cal)
    best_thr = float(np.min(candidates))
    best_cov = 0.0
    for thr in candidates:
        keep = (u_cal <= thr)
        cov = float(np.mean(keep))
        r = selective_risk(y_cal, u_cal, float(thr))
        if r <= risk_target and cov >= best_cov:
            best_thr = float(thr)
            best_cov = cov
    return float(best_thr)


# -----------------------------
# Decision rule: cluster-majority vote
# -----------------------------

def pick_final_by_cluster_majority(gens: List[str], labels: np.ndarray) -> Tuple[str, float, int]:
    if len(gens) == 0:
        return "", 0.0, -1
    uniq, counts = np.unique(labels, return_counts=True)
    best_idx = int(np.argmax(counts))
    best_label = int(uniq[best_idx])
    max_mass = float(counts[best_idx] / float(len(labels)))
    members = [gens[i] for i in range(len(gens)) if int(labels[i]) == best_label]

    norm_members = [normalize_answer(m) for m in members]
    freq: Dict[str, int] = {}
    rep: Dict[str, str] = {}
    for orig, norm in zip(members, norm_members):
        freq[norm] = freq.get(norm, 0) + 1
        if norm not in rep:
            rep[norm] = orig
    best_norm = max(freq.items(), key=lambda kv: kv[1])[0]
    final = rep[best_norm]
    return final, max_mass, best_label


# -----------------------------
# Data model + dataset loader
# -----------------------------

@dataclass
class QAExample:
    prompt: str
    gold_answers: List[str]
    meta: Optional[Dict[str, Any]] = None

def load_triviaqa_rc_nocontext(split: str = "validation", limit: int = 600) -> List[QAExample]:
    ds = load_dataset("mandarjoshi/trivia_qa", "rc.nocontext", split=split)
    if limit is not None:
        ds = ds.select(range(min(limit, len(ds))))
    out: List[QAExample] = []
    for ex in ds:
        q = re.sub(r"\s+", " ", ex["question"]).strip()
        ans = ex["answer"]
        golds: List[str] = []
        if isinstance(ans, dict):
            if ans.get("value"):
                golds.append(ans["value"])
            aliases = ans.get("aliases") or []
            golds.extend([a for a in aliases if a])
        prompt = f"Answer the trivia question with a short factual phrase. Do not add explanations.\nQ: {q}\nA:"
        out.append(QAExample(prompt=prompt, gold_answers=golds, meta={"dataset": "triviaqa"}))
    return out


# -----------------------------
# CUDA cleanup
# -----------------------------

def cleanup_cuda() -> None:
    gc.collect()
    if torch.cuda.is_available():
        torch.cuda.empty_cache()
        try:
            torch.cuda.ipc_collect()
        except Exception:
            pass
    gc.collect()


# -----------------------------
# Local HF generator (GPU + 4-bit, optional CPU offload)
# -----------------------------

class LocalHFGenerator:
    def __init__(
        self,
        model_id: str,
        allow_cpu_offload: bool = False,
        offload_folder: str = "offload_cache",
        max_memory_gpu: str = "3.6GiB",
        max_memory_cpu: str = "64GiB",
    ):
        self.model_id = model_id
        self.device = "cuda" if torch.cuda.is_available() else "cpu"

        print("CUDA available:", torch.cuda.is_available())
        if torch.cuda.is_available():
            try:
                free, total = torch.cuda.mem_get_info()
                print(f"GPU VRAM free/total: {free/1e9:.2f}GB / {total/1e9:.2f}GB")
            except Exception:
                pass

        self.tokenizer = AutoTokenizer.from_pretrained(model_id, use_fast=True)
        if self.tokenizer.pad_token_id is None:
            self.tokenizer.pad_token = self.tokenizer.eos_token

        if self.device == "cuda":
            from transformers import BitsAndBytesConfig

            bnb_config = BitsAndBytesConfig(
                load_in_4bit=True,
                bnb_4bit_use_double_quant=True,
                bnb_4bit_quant_type="nf4",
                bnb_4bit_compute_dtype=torch.float16,
                # Key flag: allows some FP32 modules to live on CPU when auto device_map offloads
                llm_int8_enable_fp32_cpu_offload=allow_cpu_offload,
            )

            kwargs: Dict[str, Any] = dict(
                quantization_config=bnb_config,
                device_map="auto",
                low_cpu_mem_usage=True,
            )

            if allow_cpu_offload:
                os.makedirs(offload_folder, exist_ok=True)
                kwargs["offload_folder"] = offload_folder
                kwargs["max_memory"] = {0: max_memory_gpu, "cpu": max_memory_cpu}

            self.model = AutoModelForCausalLM.from_pretrained(model_id, **kwargs)
        else:
            # CPU Path with memory-efficient loading
            try:
                self.model = AutoModelForCausalLM.from_pretrained(model_id, torch_dtype=torch.bfloat16, low_cpu_mem_usage=True)
            except Exception:
                self.model = AutoModelForCausalLM.from_pretrained(model_id, torch_dtype=torch.float32, low_cpu_mem_usage=True)
            self.model.to(self.device)

        self.model.eval()
        try:
            print("Model device:", next(self.model.parameters()).device)
        except Exception:
            print("Model device: (quantized / device_map)")

    @torch.inference_mode()
    def generate(self, prompt: str, n: int, temperature: float, max_new_tokens: int) -> List[str]:
        inputs = self.tokenizer(prompt, return_tensors="pt").to(self.model.device)
        outs = self.model.generate(
            **inputs,
            do_sample=True,
            temperature=temperature,
            top_p=0.95,
            num_return_sequences=n,
            max_new_tokens=max_new_tokens,
            pad_token_id=self.tokenizer.eos_token_id,
            use_cache=True,
        )
        texts = self.tokenizer.batch_decode(outs, skip_special_tokens=True)
        gens: List[str] = []
        for t in texts:
            comp = t[len(prompt):].strip() if t.startswith(prompt) else t.strip()
            gens.append(extract_short_answer(comp))
        return gens

    def close(self) -> None:
        try:
            del self.model
        except Exception:
            pass
        try:
            del self.tokenizer
        except Exception:
            pass


# -----------------------------
# ConSeU evaluator
# -----------------------------

@dataclass
class ConSeUConfig:
    n_samples: int = 8
    temperature: float = 0.7
    max_new_tokens: int = 40
    cluster_distance_threshold: float = 0.25
    lam: float = 1.0
    embed_model_name: str = "sentence-transformers/all-MiniLM-L6-v2"
    seed: int = 42

class ConSeUEvaluator:
    def __init__(self, cfg: ConSeUConfig):
        self.cfg = cfg
        set_seed(cfg.seed)
        self.embedder = SentenceTransformer(cfg.embed_model_name)

    def score_from_generations(self, gens: List[str]) -> Dict[str, Any]:
        E = self.embedder.encode(gens, convert_to_numpy=True, normalize_embeddings=False)
        labels = semantic_clusters(E, distance_threshold=self.cfg.cluster_distance_threshold)
        H, max_mass_all = entropy_from_labels(labels)

        u_conseu = conseu_score(H, max_mass_all, lam=self.cfg.lam)
        u_H = float(H)
        u_margin = float(1.0 - max_mass_all)
        u_disp = embedding_dispersion(E)

        final, max_mass_dom, dom_label = pick_final_by_cluster_majority(gens, labels)

        return {
            "H": float(H),
            "max_mass": float(max_mass_all),
            "u_conseu": float(u_conseu),
            "u_H": float(u_H),
            "u_margin": float(u_margin),
            "u_dispersion": float(u_disp),
            "cluster_labels": labels.tolist(),
            "dominant_cluster": int(dom_label),
            "dominant_cluster_mass": float(max_mass_dom),
            "final_answer": final,
        }

    def score_prompt(self, prompt: str, generate_fn: Callable[..., List[str]]) -> Dict[str, Any]:
        gens = generate_fn(prompt, self.cfg.n_samples, self.cfg.temperature, self.cfg.max_new_tokens)
        s = self.score_from_generations(gens)
        return {"prompt": prompt, "generations": gens, **s}

    def eval_scores(self, y_correct: np.ndarray, u_scores: np.ndarray) -> Dict[str, float]:
        u = np.array(u_scores, dtype=float)

        if len(np.unique(y_correct)) > 1:
            auroc = roc_auc_score(1 - y_correct, u)
            auprc = average_precision_score(1 - y_correct, u)
        else:
            auroc, auprc = float("nan"), float("nan")

        conf = np.exp(-u)
        conf = (conf - conf.min()) / (conf.max() - conf.min() + 1e-12)
        ece = ece_score(conf, y_correct)
        brier = float(np.mean((conf - y_correct) ** 2))

        risks, covers = risk_coverage(y_correct, u)
        return {
            "AUROC_error_detection": float(auroc),
            "AUPRC_error_detection": float(auprc),
            "ECE": float(ece),
            "Brier": float(brier),
            "AURC": aurc(risks, covers),
        }


# -----------------------------
# Artifact saving
# -----------------------------

def save_artifacts(tag: str, u_cal, y_cal, u_test, y_test, keep_mask_test: Optional[np.ndarray] = None) -> None:
    os.makedirs("artifacts", exist_ok=True)
    risks, covers = risk_coverage(y_test, u_test)
    if keep_mask_test is None:
        keep_mask_test = np.ones_like(y_test, dtype=bool)
    np.savez(
        f"artifacts/riskcurve_{tag}.npz",
        u_cal=u_cal,
        y_cal=y_cal,
        u_test=u_test,
        y_test=y_test,
        risks=risks,
        covers=covers,
        keep_mask_test=keep_mask_test.astype(np.int8),
    )


# -----------------------------
# Benchmark runner
# -----------------------------

def run_triviaqa_benchmark(
    model_tag: str,
    examples: List[QAExample],
    evaluator: ConSeUEvaluator,
    generate_fn: Callable[..., List[str]],
    cal_frac: float = 0.3,
    risk_target: float = 0.3,
) -> Dict[str, Any]:
    idx = np.arange(len(examples))
    np.random.shuffle(idx)
    n_cal = max(1, int(len(idx) * cal_frac))
    cal_idx, test_idx = idx[:n_cal], idx[n_cal:]

    def eval_split(split_idx: np.ndarray, split_name: str) -> Tuple[List[Dict[str, Any]], np.ndarray]:
        recs: List[Dict[str, Any]] = []
        y: List[int] = []
        t0 = time.time()
        for j, i in enumerate(tqdm(split_idx, desc=f"{model_tag}/triviaqa/{split_name}", total=len(split_idx))):
            ex = examples[int(i)]
            r = evaluator.score_prompt(ex.prompt, generate_fn)
            y_i = em_any(r["final_answer"], ex.gold_answers)
            r["correct"] = int(y_i)
            recs.append(r)
            y.append(y_i)
            if (j + 1) % 50 == 0:
                dt = time.time() - t0
                print(f"[{model_tag}/triviaqa/{split_name}] {j+1}/{len(split_idx)} done | elapsed {dt/60:.1f} min")
        return recs, np.array(y, dtype=int)

    cal_recs, y_cal = eval_split(cal_idx, "cal")
    test_recs, y_test = eval_split(test_idx, "test")

    u_cal_conseu = np.array([r["u_conseu"] for r in cal_recs], dtype=float)
    u_test_conseu = np.array([r["u_conseu"] for r in test_recs], dtype=float)

    u_test_H = np.array([r["u_H"] for r in test_recs], dtype=float)
    u_test_margin = np.array([r["u_margin"] for r in test_recs], dtype=float)
    u_test_disp = np.array([r["u_dispersion"] for r in test_recs], dtype=float)

    metrics_all = {
        "ConSeU": evaluator.eval_scores(y_test, u_test_conseu),
        "H_only": evaluator.eval_scores(y_test, u_test_H),
        "Margin_only": evaluator.eval_scores(y_test, u_test_margin),
        "Dispersion": evaluator.eval_scores(y_test, u_test_disp),
    }

    thr = choose_threshold_for_risk(u_cal_conseu, y_cal, risk_target=risk_target)
    keep = (u_test_conseu <= thr)
    coverage = float(np.mean(keep)) if len(u_test_conseu) else 0.0
    risk = 1.0 - float(np.mean(y_test[keep])) if keep.sum() > 0 else 1.0

    save_artifacts(f"{model_tag}_triviaqa_conseu", u_cal_conseu, y_cal, u_test_conseu, y_test, keep_mask_test=keep)

    return {
        "model": model_tag,
        "dataset": "triviaqa",
        "n_total": len(examples),
        "n_cal": int(len(cal_idx)),
        "n_test": int(len(test_idx)),
        "risk_target": float(risk_target),
        "threshold_conseu": float(thr),
        "metrics_test": metrics_all,
        "selective_test_conseu": {"coverage": coverage, "risk": risk},
        "sample_rows": test_recs[:3],
    }


# -----------------------------
# Main
# -----------------------------

def main() -> None:
    limit = 600
    cal_frac = 0.3
    risk_target = 0.3

    temperature = 0.7
    delta = 0.25
    lam = 1.0

    trivia = load_triviaqa_rc_nocontext(split="validation", limit=limit)

    model_ids = {
        "qwen2p5_3b": "Qwen/Qwen2.5-3B-Instruct",
        "mistral_7b": "mistralai/Mistral-7B-Instruct-v0.2",
    }

    per_model_gen = {
        "qwen2p5_3b": {"n_samples": 8, "max_new_tokens": 40},
        # Reduce KV/cache pressure for 7B
        "mistral_7b": {"n_samples": 4, "max_new_tokens": 20},
    }

    results: Dict[str, Any] = {
        "setup": {
            "limit": limit,
            "temperature": temperature,
            "delta": delta,
            "lam": lam,
            "cal_frac": cal_frac,
            "risk_target": risk_target,
            "embedder": "sentence-transformers/all-MiniLM-L6-v2",
            "notes": "Mistral uses 4-bit + CPU offload + reduced generation settings.",
        },
        "runs": {},
    }

    cleanup_cuda()

    for tag, mid in model_ids.items():
        print(f"\n==============================\nRunning model: {tag} | {mid}\n==============================\n")

        cleanup_cuda()

        gen_cfg = per_model_gen.get(tag, {"n_samples": 8, "max_new_tokens": 40})

        cfg = ConSeUConfig(
            n_samples=int(gen_cfg["n_samples"]),
            temperature=float(temperature),
            max_new_tokens=int(gen_cfg["max_new_tokens"]),
            cluster_distance_threshold=float(delta),
            lam=float(lam),
            embed_model_name="sentence-transformers/all-MiniLM-L6-v2",
            seed=42,
        )
        evaluator = ConSeUEvaluator(cfg)

        # IMPORTANT: offload ONLY for Mistral
        allow_offload = (tag == "mistral_7b")

        gen = LocalHFGenerator(
            model_id=mid,
            allow_cpu_offload=allow_offload,
            offload_folder=f"offload_{tag}",
            max_memory_gpu="3.6GiB",
            max_memory_cpu="64GiB",
        )

        res = run_triviaqa_benchmark(
            model_tag=tag,
            examples=trivia,
            evaluator=evaluator,
            generate_fn=gen.generate,
            cal_frac=cal_frac,
            risk_target=risk_target,
        )
        results["runs"][tag] = res

        gen.close()
        del gen
        del evaluator
        cleanup_cuda()

    with open("resultats_crossmodel_triviaqa.json", "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    print("\n========== SAVED ==========\nresultats_crossmodel_triviaqa.json\n")
    print(json.dumps(results, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
