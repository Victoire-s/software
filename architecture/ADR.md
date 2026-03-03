# ADR

Architecture Decision Record

---
# Status

Proposé

---
# Context

Le **client est une entreprise** qui possède un parking. Elle souhaite **organiser la gestion de réservation de places de parking**.
Les utilisateurs seront les employées de l'entreprise ; l'application devra donc être facile d'utilisation.
Son rôle principal sera de **gérer, archiver et planifier les réservations** des places de parking en prenant en compte le status de l'employé et du type de véhicule (manager / véhicule électrique ou non). Puisque l'application définira des rôles, un système d'authentification sera nécessaire. Il faudra mettre en place un système de check-in. l'utilisateur sera autonome dans sa réservation. Dashboard avec metrics

---
# Décisions

## **Choix d'architecture**
→ **Application monolithique**
Projet trop petit pour faire des micro-services
Durée de réalisation trop court pour se permettre des micro-services.
Le service est uniquement destiné à cette entreprise donc pas besoin de scalabilité.

**Composants**

→ 2 conteneurs **Docker**
- front-end
- back-end (business logic + database + queue)

## **Type d'application**
→ **Application Web**
- manque de temps
- importance/scope insuffisant pour une application executable dédiée

## **Stack technique**

**Front-end**

→ **React**
- Stack moderne (comparé à PHP) qui nous permettra notamment d'intégrer des éléments dynamique (dashboard, visualisation parking slot)
- Largement utilisée

**Back-end**

→ **Python**
- Bibliothèques et outils importants.
- Rapide à développer.
- La logique métier ne nécessitant pas de calculs complexes, choisir un langage bas niveau ne serait pas nécessaire et rendrait le développement bien plus long.

→ **Sanic** (pour le web server)

Pour ces deux service, l'expérience d''équipe nous a guidé vers le choix de ces technologies.

**Databases**

→ **MySQL**
- Léger et suffisant pour les petits projets.

**Queue / Messagerie**

→ **RabbitMQ**
- Mieux adaptés aux petits projets.
- Complexité très légère du système de queue (utilisé uniquement pour l'envoie d'emails de confirmation). Kafka était une autre option mais est plus lourd et complexe à mettre en place.

---
# Conséquences

**Avantages**
- Architecture simple à développer, tester et déployer.
- Rapidité de mise en œuvre compatible avec les délais.
- Stack maîtrisée par l’équipe, limitant les risques.

**Inconvénient**
- Evolution vers microservice + couteux
- Manque d'une application mobile: complexifie l'utilisation.
- React est complexe au débugage.

---

## **Règles métier — Durée de réservation**

### Décision : jours ouvrables pour les employés, jours calendaires pour les managers

**Employés (EMPLOYEE)**
- La durée maximale d'une réservation est de **5 jours ouvrables** (lundi au vendredi inclus).
- Les week-ends ne sont pas comptés : une réservation du lundi au lundi suivant représente 6 jours ouvrables et est donc refusée.
- Implémentation : fonction `_count_working_days(start, end)` côté backend (Python, `timedelta` itératif) et `countWorkingDays(start, end)` côté frontend (JavaScript, `Date.getDay()`).

**Managers (MANAGER)**
- La durée maximale est de **30 jours calendaires** (semaines + week-ends inclus).

**Justification**
- Le parking est un équipement professionnel ; les réservations n'ont de sens que les jours de travail.
- Autoriser une réservation « du lundi au lundi » aurait représenté 8 jours calendaires pour seulement 6 jours de présence potentielle, ce qui aurait été incohérent avec la règle des 5 jours.
- Les fériés ne sont pas gérés dans cette version (hors périmètre initial, périmètre entreprise France uniquement).

