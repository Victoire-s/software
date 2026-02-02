# ADR

Architecture Decision Record

---
### Status

Proposed

---
### Context

Le client est une entreprise qui possède un parking. Elle souhaite organiser la gestion de réservation de places de parking.
L'application doit pouvoir être utilisé et gérer par des utilisateurs lambda.
Son rôle principal sera de gérer, archiver et planifier les réservations des places de parking en prenant en compte le status de l'employé et du type de véhicule pour préciser: manager / véhicule électrique ou non. Un service de paiement ne sera pas nécessaire. Puisque l'application définira des rôles, un système d'authentification sera nécessaire. Il faudra mettre en place un système de check-in. l'utilisateur sera autonome dans sa réservation. Dashboard avec metrics

---
# Décision

##### **Choix d'architecture**
→ Application monolithique
Projet trop petit pour faire des micro-service
Durée de réalisation trop court pour se permettre des micro-service.
Le service est uniquement destiné à cette entreprise donc pas besoin de scalabilité.

##### **Type d'application**
→ Application Web
Pourquoi?
- manque de temps
- importance insuffisante pour une application executable dédiée

##### **Stack technique**
- React (front)
Stack moderne (comparé à PHP) qui nous permettra notamment d'intégrer des éléments dynamique (dashboard, visualisation parking slot)

- Python (back) avec Sanic pour le web server
Rapide à mettre en place.

→ Pour ces deux service, l'expérience d''équipe nous a guidé vers le choix de ces technologies.

- MySQL
Léger et suffisant pour les petits projet.

- RabbitMQ
La spec demande une queue pour recevoir les réservation
Mieux adapté aux petits projets.


- 2 conteneurs
	- front
	- le reste

---
### Conséquences

**Avantages**
- Architecture simple à développer, tester et déployer.
- Rapidité de mise en œuvre compatible avec les délais.
- Stack maîtrisée par l’équipe, limitant les risques.

**Inconvénient**
- Evolution vers microservice + couteux
- Manque d'une application mobile: complexifie l'utilisation.
- React est complexe au débugage.