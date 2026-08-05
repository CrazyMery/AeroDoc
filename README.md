# AeroDoc Python

Version Python/Flask de l'application AeroDoc.

## Installation

```bash
pip install -r requirements.txt
python app.py
```

Ouvrir ensuite :

```text
http://127.0.0.1:5000
```

## Règle d'alerte

Une alerte est créée si :

```text
date_expiration - 2 mois <= aujourd'hui
```

Les documents déjà expirés sont aussi affichés dans les alertes.
