# Topological Uncertainty Quantification (TUQ) for LLMs

This project implements a novel framework for quantifying uncertainty in Large Language Model (LLM) reasoning traces using **Cellular Sheaf Theory**.

## Overview

Traditional uncertainty quantification (UQ) for LLMs focuses on token probabilities (entropy, variance). Our approach, the **Local Cohomology Residual (LCR)**, measures structural and logical inconsistencies within a single reasoning chain by modeling it as a sheaf over a simplicial complex.

### Key Features
- **Sheaf-Theoretic Framework**: Uses the 0-Laplacian of a cellular sheaf to detect inconsistencies.
- **Intra-Sample Consistency**: Evaluates a single reasoning trace without needing multiple samples.
- **SBERT Integration**: Uses semantic embeddings to construct the sheaf signals.
- **GSM8K Evaluation**: Benchmarked on the GSM8K dataset with synthetic hallucination injection.

## Project Structure

- `tuq_engine.py`: The core experimental engine. It loads the dataset, injects hallucinations, computes LCR, and generates figures.
- `manuscript_builder.py`: A script to generate a publication-ready Word document (`GSM8K_TUQ_Results.docx`) including the methodology and actual results.
- `figures/`: Directory containing output plots (ROC curves, distributions) and exported metrics.
- `GSM8K_TUQ_Results.docx`: The final scientific manuscript.

## Installation

Ensure you have the following dependencies installed:

```bash
pip install datasets sentence-transformers matplotlib seaborn scikit-learn python-docx
```

## How to Run

1. **Run the Experiment**:
   ```bash
   python tuq_engine.py
   ```
   This will generate plots in the `figures/` directory and a `metrics.txt` file.

2. **Generate the Manuscript**:
   ```bash
   python manuscript_builder.py
   ```
   This will create the `GSM8K_TUQ_Results.docx` file using the results from the previous step.

## Results Summary

In our experiments on a subset of GSM8K:
- **ROC-AUC**: ~0.78
- **Consistency Criterion**: LCR = 0 implies a globally consistent reasoning trace under the defined constraints.
- **Significance**: Effectively separates logically sound reasoning from structural hallucinations.

## References

- Curry, J. (2014). *Sheaves, cosheaves and applications*. PhD thesis, University of Pennsylvania.
- Hansen, J., & Ghrist, R. (2019). *Toward a spectral theory of cellular sheaves*. Journal of Applied and Computational Topology.
- Da, L., et al. (2025). *Understanding the Uncertainty of LLM Explanations: A Perspective Based on Reasoning Topology*. arXiv:2502.17026.
