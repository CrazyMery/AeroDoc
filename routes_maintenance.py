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

maintenance_bp = Blueprint(
    "maintenance",
    __name__,
    url_prefix="/api/maintenance"
)

# =====================================================
# LISTE
# =====================================================

@maintenance_bp.route("/")
@login_required
def list_maintenance():

    rows = fetch_all("""

        SELECT

            m.*,

            e.nom,
            e.prenom,
            e.matricule,

            c.nom_societe

        FROM maintenances m

        LEFT JOIN employes e
            ON e.id_employe=m.id_employe

        LEFT JOIN clients c
            ON c.id_client=m.id_client

        ORDER BY
            m.date_intervention DESC

    """)

    return jsonify(rows)


# =====================================================
# DETAIL
# =====================================================

@maintenance_bp.route("/<int:id_maintenance>")
@login_required
def get_maintenance(id_maintenance):

    row = fetch_one("""

        SELECT

            m.*,

            e.nom,
            e.prenom,

            c.nom_societe

        FROM maintenances m

        LEFT JOIN employes e
            ON e.id_employe=m.id_employe

        LEFT JOIN clients c
            ON c.id_client=m.id_client

        WHERE m.id_maintenance=%s

    """, (id_maintenance,))

    if not row:

        return jsonify({
            "error":
            "Maintenance introuvable"
        }),404

    return jsonify(row)


# =====================================================
# RECHERCHE
# =====================================================

@maintenance_bp.route("/search")
@login_required
def search_maintenance():

    q = request.args.get("q","")

    rows = fetch_all("""

        SELECT *

        FROM maintenances

        WHERE

            reference_fiche LIKE %s

            OR immatriculation LIKE %s

            OR type_aeronef LIKE %s

            OR type_maintenance LIKE %s

        ORDER BY
            date_intervention DESC

    """, (

        f"%{q}%",

        f"%{q}%",

        f"%{q}%",

        f"%{q}%"

    ))

    return jsonify(rows)


# =====================================================
# AJOUT
# =====================================================

@maintenance_bp.route("/add", methods=["POST"])
@editor_required
def add_maintenance():

    data = (
        request.json
        if request.is_json
        else request.form
    )

    maintenance_id = execute("""

        INSERT INTO maintenances
        (

            id_employe,
            id_client,

            reference_fiche,

            type_aeronef,
            immatriculation,

            type_maintenance,

            description,

            date_intervention,

            duree_heures,

            statut,

            id_document

        )

        VALUES
        (
            %s,%s,
            %s,
            %s,%s,
            %s,
            %s,
            %s,
            %s,
            %s,
            %s
        )

    """, (

        data.get("id_employe") or None,

        data.get("id_client") or None,

        data.get("reference_fiche"),

        data.get("type_aeronef"),

        data.get("immatriculation"),

        data.get("type_maintenance"),

        data.get("description"),

        data.get("date_intervention") or None,

        data.get("duree_heures") or None,

        data.get(
            "statut",
            "PLANIFIEE"
        ),

        data.get("id_document") or None

    ))

    # création agenda

    try:

        execute("""

            INSERT INTO agenda_evenements
            (
                titre,
                categorie,
                date_debut,
                statut,
                type_maintenance
            )

            VALUES
            (
                %s,
                'MAINTENANCE',
                %s,
                'PLANIFIE',
                %s
            )

        """, (

            f"Maintenance {data.get('immatriculation')}",

            data.get("date_intervention"),

            data.get("type_maintenance")

        ))

    except:
        pass

    log_action(
        "Création maintenance",
        "maintenance",
        f"id_maintenance={maintenance_id}"
    )

    return jsonify({

        "success":True,

        "id_maintenance":
            maintenance_id

    })


# =====================================================
# MODIFICATION
# =====================================================

