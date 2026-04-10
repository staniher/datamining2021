import pytest
from app import app, db, Patient
from datetime import datetime, timedelta

@pytest.fixture
def client():
    # Configuration de l'application pour les tests
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:' # Utilisation d'une base de données en mémoire
    with app.test_client() as client:
        with app.app_context():
            db.create_all() # Création des tables
        yield client
        with app.app_context():
            db.drop_all() # Nettoyage après les tests

def test_home_page(client):
    # Test de la page d'accueil
    response = client.get('/')
    assert response.status_code == 200
    assert b"Nouveau Patient" in response.data

def test_add_patient(client):
    # Test de l'ajout d'un patient et de la prédiction
    response = client.post('/predict', data={
        'nom': 'Patient Test',
        'genre': '1',
        'age': '25',
        'maladie': '54',
        'service': '1',
        'date': '2023-01-01'
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b"Patient Test" in response.data

    # Vérification en base de données
    with app.app_context():
        patient = Patient.query.filter_by(nom='Patient Test').first()
        assert patient is not None
        assert patient.genre == 1

def test_delete_patient(client):
    # Test de la suppression d'un patient
    with app.app_context():
        p = Patient(nom='A Supprimer', genre=0, age=30, maladie=15, service=2,
                    date_entree=datetime.now(), date_sortie_predite=datetime.now())
        db.session.add(p)
        db.session.commit()
        patient_id = p.id

    response = client.get(f'/delete/{patient_id}', follow_redirects=True)
    assert response.status_code == 200

    with app.app_context():
        patient = Patient.query.get(patient_id)
        assert patient is None

def test_list_patients(client):
    # Test de l'affichage de la liste
    response = client.get('/patients')
    assert response.status_code == 200
    assert b"Gestion des Patients" in response.data

def test_dashboard(client):
    # Test du tableau de bord
    response = client.get('/dashboard')
    assert response.status_code == 200
    assert b"Statistiques" in response.data
