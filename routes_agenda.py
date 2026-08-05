from flask import Blueprint, request, jsonify
from datetime import datetime
from utils import (
    fetch_all,
    fetch_one,
    execute,
    login_required,
    editor_required,
    admin_required,
    log_action
)

agenda_bp = Blueprint(
    "agenda",
    __name__,
    url_prefix="/api/agenda"
)


# ==========================
# OUTILS
# ==========================

def clean_value(value):
    if value == "":
        return None
    return value


def clean_int(value):
    if value in ("", None):
        return None
    try:
        return int(value)
    except ValueError:
        return None


def clean_float(value):
    if value in ("", None):
        return None
    try:
        return float(value)
    except ValueError:
        return None


def normalize_datetime(value):
    """
    Accepte :
    - 2026-06-15T09:00
    - 2026-06-15 09:00:00
    Retourne un format MySQL DATETIME.
    """
    if not value:
        return None

    value = str(value).replace("T", " ")

    if len(value) == 16:
        value += ":00"

    try:
        datetime.strptime(value, "%Y-%m-%d %H:%M:%S")
        return value
    except ValueError:
        return None


def get_event_payload(data):
    return {
        "titre": clean_value(data.get("titre")),
        "categorie": clean_value(data.get("categorie")),
        "description": clean_value(data.get("description")),
        "date_debut": normalize_datetime(data.get("date_debut")),
        "date_fin": normalize_datetime(data.get("date_fin")),
        "lieu": clean_value(data.get("lieu")),
        "statut": clean_value(data.get("statut")) or "PLANIFIE",

        "organisateur": clean_value(data.get("organisateur")),
        "id_client": clean_int(data.get("id_client")),

        "fournisseur": clean_value(data.get("fournisseur")),
        "piece": clean_value(data.get("piece")),
        "quantite": clean_int(data.get("quantite")),
        "montant": clean_float(data.get("montant")),

        "technicien": clean_value(data.get("technicien")),
        "hangar": clean_value(data.get("hangar")),
        "type_maintenance": clean_value(data.get("type_maintenance")),
    }


def validate_event(payload):
    errors = []

    if not payload["titre"]:
        errors.append("Le titre est obligatoire.")

    if not payload["categorie"]:
        errors.append("La catégorie est obligatoire.")

    if not payload["date_debut"]:
        errors.append("La date de début est obligatoire ou invalide.")

    allowed_categories = {
        "REUNION_CLIENT",
        "REUNION_ADMIN",
        "MAINTENANCE",
        "COMMANDE_MATERIEL",
        "RECEPTION_MATERIEL",
        "PAIEMENT",
        "AUDIT",
        "FORMATION",
        "LIVRAISON",
        "AUTRE"
    }

    if payload["categorie"] and payload["categorie"] not in allowed_categories:
        errors.append("Catégorie invalide.")

    allowed_status = {
        "PLANIFIE",
        "EN_COURS",
        "TERMINE",
        "ANNULE"
    }

    if payload["statut"] not in allowed_status:
        errors.append("Statut invalide.")

    if payload["date_fin"] and payload["date_debut"]:
        if payload["date_fin"] < payload["date_debut"]:
            errors.append("La date de fin doit être après la date de début.")

    return errors


# ==========================
# LISTE DES EVENEMENTS
# ==========================

@agenda_bp.route("/", methods=["GET"])
@login_required
def list_events():

    rows = fetch_all("""
        SELECT
            a.*,
            c.nom_societe
        FROM agenda_evenements a
        LEFT JOIN clients c
            ON c.id_client = a.id_client
        ORDER BY a.date_debut ASC
    """)

    return jsonify(rows)


# ==========================
# EVENEMENTS DU JOUR
# ==========================

@agenda_bp.route("/today", methods=["GET"])
@login_required
def today_events():

    rows = fetch_all("""
        SELECT
            a.*,
            c.nom_societe
        FROM agenda_evenements a
        LEFT JOIN clients c
            ON c.id_client = a.id_client
        WHERE DATE(a.date_debut) = CURDATE()
        ORDER BY a.date_debut ASC
    """)

    return jsonify(rows)


# ==========================
# EVENEMENTS PAR DATE
# Exemple : /api/agenda/day/2026-06-15
# ==========================

@agenda_bp.route("/day/<string:day>", methods=["GET"])
@login_required
def events_by_day(day):

    rows = fetch_all("""
        SELECT
            a.*,
            c.nom_societe
        FROM agenda_evenements a
        LEFT JOIN clients c
            ON c.id_client = a.id_client
        WHERE DATE(a.date_debut) = %s
        ORDER BY a.date_debut ASC
    """, (day,))

    return jsonify(rows)


# ==========================
# DETAIL EVENEMENT
# ==========================

