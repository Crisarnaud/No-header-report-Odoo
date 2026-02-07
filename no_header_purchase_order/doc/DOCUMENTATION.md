# Module : No Header Purchase Order

> **Nom technique** : `no_header_purchase_order`
> **Version** : 15.0
> **Catégorie** : Comptabilité (Accounting)
> **Auteur** : VEONE
> **Licence** : LGPL-3

---

## Description

Ce module permet de générer des **bons de commande fournisseur au format PDF sans en-tête ni pied de page**. Il est utile lorsque l'entreprise imprime ses documents sur du papier pré-imprimé contenant déjà l'en-tête de la société, ou lorsqu'on souhaite simplement obtenir un document épuré.

---

## Dépendances

| Module   | Description                          |
|----------|--------------------------------------|
| `base`   | Module de base Odoo                  |
| `web`    | Gestion des rapports et layouts web  |
| `purchase` | Module Achats (commandes fournisseur) |

---

## Fonctionnalités

### 1. Nouveau rapport PDF : "Commande fournisseur sans en-tête"

Le module ajoute une **action de rapport** accessible depuis le menu **Imprimer** de toute commande fournisseur (`purchase.order`). Ce rapport génère un PDF identique au rapport standard de commande fournisseur, mais **sans l'en-tête ni le pied de page** de la société.

**Accès :** Achats > Commandes > (sélectionner une commande) > Imprimer > *Commande fournisseur sans entête*

### 2. Mécanisme de contrôle des en-têtes (variable `entete`)

Le module surcharge les templates de layout standard d'Odoo (`web.external_layout_*`) en introduisant une variable de contrôle `entete` :

- **`entete != False`** (par défaut) : le rapport affiche normalement l'en-tête et le pied de page de la société.
- **`entete == False`** : l'en-tête et le pied de page sont masqués, et des sauts de ligne sont ajoutés dans le bloc d'adresse pour compenser l'espace libéré.

### 3. Layouts supportés

Les quatre layouts standards d'Odoo sont surchargés pour respecter la variable `entete` :

| Layout | Template ID | Éléments conditionnels |
|--------|-------------|----------------------|
| **Standard** | `web.external_layout_standard` | En-tête (logo, slogan, séparateur, adresse société) + Pied de page |
| **Boxed** | `web.external_layout_boxed` | En-tête (logo, slogan, détails société) + Pied de page |
| **Striped** | `web.external_layout_striped` | En-tête (logo, slogan, adresse société) + Pied de page |
| **Bold** | `web.external_layout_bold` | En-tête (logo, nom, TVA, téléphone, email, site web) + Pied de page |

Quel que soit le layout configuré pour la société, le rapport sans en-tête fonctionnera correctement.

---

## Architecture technique

### Structure des fichiers

```
no_header_purchase_order/
├── __init__.py                  # Import du package models
├── __manifest__.py              # Métadonnées du module
├── models/
│   ├── __init__.py              # Import du modèle purchase_order
│   └── purchase_order.py        # Héritage du modèle purchase.order
└── report/
    └── report_menu.xml          # Templates QWeb et action de rapport
```

### Modèle Python

| Modèle | Type | Description |
|--------|------|-------------|
| `purchase.order` | `_inherit` | Extension du modèle commande fournisseur (réservé pour extensions futures) |

### Templates QWeb

| Template ID | Type | Description |
|-------------|------|-------------|
| `web.external_layout` | Surcharge | Résolution de la société et routage vers le layout approprié |
| `web.address_layout` | Surcharge | Ajout de la logique conditionnelle `entete` pour l'espacement |
| `web.external_layout_boxed` | Surcharge | Masquage conditionnel de l'en-tête/pied de page (layout Boxed) |
| `web.external_layout_striped` | Surcharge | Masquage conditionnel de l'en-tête/pied de page (layout Striped) |
| `web.external_layout_bold` | Surcharge | Masquage conditionnel de l'en-tête/pied de page (layout Bold) |
| `web.external_layout_standard` | Surcharge | Masquage conditionnel de l'en-tête/pied de page (layout Standard) |
| `report_purchasequotation_without_header` | Nouveau | Template du rapport sans en-tête |

### Action de rapport

| Champ | Valeur |
|-------|--------|
| **ID XML** | `action_report_purchase_order` |
| **Nom** | Commande fournisseur sans entête |
| **Modèle** | `purchase.order` |
| **Type** | `qweb-pdf` |
| **Nom du rapport** | `no_header_purchase_order.report_purchasequotation_without_header` |
| **Liaison** | Rapport lié au modèle `purchase.order` (menu Imprimer) |

---

## Fonctionnement détaillé

### Flux d'exécution du rapport

```
1. L'utilisateur clique sur "Imprimer" > "Commande fournisseur sans entête"
         │
         ▼
2. Le template `report_purchasequotation_without_header` est appelé
   → La variable `entete` est définie à `False`
   → Le template standard `purchase.report_purchaseorder_document` est appelé
     (dans la langue du partenaire)
         │
         ▼
3. Le document appelle `web.external_layout`
   → Détermine la société courante
   → Route vers le layout configuré (standard, boxed, striped, bold)
         │
         ▼
4. Le layout vérifie `entete != False`
   → Comme `entete == False` : l'en-tête et le pied de page sont masqués
         │
         ▼
5. Le layout appelle `web.address_layout`
   → Comme `entete == False` : 4 sauts de ligne sont ajoutés pour l'espacement
         │
         ▼
6. Le contenu du document est rendu normalement
         │
         ▼
7. Le PDF est généré et téléchargé sans en-tête ni pied de page
```

### Gestion multi-société

Le module gère correctement les environnements multi-sociétés. La résolution de la société suit cet ordre de priorité :

1. Variable `company_id` si définie dans le contexte
2. Champ `company_id` de l'objet courant (`o.company_id`)
3. Variable `res_company` par défaut

---

## Impact et compatibilité

### Portée de la surcharge

Les surcharges des templates de layout (`web.external_layout_*`) s'appliquent **globalement** à tous les rapports du système. Cependant, comme la variable `entete` n'est définie à `False` que dans le template spécifique `report_purchasequotation_without_header`, les autres rapports ne sont pas impactés : la condition `entete != False` sera évaluée à `True` (car `entete` sera `undefined`/non défini, donc différent de `False`).

### Compatibilité

- **Odoo** : Version 15.0
- **Autres modules** : Compatible avec tout module utilisant les layouts standards d'Odoo. Si un autre module surcharge les mêmes templates de layout, des conflits peuvent survenir.

---

## Installation

1. Copier le dossier `no_header_purchase_order` dans le répertoire des addons Odoo
2. Mettre à jour la liste des modules : *Paramètres > Mettre à jour la liste des modules*
3. Rechercher "Gestions des headers sur la facture" et cliquer sur **Installer**

---

## Utilisation

1. Aller dans **Achats > Commandes > Bons de commande**
2. Ouvrir un bon de commande existant
3. Cliquer sur **Imprimer**
4. Sélectionner **"Commande fournisseur sans entête"**
5. Le PDF est généré sans en-tête ni pied de page de la société
