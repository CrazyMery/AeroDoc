from flask import Blueprint, jsonify
from utils import (
    fetch_one,
    fetch_all,
    login_required
)

dashboard_bp = Blueprint(
    "dashboard",
    __name__,
    url_prefix="/api/dashboard"
)


@dashboard_bp.route("/")
@login_required
def dashboard():

    total_employes = fetch_one(
        "SELECT COUNT(*) total FROM employes"
    )["total"]

    total_users = fetch_one(
        "SELECT COUNT(*) total FROM utilisateurs"
    )["total"]

    total_documents = fetch_one(
        "SELECT COUNT(*) total FROM documents"
    )["total"]

    valid_documents = fetch_one("""
        SELECT COUNT(*) total
        FROM documents
        WHERE statut='VALIDE'
    """)["total"]

    renew_documents = fetch_one("""
        SELECT COUNT(*) total
        FROM documents
        WHERE statut IN
        (
            'A_RENOUVELER',
            'EXPIRATION_PROCHE'
        )
    """)["total"]

    expired_documents = fetch_one("""
        SELECT COUNT(*) total
        FROM documents
        WHERE statut='EXPIRE'
    """)["total"]

    active_alerts = fetch_one("""
        SELECT COUNT(*) total
        FROM alertes
        WHERE statut='OUVERTE'
    """)["total"]

    total_clients = fetch_one("""
        SELECT COUNT(*) total
        FROM clients
    """)["total"]

    total_maintenances = fetch_one("""
        SELECT COUNT(*) total
        FROM maintenances
    """)["total"]

    maint_planifiees = fetch_one("""
        SELECT COUNT(*) total
        FROM maintenances
        WHERE statut='PLANIFIEE'
    """)["total"]

    maint_en_cours = fetch_one("""
        SELECT COUNT(*) total
        FROM maintenances
        WHERE statut='EN_COURS'
    """)["total"]

    stock_total = fetch_one("""
        SELECT
            COALESCE(
                SUM(quantite_stock),
                0
            ) total
        FROM pieces
    """)["total"]

    pieces_critiques = fetch_one("""
        SELECT COUNT(*) total
        FROM pieces
        WHERE quantite_stock <= stock_alerte
    """)["total"]

    pieces_rupture = fetch_one("""
        SELECT COUNT(*) total
        FROM pieces
        WHERE quantite_stock <= 0
    """)["total"]

    total_commandes = fetch_one("""
        SELECT COUNT(*) total
        FROM panier_client
    """)["total"]

    commandes_validees = fetch_one("""
        SELECT COUNT(*) total
        FROM panier_client
        WHERE statut='VALIDEE'
    """)["total"]

    agenda_total = fetch_one("""
        SELECT COUNT(*) total
        FROM agenda_evenements
    """)["total"]

    agenda_today = fetch_one("""
        SELECT COUNT(*) total
        FROM agenda_evenements
        WHERE DATE(date_debut)=CURDATE()
    """)["total"]

    agenda_reunions = fetch_one("""
        SELECT COUNT(*) total
        FROM agenda_evenements
        WHERE categorie IN
        (
            'REUNION_CLIENT',
            'REUNION_ADMIN'
        )
    """)["total"]

    agenda_maintenances = fetch_one("""
        SELECT COUNT(*) total
        FROM agenda_evenements
        WHERE categorie='MAINTENANCE'
    """)["total"]

    top_pieces = fetch_all("""
        SELECT
            p.designation,
            SUM(pc.quantite) total
        FROM panier_client pc
        JOIN pieces p
            ON p.id_piece=pc.id_piece
        WHERE pc.statut='VALIDEE'
        GROUP BY
            p.id_piece,
            p.designation
        ORDER BY total DESC
        LIMIT 10
    """)

    qualifications = fetch_all("""
        SELECT
            nom_qualification,
            COUNT(*) total
        FROM qualifications
        GROUP BY nom_qualification
        ORDER BY total DESC
    """)

    return jsonify({

        "total_employes":
            total_employes,

        "total_users":
            total_users,

        "total_documents":
            total_documents,

        "valid_documents":
            valid_documents,

        "renew_documents":
            renew_documents,

        "expired_documents":
            expired_documents,

        "active_alerts":
            active_alerts,

        "total_clients":
            total_clients,

        "total_maintenances":
            total_maintenances,

        "maint_planifiees":
            maint_planifiees,

        "maint_en_cours":
            maint_en_cours,

        "stock_total":
            int(stock_total or 0),

        "pieces_critiques":
            pieces_critiques,

        "pieces_rupture":
            pieces_rupture,

        "total_commandes":
            total_commandes,

        "commandes_validees":
            commandes_validees,

        "agenda_total":
            agenda_total,

        "agenda_today":
            agenda_today,

        "agenda_reunions":
            agenda_reunions,

        "agenda_maintenances":
            agenda_maintenances,

        "top_pieces":
            top_pieces,

        "qualifications":
            qualifications

    })