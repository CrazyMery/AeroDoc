from flask import Flask, render_template, jsonify, request, redirect, url_for
import mysql.connector
from datetime import date, datetime
from dateutil.relativedelta import relativedelta

app = Flask(__name__)


# ==========================
# CONNEXION MYSQL
# ==========================

def get_db():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="aerodoc"
    )


# ==========================
# OUTILS
# ==========================

def parse_date(value):
    if not value:
        return None
    if isinstance(value, date):
        return value
    return datetime.strptime(str(value), "%Y-%m-%d").date()


def compute_status(expiration_date):
    if not expiration_date:
        return "sans_expiration"

    today = date.today()
    jours = (expiration_date - today).days

    if jours < 0:
        return "expire"
    elif jours <= 30:
        return "expire_bientot"
    elif jours <= 60:
        return "a_renouveler"
    else:
        return "valide"


def status_label(status):
    return {
        "valide": "Valide",
        "a_renouveler": "À renouveler",
        "expire_bientot": "Expiration proche",
        "expire": "Expiré",
        "sans_expiration": "Sans expiration"
    }.get(status, status)


def status_class(status):
    return {
        "valide": "valid",
        "a_renouveler": "renew",
        "expire_bientot": "warn",
        "expire": "expired",
        "sans_expiration": "neutral"
    }.get(status, "neutral")


def sql_statut(status):
    if status == "expire":
        return "EXPIRE"
    elif status in ["a_renouveler", "expire_bientot"]:
        return "A_RENOUVELER"
    else:
        return "VALIDE"


def alert_level(status):
    if status == "expire":
        return "CRITIQUE"
    elif status == "expire_bientot":
        return "ATTENTION"
    elif status == "a_renouveler":
        return "INFO"
    return "INFO"


# ==========================
# EMPLOYES
# ==========================

def get_employees():
    conn = get_db()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT e.*,
               COUNT(d.id) AS document_count
        FROM employes e
        LEFT JOIN documents d ON d.employe_id = e.id
        GROUP BY e.id
        ORDER BY e.nom, e.prenom
    """)

    employees = cursor.fetchall()

    cursor.close()
    conn.close()

    return employees


# ==========================
# DOCUMENTS
# ==========================

def get_documents():
    conn = get_db()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT d.id,
               d.employe_id,
               d.type_document,
               d.nom_fichier,
               d.chemin_fichier,
               d.date_import AS date_depot,
               d.date_expiration,
               d.statut,
               e.nom,
               e.prenom,
               e.matricule
        FROM documents d
        JOIN employes e ON e.id = d.employe_id
        ORDER BY d.date_expiration ASC
    """)

    rows = cursor.fetchall()

    cursor.close()
    conn.close()

    documents = []

    for row in rows:
        exp = parse_date(row["date_expiration"])
        status = compute_status(exp)

        row["status"] = status
        row["status_label"] = status_label(status)
        row["status_class"] = status_class(status)
        row["jours_restants"] = (exp - date.today()).days if exp else 9999

        documents.append(row)

    return documents


# ==========================
# ALERTES AUTO
# ==========================

def generate_alerts():
    conn = get_db()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT d.id,
               d.employe_id,
               d.type_document,
               d.date_expiration
        FROM documents d
        WHERE d.date_expiration IS NOT NULL
    """)

    documents = cursor.fetchall()

    for doc in documents:
        exp = parse_date(doc["date_expiration"])
        status = compute_status(exp)

        if status in ["a_renouveler", "expire_bientot", "expire"]:
            niveau = alert_level(status)

            cursor.execute("""
                SELECT id
                FROM alertes
                WHERE employe_id = %s
                AND type_document = %s
                AND date_expiration = %s
                AND statut = 'OUVERTE'
            """, (
                doc["employe_id"],
                doc["type_document"],
                doc["date_expiration"]
            ))

            existing = cursor.fetchone()

            if not existing:
                cursor.execute("""
                    INSERT INTO alertes
                    (
                        employe_id,
                        type_document,
                        date_expiration,
                        niveau,
                        statut
                    )
                    VALUES (%s, %s, %s, %s, 'OUVERTE')
                """, (
                    doc["employe_id"],
                    doc["type_document"],
                    doc["date_expiration"],
                    niveau
                ))

            cursor.execute("""
                UPDATE documents
                SET statut = %s
                WHERE id = %s
            """, (
                sql_statut(status),
                doc["id"]
            ))

    conn.commit()
    cursor.close()
    conn.close()


def get_alerts():
    generate_alerts()

    conn = get_db()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT a.*,
               e.nom,
               e.prenom,
               e.matricule
        FROM alertes a
        JOIN employes e ON e.id = a.employe_id
        WHERE a.statut = 'OUVERTE'
        ORDER BY a.date_expiration ASC
    """)

    rows = cursor.fetchall()

    cursor.close()
    conn.close()

    alerts = []

    for row in rows:
        exp = parse_date(row["date_expiration"])
        status = compute_status(exp)

        row["status"] = status
        row["status_label"] = status_label(status)
        row["status_class"] = status_class(status)
        row["jours_restants"] = (exp - date.today()).days if exp else 9999

        alerts.append(row)

    return alerts


