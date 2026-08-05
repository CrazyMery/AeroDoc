from flask import Blueprint, request, jsonify

from utils import (
    fetch_all,
    fetch_one,
    execute,
    login_required,
    editor_required,
    admin_required,
    log_action
)

employees_bp = Blueprint(
    "employees",
    __name__,
    url_prefix="/api/employees"
)

# =====================================================
# LISTE EMPLOYES
# =====================================================

@employees_bp.route("/")
@login_required
def list_employees():

    rows = fetch_all("""

        SELECT
            e.*,
            COUNT(d.id_document) AS document_count

        FROM employes e

        LEFT JOIN documents d
            ON d.id_employe = e.id_employe

        GROUP BY e.id_employe

        ORDER BY e.nom,e.prenom

    """)

    return jsonify(rows)


# =====================================================
# RECHERCHE
# =====================================================

@employees_bp.route("/search")
@login_required
def search_employees():

    q = request.args.get("q","")

    rows = fetch_all("""

        SELECT *

        FROM employes

        WHERE

            nom LIKE %s

            OR prenom LIKE %s

            OR matricule LIKE %s

            OR fonction LIKE %s

        ORDER BY nom

    """,(

        f"%{q}%",
        f"%{q}%",
        f"%{q}%",
        f"%{q}%"

    ))

    return jsonify(rows)


# =====================================================
# DETAIL EMPLOYE
# =====================================================

@employees_bp.route("/<int:id_employe>")
@login_required
def get_employee(id_employe):

    employee = fetch_one("""

        SELECT *

        FROM employes

        WHERE id_employe=%s

    """,(id_employe,))

    if not employee:

        return jsonify({
            "error":"Employé introuvable"
        }),404

    documents = fetch_all("""

        SELECT *

        FROM documents

        WHERE id_employe=%s

        ORDER BY date_import DESC

    """,(id_employe,))

    qualifications = fetch_all("""

        SELECT *

        FROM qualifications

        WHERE id_employe=%s

    """,(id_employe,))

    formations = fetch_all("""

        SELECT *

        FROM formations

        WHERE id_employe=%s

    """,(id_employe,))

    return jsonify({

        "employe":employee,

        "documents":documents,

        "qualifications":qualifications,

        "formations":formations

    })


# =====================================================
# AJOUT EMPLOYE
# =====================================================

@employees_bp.route(
    "/add",
    methods=["POST"]
)
@editor_required
def add_employee():

    data = (
        request.json
        if request.is_json
        else request.form
    )

    employee_id = execute("""

        INSERT INTO employes
        (

            matricule,

            nom,
            prenom,

            fonction,

            date_naissance,

            nationalite,

            adresse,

            telephone,

            email,

            date_embauche,

            statut

        )

        VALUES
        (
            %s,%s,%s,%s,
            %s,%s,%s,%s,
            %s,%s,%s
        )

    """,(

        data.get("matricule"),

        data.get("nom"),
        data.get("prenom"),

        data.get("fonction"),

        data.get("date_naissance"),

        data.get("nationalite"),

        data.get("adresse"),

        data.get("telephone"),

        data.get("email"),

        data.get("date_embauche"),

        data.get("statut","ACTIF")

    ))

    log_action(
        "Création employé",
        "employees",
        f"id_employe={employee_id}"
    )

    return jsonify({

        "success":True,

        "id_employe":employee_id

    })


# =====================================================
# MODIFICATION EMPLOYE
# =====================================================

@employees_bp.route(
    "/edit/<int:id_employe>",
    methods=["POST"]
)
@editor_required
def edit_employee(id_employe):

    data = (
        request.json
        if request.is_json
        else request.form
    )

    execute("""

        UPDATE employes

        SET

            matricule=%s,

            nom=%s,

            prenom=%s,

            fonction=%s,

            date_naissance=%s,

            nationalite=%s,

            adresse=%s,

            telephone=%s,

            email=%s,

            date_embauche=%s,

            statut=%s

        WHERE id_employe=%s

    """,(

        data.get("matricule"),

        data.get("nom"),

        data.get("prenom"),

        data.get("fonction"),

        data.get("date_naissance"),

        data.get("nationalite"),

        data.get("adresse"),

        data.get("telephone"),

        data.get("email"),

        data.get("date_embauche"),

        data.get("statut"),

        id_employe

    ))

    log_action(
        "Modification employé",
        "employees",
        f"id_employe={id_employe}"
    )

    return jsonify({
        "success":True
    })


# =====================================================
# SUPPRESSION
# =====================================================

@employees_bp.route(
    "/delete/<int:id_employe>",
    methods=["POST","DELETE"]
)
@admin_required
def delete_employee(id_employe):

    execute("""

        DELETE

        FROM employes

        WHERE id_employe=%s

    """,(id_employe,))

    log_action(
        "Suppression employé",
        "employees",
        f"id_employe={id_employe}"
    )

    return jsonify({
        "success":True
    })


# =====================================================
# STATISTIQUES
# =====================================================

@employees_bp.route("/stats")
@login_required
def employee_stats():

    total = fetch_one("""

        SELECT COUNT(*) total

        FROM employes

    """)["total"]

    actifs = fetch_one("""

        SELECT COUNT(*) total

        FROM employes

        WHERE statut='ACTIF'

    """)["total"]

    return jsonify({

        "total":total,

        "actifs":actifs

    })