@agenda_bp.route("/<int:id_evenement>", methods=["GET"])
@login_required
def get_event(id_evenement):

    row = fetch_one("""
        SELECT
            a.*,
            c.nom_societe
        FROM agenda_evenements a
        LEFT JOIN clients c
            ON c.id_client = a.id_client
        WHERE a.id_evenement = %s
    """, (id_evenement,))

    if not row:
        return jsonify({
            "success": False,
            "error": "Événement introuvable."
        }), 404

    return jsonify(row)


# ==========================
# AJOUT EVENEMENT
# ==========================

@agenda_bp.route("/add", methods=["POST"])
@editor_required
def add_event():

    data = request.json if request.is_json else request.form
    payload = get_event_payload(data)
    errors = validate_event(payload)

    if errors:
        return jsonify({
            "success": False,
            "errors": errors
        }), 400

    event_id = execute("""
        INSERT INTO agenda_evenements
        (
            titre,
            categorie,
            description,
            date_debut,
            date_fin,
            lieu,
            statut,
            organisateur,
            id_client,
            fournisseur,
            piece,
            quantite,
            montant,
            technicien,
            hangar,
            type_maintenance
        )
        VALUES
        (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
    """, (
        payload["titre"],
        payload["categorie"],
        payload["description"],
        payload["date_debut"],
        payload["date_fin"],
        payload["lieu"],
        payload["statut"],
        payload["organisateur"],
        payload["id_client"],
        payload["fournisseur"],
        payload["piece"],
        payload["quantite"],
        payload["montant"],
        payload["technicien"],
        payload["hangar"],
        payload["type_maintenance"]
    ))

    log_action(
        "Création événement",
        "agenda",
        f"id_evenement={event_id}"
    )

    return jsonify({
        "success": True,
        "id_evenement": event_id,
        "message": "Événement créé avec succès."
    })


# ==========================
# MODIFICATION EVENEMENT
# ==========================

@agenda_bp.route("/edit/<int:id_evenement>", methods=["POST"])
@editor_required
def edit_event(id_evenement):

    existing = fetch_one("""
        SELECT id_evenement
        FROM agenda_evenements
        WHERE id_evenement=%s
    """, (id_evenement,))

    if not existing:
        return jsonify({
            "success": False,
            "error": "Événement introuvable."
        }), 404

    data = request.json if request.is_json else request.form
    payload = get_event_payload(data)
    errors = validate_event(payload)

    if errors:
        return jsonify({
            "success": False,
            "errors": errors
        }), 400

    execute("""
        UPDATE agenda_evenements
        SET
            titre=%s,
            categorie=%s,
            description=%s,
            date_debut=%s,
            date_fin=%s,
            lieu=%s,
            statut=%s,
            organisateur=%s,
            id_client=%s,
            fournisseur=%s,
            piece=%s,
            quantite=%s,
            montant=%s,
            technicien=%s,
            hangar=%s,
            type_maintenance=%s
        WHERE id_evenement=%s
    """, (
        payload["titre"],
        payload["categorie"],
        payload["description"],
        payload["date_debut"],
        payload["date_fin"],
        payload["lieu"],
        payload["statut"],
        payload["organisateur"],
        payload["id_client"],
        payload["fournisseur"],
        payload["piece"],
        payload["quantite"],
        payload["montant"],
        payload["technicien"],
        payload["hangar"],
        payload["type_maintenance"],
        id_evenement
    ))

    log_action(
        "Modification événement",
        "agenda",
        f"id_evenement={id_evenement}"
    )

    return jsonify({
        "success": True,
        "message": "Événement modifié avec succès."
    })


# ==========================
# CHANGEMENT STATUT
# ==========================

@agenda_bp.route("/status/<int:id_evenement>", methods=["POST"])
@editor_required
def update_event_status(id_evenement):

    data = request.json if request.is_json else request.form
    statut = clean_value(data.get("statut"))

    allowed_status = {
        "PLANIFIE",
        "EN_COURS",
        "TERMINE",
        "ANNULE"
    }

    if statut not in allowed_status:
        return jsonify({
            "success": False,
            "error": "Statut invalide."
        }), 400

    execute("""
        UPDATE agenda_evenements
        SET statut=%s
        WHERE id_evenement=%s
    """, (statut, id_evenement))

    log_action(
        "Changement statut événement",
        "agenda",
        f"id_evenement={id_evenement}; statut={statut}"
    )

    return jsonify({
        "success": True,
        "message": "Statut mis à jour."
    })


# ==========================
# SUPPRESSION EVENEMENT
# ==========================

@agenda_bp.route(
    "/delete/<int:id_evenement>",
    methods=["POST", "DELETE"]
)
@admin_required
def delete_event(id_evenement):

    existing = fetch_one("""
        SELECT id_evenement
        FROM agenda_evenements
        WHERE id_evenement=%s
    """, (id_evenement,))

    if not existing:
        return jsonify({
            "success": False,
            "error": "Événement introuvable."
        }), 404

    execute("""
        DELETE FROM agenda_evenements
        WHERE id_evenement=%s
    """, (id_evenement,))

    log_action(
        "Suppression événement",
        "agenda",
        f"id_evenement={id_evenement}"
    )

    return jsonify({
        "success": True,
        "message": "Événement supprimé."
    })


