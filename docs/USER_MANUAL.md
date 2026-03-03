# Manuel Utilisateur - Application de Réservation de Parking

Bienvenue sur l'application de réservation de parking. Cette application a été conçue pour remplacer l'ancien système basé sur Excel et les échanges de mails, afin de vous offrir une autonomie complète sur vos réservations de places de parking.

L'application est accessible depuis n'importe quel navigateur web moderne et s'adapte à la fois aux ordinateurs de bureau et aux smartphones.

---

## 🚙 1. Profil Employé (Utilisateur Standard)

Dès votre connexion, vous accédez à votre profil employé. Ce profil vous permet de consulter les disponibilités et de réserver une place.

### Les Règles de Réservation
*   **Durée maximale :** Vous pouvez réserver une place pour un maximum de **5 jours ouvrés consécutifs**. Il n'est plus possible de bloquer une place pour un mois entier.
*   **Véhicules Électriques/Hybrides :** Si vous avez besoin de recharger votre véhicule, vous devez impérativement choisir une place située dans les **rangées A ou F**. Ces places disposent de bornes de recharge murales (l'électricité est prise en charge par l'entreprise).
*   **Réservation pour le jour même :** Il est tout à fait possible de réserver une place pour la journée en cours si l'une d'elles est encore disponible sur le plan.

### Comment Réserver une Place ?
1.  **Consulter le plan :** Sur l'écran principal, une carte interactive du parking affiche les 60 places réparties sur 6 rangées (A à F). Les places libres sont visuellement distinctes des places occupées.
2.  **Sélectionner les dates :** Choisissez votre date de début et votre date de fin de réservation.
3.  **Choisir une place :** Cliquez sur une place libre sur le plan. Les places avec l'icône "⚡" (Rangées A et F) sont réservées aux véhicules électriques.
4.  **Confirmer :** Cliquez sur le bouton de réservation. Vous recevrez une confirmation (et un email vous sera envoyé automatiquement).

### Le Check-in (Obligatoire)
Afin de lutter contre les "no-shows" (réservations non honorées), **le check-in est obligatoire**.
*   **Comment faire :** Lorsque vous garez votre voiture, scannez le **QR code** affiché sur votre place de parking à l'aide de votre smartphone, ou cliquez sur le bouton "Check-in" depuis l'interface de vos réservations, le jour même de votre réservation.
*   **Règle de libération à 11h :** Si vous n'avez pas validé votre check-in avant **11h00** le jour de votre réservation, le système considérera que vous êtes absent. **Votre réservation sera automatiquement annulée pour la journée en cours**, et la place redeviendra disponible pour un autre collaborateur.

### Historique et Annulation
*   Vous pouvez consulter l'historique complet de toutes vos réservations (passées et futures) depuis votre tableau de bord.
*   Si vous avez un empêchement, vous pouvez annuler votre réservation vous-même en cliquant sur le bouton **"Annuler"** depuis la liste de vos réservations en cours. La place sera instantanément libérée sur le plan.

---

## 📊 2. Profil Manager

Si vous disposez d'un profil Manager, vous avez accès à des fonctionnalités étendues pour la gestion de vos propres réservations et l'analyse de l'utilisation du parking.

### Réservations Étendues
Contrairement aux employés, les managers bénéficient d'une dérogation concernant la durée :
*   Vous êtes autorisé à réserver une place pour une durée pouvant aller jusqu'à **30 jours calendaires** (un mois complet).
*   Les autres règles (check-in obligatoire, places électriques A et F) s'appliquent de la même manière.

### Le Tableau de Bord (Dashboard)
Vous accédez à un onglet supplémentaire nommé "Manager Dashboard". Celui-ci vous fournit des indicateurs clés en temps réel pour analyser l'efficacité du parking :
*   **Taux d'occupation :** Le pourcentage de places actuellement réservées par rapport à la capacité totale (60 places).
*   **Places Libres :** Le nombre exact de places encore disponibles à l'instant T.
*   **Les "No-shows" :** Le nombre de collaborateurs ayant réservé une place mais n'ayant pas effectué leur check-in avant 11h (ces places ont donc été remises à disposition).
*   **Utilisation Électrique :** La proportion de bornes de recharge (rangées A et F) actuellement occupées.

---

## ⚙️ 3. Profil Secrétaire (Administration)

Le profil Secrétaire dispose des droits d'administration les plus élevés. En tant que secrétaire, vous êtes en charge du support utilisateur et de la gestion de l'application.

Vous avez accès à l'onglet "Admin Panel" qui contient les outils suivants :

### Administration des Réservations
*   **Vue globale :** Vous voyez la liste complète de **toutes** les réservations en cours et passées de tous les collaborateurs.
*   **Annulation forcée :** Si un collaborateur se trompe ou a un problème technique, vous avez le pouvoir, depuis le tableau, d'**annuler n'importe quelle réservation**. Cela libère la place immédiatement.
*   **Vérification du Check-in :** Vous pouvez voir en un coup d'œil qui a bien validé sa présence aujourd'hui et qui ne l'a pas fait.

### Gestion des Utilisateurs (CRUD)
Pour ne plus utiliser le fichier Excel, l'application intègre un annuaire des utilisateurs.
*   **Ajouter un Utilisateur :** Vous pouvez créer manuellement de nouveaux comptes pour les nouveaux arrivants en complétant leur Nom, Prénom, Email et Rôle initial.
*   **Modifier un Utilisateur :** Un problème sur un nom ou un changement d'adresse mail ? Vous pouvez éditer leurs informations.
*   **Gérer les Rôles :** Vous avez le pouvoir de promouvoir un employé au statut de "MANAGER" afin qu'il puisse réserver sur 30 jours, ou de donner les droits "SECRETAIRE" à un collègue.
*   **Supprimer un Utilisateur :** Lorsqu'un collaborateur quitte l'entreprise, vous pouvez supprimer son compte depuis ce panneau d'administration.

---

*Ce manuel est conçu pour évoluer. Si vous rencontrez une difficulté non listée ici, veuillez vous adresser au service de secrétariat en charge de la gestion du parking.*