@maintenance_bp.route(
    "/edit/<int:id_maintenance>",
    methods=["POST"]
)
@editor_required
def edit_maintenance(id_maintenance):

    data = (
        request.json
        if request.is_json
        else request.form
    )

    execute("""

        UPDATE maintenances

        SET

            id_employe=%s,

            id_client=%s,

            reference_fiche=%s,

            type_aeronef=%s,

            immatriculation=%s,

            type_maintenance=%s,

            description=%s,

            date_intervention=%s,

            duree_heures=%s,

            statut=%s,

            id_document=%s

        WHERE
            id_maintenance=%s

    """, (

        data.get("id_employe") or None,

        data.get("id_client") or None,

        data.get("reference_fiche"),

        data.get("type_aeronef"),

        data.get("immatriculation"),

        data.get("type_maintenance"),

        data.get("description"),

        data.get("date_intervention") or None,

        data.get("duree_heures") or None,

        data.get("statut"),

        data.get("id_document") or None,

        id_maintenance

    ))

    log_action(
        "Modification maintenance",
        "maintenance",
        f"id_maintenance={id_maintenance}"
    )

    return jsonify({
        "success":True
    })


# =====================================================
# CHANGER STATUT
# =====================================================

@maintenance_bp.route(
    "/status/<int:id_maintenance>",
    methods=["POST"]
)
@editor_required
def update_status(id_maintenance):

    data = (
        request.json
        if request.is_json
        else request.form
    )

    execute("""

        UPDATE maintenances

        SET statut=%s

        WHERE id_maintenance=%s

    """, (

        data.get("statut"),

        id_maintenance

    ))

    return jsonify({
        "success":True
    })


# =====================================================
# SUPPRESSION
# =====================================================

@maintenance_bp.route(
    "/delete/<int:id_maintenance>",
    methods=["POST","DELETE"]
)
@admin_required
def delete_maintenance(id_maintenance):

    execute("""

        DELETE FROM maintenances

        WHERE id_maintenance=%s

    """, (id_maintenance,))

    log_action(
        "Suppression maintenance",
        "maintenance",
        f"id_maintenance={id_maintenance}"
    )

    return jsonify({
        "success":True
    })


# =====================================================
# HISTORIQUE AVION
# =====================================================

@maintenance_bp.route(
    "/aircraft/<string:immat>"
)
@login_required
def aircraft_history(immat):

    rows = fetch_all("""

        SELECT *

        FROM maintenances

        WHERE immatriculation=%s

        ORDER BY date_intervention DESC

    """, (immat,))

    return jsonify(rows)


# =====================================================
# HISTORIQUE CLIENT
# =====================================================

@maintenance_bp.route(
    "/client/<int:id_client>"
)
@login_required
def client_history(id_client):

    rows = fetch_all("""

        SELECT *

        FROM maintenances

        WHERE id_client=%s

        ORDER BY date_intervention DESC

    """, (id_client,))

    return jsonify(rows)


# =====================================================
# HISTORIQUE TECHNICIEN
# =====================================================

@maintenance_bp.route(
    "/employee/<int:id_employe>"
)
@login_required
def employee_history(id_employe):

    rows = fetch_all("""

        SELECT *

        FROM maintenances

        WHERE id_employe=%s

        ORDER BY date_intervention DESC

    """, (id_employe,))

    return jsonify(rows)


# =====================================================
# AJOUT PIECE
# =====================================================

@maintenance_bp.route(
    "/piece/add",
    methods=["POST"]
)
@editor_required
def add_piece_to_maintenance():

    data = (
        request.json
        if request.is_json
        else request.form
    )

    execute("""

        INSERT INTO maintenance_pieces
        (
            id_maintenance,
            id_piece,
            quantite
        )

        VALUES
        (%s,%s,%s)

    """, (

        data.get("id_maintenance"),

        data.get("id_piece"),

        data.get("quantite")

    ))

    execute("""

        UPDATE pieces

        SET quantite_stock=
            quantite_stock-%s

        WHERE id_piece=%s

    """, (

        data.get("quantite"),

        data.get("id_piece")

    ))

    return jsonify({
        "success":True
    })


# =====================================================
# STATISTIQUES
# =====================================================

@maintenance_bp.route("/stats")
@login_required
def maintenance_stats():

    by_aircraft = fetch_all("""

        SELECT

            type_aeronef,

            COUNT(*) total

        FROM maintenances

        GROUP BY type_aeronef

        ORDER BY total DESC

    """)

    by_employee = fetch_all("""

        SELECT

            e.nom,
            e.prenom,

            COUNT(
                m.id_maintenance
            ) total

        FROM maintenances m

        JOIN employes e
            ON e.id_employe=m.id_employe

        GROUP BY e.id_employe

        ORDER BY total DESC

        LIMIT 10

    """)

    return jsonify({

        "by_aircraft":
            by_aircraft,

        "by_employee":
            by_employee

    })