# ==========================
# FORMAT FULLCALENDAR
# ==========================

@agenda_bp.route("/calendar", methods=["GET"])
@login_required
@agenda_bp.route("/calendar", methods=["GET"])
@login_required
def calendar_events():
    rows = fetch_all("""
        SELECT
            a.id_evenement,
            a.titre,
            a.categorie,
            a.date_debut,
            a.date_fin,
            a.statut,
            a.lieu,
            a.organisateur,
            a.id_client,
            c.nom_societe
        FROM agenda_evenements a
        LEFT JOIN clients c
            ON c.id_client = a.id_client
        WHERE a.date_debut IS NOT NULL
          AND a.date_debut <> '0000-00-00 00:00:00'
        ORDER BY a.date_debut ASC
    """)

    colors = {
        "REUNION_CLIENT": "#2563eb",
        "REUNION_ADMIN": "#64748b",
        "MAINTENANCE": "#dc2626",
        "COMMANDE_MATERIEL": "#ca8a04",
        "RECEPTION_MATERIEL": "#16a34a",
        "PAIEMENT": "#9333ea",
        "AUDIT": "#ea580c",
        "FORMATION": "#0891b2",
        "LIVRAISON": "#4f46e5",
        "AUTRE": "#6b7280"
    }

    events = []

    for row in rows:
        start = row.get("date_debut")
        end = row.get("date_fin")

        if not start:
            continue

        # FullCalendar attend de préférence une date ISO 8601
        if hasattr(start, "isoformat"):
            start = start.isoformat()

        if end and hasattr(end, "isoformat"):
            end = end.isoformat()

        events.append({
            "id": str(row["id_evenement"]),
            "title": row["titre"] or "Événement",
            "start": start,
            "end": end or None,
            "backgroundColor": colors.get(
                row["categorie"],
                "#6b7280"
            ),
            "borderColor": colors.get(
                row["categorie"],
                "#6b7280"
            ),
            "textColor": "#ffffff",
            "extendedProps": {
                "categorie": row.get("categorie"),
                "statut": row.get("statut"),
                "lieu": row.get("lieu"),
                "organisateur": row.get("organisateur"),
                "client": row.get("nom_societe")
            }
        })

    return jsonify(events)
    rows = fetch_all("""
        SELECT
            a.id_evenement,
            a.titre,
            a.categorie,
            a.date_debut,
            a.date_fin,
            a.statut,
            a.lieu,
            a.organisateur,
            a.id_client,
            c.nom_societe
        FROM agenda_evenements a
        LEFT JOIN clients c
            ON c.id_client = a.id_client
        ORDER BY a.date_debut ASC
    """)

    colors = {
        "REUNION_CLIENT": "#2563eb",
        "REUNION_ADMIN": "#64748b",
        "MAINTENANCE": "#dc2626",
        "COMMANDE_MATERIEL": "#ca8a04",
        "RECEPTION_MATERIEL": "#16a34a",
        "PAIEMENT": "#9333ea",
        "AUDIT": "#ea580c",
        "FORMATION": "#0891b2",
        "LIVRAISON": "#4f46e5",
        "AUTRE": "#6b7280"
    }

    events = []

    for row in rows:
        events.append({
            "id": row["id_evenement"],
            "title": row["titre"],
            "start": row["date_debut"],
            "end": row["date_fin"],
            "color": colors.get(row["categorie"], "#6b7280"),
            "extendedProps": {
                "categorie": row["categorie"],
                "statut": row["statut"],
                "lieu": row["lieu"],
                "organisateur": row["organisateur"],
                "client": row["nom_societe"]
            }
        })

    return jsonify(events)


# ==========================
# STATISTIQUES AGENDA
# ==========================

@agenda_bp.route("/stats", methods=["GET"])
@login_required
def agenda_stats():

    total = fetch_one("""
        SELECT COUNT(*) AS total
        FROM agenda_evenements
    """)["total"]

    today = fetch_one("""
        SELECT COUNT(*) AS total
        FROM agenda_evenements
        WHERE DATE(date_debut) = CURDATE()
    """)["total"]

    planned = fetch_one("""
        SELECT COUNT(*) AS total
        FROM agenda_evenements
        WHERE statut='PLANIFIE'
    """)["total"]

    in_progress = fetch_one("""
        SELECT COUNT(*) AS total
        FROM agenda_evenements
        WHERE statut='EN_COURS'
    """)["total"]

    by_category = fetch_all("""
        SELECT categorie, COUNT(*) AS total
        FROM agenda_evenements
        GROUP BY categorie
        ORDER BY total DESC
    """)

    return jsonify({
        "total": total,
        "today": today,
        "planned": planned,
        "in_progress": in_progress,
        "by_category": by_category
    })
