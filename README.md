# Granulo pour Home Assistant

![Logo Granulo](https://raw.githubusercontent.com/KauBryy/granulo-home-assistant/main/images/logo.png) <!-- N'hésite pas à ajouter un logo ici plus tard -->

Bienvenue sur l'intégration officielle **Granulo** pour Home Assistant !

Cette intégration fait le lien entre votre application mobile **Granulo** (qui vous aide à gérer votre stock de granulés de bois et l'entretien de votre poêle) et votre domotique locale.

## 🌟 Fonctionnalités

Une fois configurée, l'application mobile poussera instantanément (Push) les données vers Home Assistant à chaque modification. Vous obtiendrez 13 capteurs automatiquement :

*   **📦 Stock :** Nombre de sacs restants.
*   **⏳ Autonomie :** Estimation du nombre de jours restants.
*   **🧹 Entretien :** Nombre de sacs brûlés depuis le dernier nettoyage de la vitre ou l'entretien complet.
*   **❄️ Saison :** Statistiques des achats, brûlages et dépenses pour la saison en cours.
*   **📈 Global :** Historique total des achats, brûlages et dépenses.
*   **📊 Moyennes :** Consommation moyenne sur 7 jours, sur le mois et sur la saison.

## 🛠 Installation

### Étape 1 : Installation via HACS (Recommandé)
1. Ouvrez HACS dans Home Assistant.
2. Allez dans **Intégrations**.
3. Cliquez sur les 3 petits points en haut à droite > **Dépôts personnalisés**.
4. Ajoutez l'URL de ce dépôt (`https://github.com/KauBryy/granulo-home-assistant`) et choisissez la catégorie **Intégration**.
5. Cherchez "Granulo" et installez-la.
6. Redémarrez Home Assistant.

### Étape 2 : Configuration
1. Dans Home Assistant, allez dans **Paramètres** > **Appareils et services**.
2. Cliquez sur **Ajouter une intégration** en bas à droite.
3. Cherchez **Granulo** et suivez les instructions à l'écran.

### Étape 3 : Lien avec l'application mobile
1. Ouvrez votre application Granulo.
2. Allez dans les paramètres Home Assistant.
3. Connectez-vous avec vos identifiants Home Assistant (ou collez votre Long-Lived Access Token).
4. Profitez de vos données en temps réel !

---
*Développé avec amour pour la communauté Granulo.*
