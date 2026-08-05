AeroDoc Backend V2

Fichiers inclus :
- app.py
- utils.py
- routes_auth.py
- routes_users.py
- routes_employees.py
- routes_documents.py
- routes_clients.py
- routes_stock.py
- routes_maintenance.py
- routes_ocr.py
- routes_signatures.py
- routes_dashboard.py
- templates/login.html

Installation :
1. Importer le nouveau aerodoc.sql dans phpMyAdmin.
2. Placer ces fichiers dans le dossier Flask.
3. Installer requirements.txt.
4. Lancer : python app.py

Important :
- Ce backend utilise MySQL, pas aerodoc.db.
- Les routes sont en API JSON pour faciliter l'intégration avec index.html.
- Le fichier index.html doit ensuite être adapté pour appeler ces routes.
