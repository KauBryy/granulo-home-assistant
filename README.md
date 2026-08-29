# Granulo pour Home Assistant

Bienvenue sur l'intégration officielle **Granulo** pour Home Assistant !

Cette intégration connecte votre compte **Granulo** (gestion de stock de granulés de bois et entretien de votre poêle) à votre domotique locale Home Assistant.

## 🌟 Fonctionnalités

* **📦 Stock en temps réel :** Nombre de sacs restants et équivalent en kg.
* **🏷️ Sélection de marque :** Choisissez vos marques de granulés configurées dans l'application lors de l'enregistrement.
* **⏳ Autonomie :** Estimation du nombre de jours restants basée sur votre historique.
* **🧹 Entretien :** Suivi des sacs brûlés depuis le dernier nettoyage de vitre et entretien régulier.
* **❄️ Saison :** Statistiques des achats, brûlages et dépenses pour la saison de chauffe en cours.
* **📈 Global :** Historique total des achats, brûlages et dépenses.
* **📊 Moyennes :** Consommation moyenne sur 7 jours, mois en cours et saison.
* **⚡ Actions rapides :** Boutons d'enregistrement direct (brûlage, achat, rafraîchissement).

---

## 🛠 Installation

### Étape 1 : Installation via HACS
1. Dans Home Assistant, ouvrez **HACS**.
2. Cliquez sur les 3 points en haut à droite > **Dépôts personnalisés**.
3. Ajoutez l'URL de ce dépôt : `https://github.com/KauBryy/granulo-home-assistant` (Catégorie : **Intégration**).
4. Cliquez sur **Télécharger** puis **redémarrez Home Assistant**.

### Étape 2 : Connecter votre compte
1. Allez dans **Paramètres** > **Appareils et services** > **Ajouter une intégration**.
2. Recherchez **Granulo**.
3. Collez votre **ID Utilisateur (UID)** (disponible dans votre application Granulo sous *Paramètres > Maison Connectée*).

---

## 📊 Configuration du Tableau de Bord (2 Méthodes)

### Option 1 : Via l'Éditeur de Configuration Brute (Vue complète)
Dans votre tableau de bord, cliquez sur les 3 points en haut à droite > **Éditeur de configuration brute** et collez :

```yaml
views:
  - title: Granulo
    path: granulo
    icon: mdi:fire
    cards:
      - type: vertical-stack
        title: 🔥 Mon Poêle à Granulés
        cards:
          - type: horizontal-stack
            cards:
              - type: gauge
                entity: sensor.granulo_poele_stock_actuel
                name: Stock restant
                unit: sacs
                min: 0
                max: 60
                needle: true
                severity:
                  red: 0
                  yellow: 5
                  green: 15
              - type: entity
                entity: sensor.granulo_poele_jours_restants
                name: Autonomie estimée
                icon: mdi:clock-outline

          - type: glance
            title: 📊 Statistiques Saison
            show_name: true
            show_state: true
            entities:
              - entity: sensor.granulo_poele_stock_kg
                name: Stock (kg)
              - entity: sensor.granulo_poele_brulages_saison
                name: Brûlés
              - entity: sensor.granulo_poele_depenses_saison
                name: Dépenses
              - entity: sensor.granulo_poele_moyenne_7j
                name: Moyenne 7j

          - type: entities
            title: 🧹 Entretien du Poêle
            entities:
              - entity: sensor.granulo_poele_vitre
                name: Nettoyage Vitre
              - entity: sensor.granulo_poele_entretien
                name: Prochain entretien

          - type: entities
            title: ⚡ Enregistrement rapide
            show_header_toggle: false
            entities:
              - entity: select.granulo_poele_marque
                name: Marque de granulés
              - entity: number.granulo_poele_quantite
                name: Quantité (sacs)
              - entity: number.granulo_poele_prix
                name: Prix unitaire (€)
              - entity: text.granulo_poele_note
                name: Note optionnelle

          - type: horizontal-stack
            cards:
              - type: button
                name: 🔥 Brûler sac(s)
                icon: mdi:fire
                tap_action:
                  action: perform-action
                  perform_action: button.press
                  target:
                    entity_id: button.granulo_poele_enregistrer_un_brulage
              - type: button
                name: 🛒 Ajouter Achat
                icon: mdi:cart-plus
                tap_action:
                  action: perform-action
                  perform_action: button.press
                  target:
                    entity_id: button.granulo_poele_enregistrer_un_achat
              - type: button
                name: 🔄 Rafraîchir
                icon: mdi:refresh
                tap_action:
                  action: perform-action
                  perform_action: button.press
                  target:
                    entity_id: button.granulo_poele_actualiser_donnees
```

### Option 2 : Ajouter une Carte Manuel dans un tableau existant
Sur votre tableau de bord > 3 points > **Modifier le tableau de bord** > **+ Ajouter une carte** > **Manuel** :

```yaml
type: vertical-stack
title: 🔥 Mon Poêle à Granulés
cards:
  - type: horizontal-stack
    cards:
      - type: gauge
        entity: sensor.granulo_poele_stock_actuel
        name: Stock restant
        unit: sacs
        min: 0
        max: 60
        needle: true
        severity:
          red: 0
          yellow: 5
          green: 15
      - type: entity
        entity: sensor.granulo_poele_jours_restants
        name: Autonomie estimée
        icon: mdi:clock-outline

  - type: glance
    title: 📊 Statistiques Saison
    show_name: true
    show_state: true
    entities:
      - entity: sensor.granulo_poele_stock_kg
        name: Stock (kg)
      - entity: sensor.granulo_poele_brulages_saison
        name: Brûlés
      - entity: sensor.granulo_poele_depenses_saison
        name: Dépenses
      - entity: sensor.granulo_poele_moyenne_7j
        name: Moyenne 7j

  - type: entities
    title: 🧹 Entretien du Poêle
    entities:
      - entity: sensor.granulo_poele_vitre
        name: Nettoyage Vitre
      - entity: sensor.granulo_poele_entretien
        name: Prochain entretien

  - type: entities
    title: ⚡ Enregistrement rapide
    show_header_toggle: false
    entities:
      - entity: select.granulo_poele_marque
        name: Marque de granulés
      - entity: number.granulo_poele_quantite
        name: Quantité (sacs)
      - entity: number.granulo_poele_prix
        name: Prix unitaire du sac (€)
      - entity: text.granulo_poele_note
        name: Note optionnelle

  - type: horizontal-stack
    cards:
      - type: button
        name: 🔥 Brûler sac(s)
        icon: mdi:fire
        tap_action:
          action: perform-action
          perform_action: button.press
          target:
            entity_id: button.granulo_poele_enregistrer_un_brulage
      - type: button
        name: 🛒 Ajouter Achat
        icon: mdi:cart-plus
        tap_action:
          action: perform-action
          perform_action: button.press
          target:
            entity_id: button.granulo_poele_enregistrer_un_achat
      - type: button
        name: 🔄 Rafraîchir
        icon: mdi:refresh
        tap_action:
          action: perform-action
          perform_action: button.press
          target:
            entity_id: button.granulo_poele_actualiser_donnees
```