# ==========================
# DASHBOARD
# ==========================

def get_dashboard():
    employees = get_employees()
    documents = get_documents()
    alerts = get_alerts()

    valid_documents = sum(1 for d in documents if d["status"] == "valide")
    renew_documents = sum(1 for d in documents if d["status"] in ["a_renouveler", "expire_bientot"])
    expired_documents = sum(1 for d in documents if d["status"] == "expire")

    conn = get_db()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT q.nom_qualification,
               COUNT(eq.id) AS total
        FROM qualifications q
        LEFT JOIN employe_qualifications eq
        ON eq.qualification_id = q.id
        GROUP BY q.id, q.nom_qualification
    """)

    aircraft_counts = {}

    for row in cursor.fetchall():
        aircraft_counts[row["nom_qualification"]] = row["total"]

    cursor.close()
    conn.close()

    return {
        "total_employees": len(employees),
        "total_documents": len(documents),
        "valid_documents": valid_documents,
        "renew_documents": renew_documents,
        "expired_documents": expired_documents,
        "missing_documents": 0,
        "active_alerts": len(alerts),
        "aircraft_counts": aircraft_counts
    }


# ==========================
# ROUTES
# ==========================

@app.route("/")
def index():
    return render_template(
        "index.html",
        dashboard=get_dashboard(),
        employees=get_employees(),
        documents=get_documents(),
        alerts=get_alerts(),
        today=date.today()
    )


@app.route("/documents/add", methods=["POST"])
def add_document():
    employe_id = request.form.get("employee_id")
    type_document = request.form.get("type_document")
    nom_fichier = request.form.get("nom_fichier")
    date_expiration = request.form.get("date_expiration")

    if not employe_id or not type_document or not nom_fichier:
        return redirect(url_for("index"))

    exp = parse_date(date_expiration)
    status = compute_status(exp)
    statut_sql = sql_statut(status)

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO documents
        (
            employe_id,
            type_document,
            nom_fichier,
            chemin_fichier,
            date_expiration,
            statut
        )
        VALUES (%s, %s, %s, %s, %s, %s)
    """, (
        employe_id,
        type_document,
        nom_fichier,
        "uploads/" + nom_fichier,
        date_expiration if date_expiration else None,
        statut_sql
    ))

    conn.commit()
    cursor.close()
    conn.close()

    generate_alerts()

    return redirect(url_for("index"))


@app.route("/alertes/traiter/<int:alerte_id>")
def traiter_alerte(alerte_id):
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE alertes
        SET statut = 'TRAITEE',
            date_resolution = NOW()
        WHERE id = %s
    """, (alerte_id,))

    conn.commit()
    cursor.close()
    conn.close()

    return redirect(url_for("index"))


# ==========================
# API JSON
# ==========================

@app.route("/api/dashboard")
def api_dashboard():
    return jsonify(get_dashboard())


@app.route("/api/employees")
def api_employees():
    return jsonify(get_employees())


@app.route("/api/documents")
def api_documents():
    return jsonify(get_documents())


@app.route("/api/alerts")
def api_alerts():
    return jsonify(get_alerts())


# ==========================
# LANCEMENT
# ==========================

if __name__ == "__main__":
    app.run(debug=True)