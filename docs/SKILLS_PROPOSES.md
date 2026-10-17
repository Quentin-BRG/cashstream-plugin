# Skills proposés pour CashStream

Les deux skills distribués sont `cashstream` et `cashstream-import-statement`.
Les six workflows ci-dessous sont des propositions, pas des skills activés.

Le fil conducteur : savoir ce qu'il reste réellement à dépenser, anticiper les
prochaines semaines et faire avancer ses objectifs. Chaque skill doit avoir
un résultat distinct et s'appuyer sur les outils MCP disponibles.

| Priorité | Skill proposé | Résultat attendu | Exemple de demande |
| --- | --- | --- | --- |
| 1 | `cashstream-budget-review` | Faire le point sur les soldes et enveloppes, les opérations non affectées et les prochaines échéances. | « Où j'en suis cette semaine, et que dois-je vérifier ? » |
| 1 | `cashstream-recurring-flows` | Créer ou ajuster abonnements, factures, revenus, virements et remboursements ; vérifier les paiements liés. | « Ajoute mon loyer et vérifie mes abonnements. » |
| 1 | `cashstream-envelope-planning` | Construire ou ajuster les enveloppes de dépenses et d'épargne à partir des priorités de l'utilisateur. | « Organise mes enveloppes pour le mois prochain. » |
| 2 | `cashstream-onboarding` | Guider les premiers comptes, les opérations fournies, les flux récurrents et une première enveloppe. | « Aide-moi à démarrer avec CashStream. » |
| 2 | `cashstream-cashflow-forecast` | Estimer la trésorerie sur un horizon demandé et signaler les creux possibles avec des hypothèses explicites. | « Est-ce que mon compte passe les six prochaines semaines ? » |
| 2 | `cashstream-monthly-review` | Produire un bilan mensuel des flux réalisés, écarts et points à corriger, avec les transferts traités séparément. | « Fais le bilan de septembre. » |

## Périmètres et outils

### Point budget — `cashstream-budget-review`

- Lecture : `search_accounts`, `search_transactions`, `search_envelopes`,
  recherches des objets récurrents et `list_flow_occurrences`.
- Sortie : une vue datée, les exceptions utiles et quelques actions proposées.
- Ne pas présenter la somme des soldes comme un reste à dépenser. Distinguer
  argent disponible, argent affecté et échéances à venir, sans double comptage.
- Lecture seule par défaut. Pas de rappel récurrent créé sans demande.

### Flux récurrents — `cashstream-recurring-flows`

- Utiliser les outils métier `search/create/update/archive` de `subscription`,
  `bill`, `income_plan`, `transfer_plan` et `repayment_plan`.
- Lire les échéances avec `list_flow_occurrences`. Lier un paiement réel via
  `add_transactions` ou `update_transaction`, avec sa date d'occurrence.
- Distinguer le calendrier prévu des transactions réalisées. Archiver un
  abonnement dans CashStream ne résilie pas le contrat auprès du fournisseur.

### Enveloppes — `cashstream-envelope-planning`

- Lire `search_accounts`, `search_envelopes` et les engagements utiles.
- Utiliser `create_envelope`, `update_envelope`, `allocate_to_envelope` pour
  appliquer les choix demandés.
- Distinguer budget de dépenses et objectif d'épargne. Vérifier ce que les
  données permettent d'affecter, sans créer de transaction pour une allocation.
- Rester dans les priorités de l'utilisateur ; présenter un arbitrage concret
  si plusieurs répartitions sont possibles.

### Prise en main — `cashstream-onboarding`

- Guider un état initial réel : comptes avec leurs soldes et devises, opérations
  fournies, récurrents, puis première enveloppe ou objectif.
- Ne pas promettre de connexion bancaire automatique ni inventer des dépenses
  de démonstration dans un vrai espace.
- Compléter le skill général par un parcours guidé ; ne pas créer un second
  catalogue de toutes les opérations CRUD.

### Prévision — `cashstream-cashflow-forecast`

- Lire soldes, transactions et échéances nécessaires sur l'horizon demandé.
- Le MCP ne fournit pas d'outil de prévision globale dédié : le calcul doit
  être dérivé des données disponibles, avec couverture et hypothèses annoncées.
- Prendre en compte les paiements déjà réalisés sans compter deux fois une
  échéance. Séparer devises, simulations et mouvements internes.
- Présenter une estimation ; ne pas inscrire automatiquement les montants
  prévus comme des opérations réalisées.

### Bilan mensuel — `cashstream-monthly-review`

- Lire l'ensemble des pages de transactions sur la période et les comptes
  concernés. Déclarer les données manquantes et leur effet sur le bilan.
- Séparer revenus, dépenses, virements internes et simulations ; conserver les
  remboursements et ventilations dans le calcul approprié.
- Proposer les corrections de données détectées. Un bilan n'autorise pas à
  modifier les écritures ni à clôturer automatiquement une période.

## Ordre recommandé

1. Garder l'import de relevés comme premier moyen de mise à jour.
2. Ajouter le point budget pour installer un usage hebdomadaire utile.
3. Ajouter les flux récurrents, puis la planification des enveloppes.
4. Ajouter la prise en main si le parcours dans l'application en a besoin.
5. Valider les calculs et la couverture avant de distribuer les prévisions
   et les bilans mensuels.

Les révisions doivent respecter les autorisations déjà données : exécuter les
changements clairement demandés, demander seulement les choix manquants qui
modifient le résultat, et vérifier les écritures incertaines avant une reprise.
