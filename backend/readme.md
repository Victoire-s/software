# Parking Reservation System

Application interne pour gérer la réservation de places de parking (créneaux demi-journée), avec check-in via QR code, back-office secrétariat, dashboard management, historique et émission d’événements vers une queue (email de confirmation).

---

## Structure du projet

```text
/
  backend/      # API (Python + Sanic)
  frontend/     # Web app (React)
  docs/         # ADR + diagrammes (C4)
  scripts/      # build/run/test (scripts simples)
  docker-compose.yml


## Run 

cd backend
python3 -m venv .venv
source .venv/bin/activate

python3 -m pip install --upgrade pip
python3 -m pip install -r requirements.txt

python3 -m pip install -r requirements-dev.txt


## Variables d’environnement
DATABASE_URL

Exemples :

SQLite (dev local) :

sqlite+aiosqlite:///./dev.db

SQLite in-memory (tests) :

sqlite+aiosqlite:///:memory:

MySQL (docker/prod) :

mysql+asyncmy://user:password@mysql:3306/parking

Pour exporter une variable en local :

export DATABASE_URL="sqlite+aiosqlite:///./dev.db"


Lancer l’API en local

Dans backend/ (venv actif) :

python3 app.py


L’API démarre par défaut sur :

http://localhost:8000


Endpoints
POST /hello

Stocke un message en base et retourne l’enregistrement stocké.

Exemple :

curl -X POST http://localhost:8000/hello \
  -H "Content-Type: application/json" \
  -d '{"message":"hello"}'


Réponse attendue (exemple) :

{ "id": 1, "message": "hello" }



Lancer tous les tests

Dans backend/ (venv actif) :

python3 -m pytest -q

Lancement prod : 
cd backend
source .venv/bin/activate

python3 -m sanic app:create_app --factory --reload --host=0.0.0.0 --port=8000

Lancement rabbitmq : docker compose up -d rabbitmq

Lancer le consumer : python3 consume_hello.py


