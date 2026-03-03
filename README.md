# ParkingApp — Gestion des réservations de parking

Application web de réservation de places de parking pour les employés de l'entreprise.
Elle remplace l'ancien process par mail/Excel géré par les secrétaires.

---

## Démarrage rapide (ops / développeurs)

### Prérequis

- [Docker](https://www.docker.com/) et Docker Compose installés
- Ports libres : `3000` (frontend), `8000` (backend), `3306` (MySQL), `5672` / `15672` (RabbitMQ)

### Lancer l'application

```bash
./run.sh
```

L'application est accessible sur **http://localhost:3000**

### Construire les images

```bash
./build.sh
```

### Lancer les tests

```bash
./test.sh
```

---

## Guide utilisateur

### 1. Se connecter

1. Ouvrir **http://localhost:3000** dans votre navigateur.
2. Entrer votre **adresse e-mail professionnelle**.
3. Si c'est votre première connexion, cliquer sur **"S'inscrire"** et renseigner votre prénom et nom.
4. Cliquer sur **"Se connecter"** (ou **"S'inscrire"**).

> Aucun mot de passe requis : l'authentification est basée sur votre e-mail professionnel.

---

### 2. Réserver une place (Employé)

1. Sur la page principale, vous voyez le **plan du parking** (6 rangées A à F, 10 places par rangée).
   - Les places **blanches/bleues** sont disponibles.
   - Les places **rouges** sont déjà réservées.
   - Les places avec l'icône **⚡** (rangées A et F) disposent d'une borne de recharge électrique.

2. Si vous avez besoin de recharger votre véhicule, cochez **"J'ai besoin d'une borne électrique"** — seules les rangées A et F s'afficheront.

3. **Cliquez sur une place disponible** pour la sélectionner (elle devient bleue foncé).

4. Dans le panneau de réservation à droite :
   - Sélectionnez la **date de début** (aujourd'hui ou une date future).
   - Pour plusieurs jours, décochez *"Réserver pour un seul jour"* et choisissez la **date de fin**.
   - **Maximum : 5 jours ouvrables** (lundi au vendredi). Les week-ends ne sont pas comptabilisés.

5. Cliquer sur **"Réserver"**.

> **Confirmation** : un e-mail de confirmation vous sera envoyé automatiquement.

---

### 3. Faire son check-in

Le check-in est **obligatoire** le jour de votre réservation. Si vous ne le faites pas avant **11h00**, votre place est automatiquement libérée et peut être reprise par quelqu'un d'autre.

#### Option A — Via l'application

1. Connectez-vous à l'application.
2. Dans la section **"Mes Réservations"**, repérez la réservation du jour.
3. Un badge orange **"⚠ Check-in requis"** s'affiche si le check-in n'a pas encore été fait.
4. Cliquer sur le bouton **"Check-in"**.
5. Le badge devient vert **"✓ Check-in effectué"** : votre place est confirmée.

#### Option B — Via le QR code (recommandé sur mobile)

Chaque place de parking dispose d'un QR code affiché physiquement.

1. Arrivez à votre place de parking.
2. **Scannez le QR code** avec votre téléphone (application de scan ou appareil photo).
3. Vous êtes redirigé vers l'application. Si vous n'êtes pas connecté, connectez-vous.
4. Le check-in est effectué automatiquement pour la réservation active de cette place.

> Le QR code encode directement l'identifiant de la place (ex. `B04`). L'application vérifie que vous avez bien une réservation active pour cette place aujourd'hui.

---

### 4. Consulter ses réservations

Dans la section **"Mes Réservations"** de la page principale :

| Statut | Signification |
|---|---|
| Badge vert **✓ Check-in effectué** | Vous êtes enregistré pour cette journée |
| Badge orange **⚠ Check-in requis** | À faire avant 11h, sinon la place est libérée |
| Carte grisée | Réservation passée (historique) |

---

### 5. Profils et droits

| Profil | Ce qu'il peut faire |
|---|---|
| **Employé** | Réserver jusqu'à 5 jours ouvrables, faire son check-in, voir ses réservations |
| **Manager** | Idem + réserver jusqu'à 30 jours calendaires + accès au tableau de bord |
| **Secrétaire** | Accès admin complet : gérer utilisateurs, modifier/annuler toute réservation |

---

### 6. Tableau de bord (Manager uniquement)

Le tableau de bord affiche en temps réel :

- **Taux d'occupation** : pourcentage de places utilisées
- **Places libres** : nombre de places disponibles maintenant
- **No-shows** : proportion de réservations sans check-in
- **Proportion électrique** : part des places avec borne utilisées

---

### 7. Administration (Secrétaire uniquement)

L'onglet Admin permet de :

- Voir et modifier **tous les utilisateurs** (créer, changer de rôle, supprimer)
- Voir et modifier **toutes les réservations**
- Forcer un check-in ou annuler une réservation manuellement

---

## Plan du parking

```
ENTRÉE
│
│   A01 A02 A03 A04 A05 A06 A07 A08 A09 A10   <- Rangée A (⚡ électrique, mur)
│   B01 B02 B03 B04 B05 B06 B07 B08 B09 B10   <- Rangée B
│   C01 C02 C03 C04 C05 C06 C07 C08 C09 C10   <- Rangée C
│   D01 D02 D03 D04 D05 D06 D07 D08 D09 D10   <- Rangée D
│   E01 E02 E03 E04 E05 E06 E07 E08 E09 E10   <- Rangée E
│   F01 F02 F03 F04 F05 F06 F07 F08 F09 F10   <- Rangée F (⚡ électrique, mur)
│
SORTIE
```

- **Rangées A et F** : places avec bornes de recharge électrique (gratuites pour l'employé)
- **Rangées B–E** : places standard, organisées par paires [A B | C D | E F]
- **60 places au total**, toutes de taille identique

---

## Architecture technique

| Composant | Technologie |
|---|---|
| Frontend | React 19 + Vite + TypeScript |
| Backend | Python 3.13 + Sanic |
| Base de données | MySQL 8.4 |
| File de messages | RabbitMQ 3 |
| Conteneurs | Docker Compose |

Documentation d'architecture détaillée : [architecture/ADR.md](architecture/ADR.md)
Diagramme C4 : [architecture/C4_Model.png](architecture/C4_Model.png)

---

## Règles métier importantes

- **Durée max employé** : 5 jours **ouvrables** (lundi–vendredi). Une réservation du lundi au vendredi = 5 jours ✓. Du lundi au lundi suivant = 6 jours ✗.
- **Durée max manager** : 30 jours calendaires.
- **Check-in obligatoire avant 11h00** chaque jour de réservation.
- **Places électriques** : uniquement les rangées A et F. La recharge est prise en charge par l'entreprise.
- **Réservation le jour même** : possible si des places sont disponibles.
