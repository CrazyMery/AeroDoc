from flask import Blueprint, jsonify

from utils import fetch_all, login_required


alerts_bp = Blueprint(
    "alerts",
    __name__,
    url_prefix="/api/alerts"
)


@alerts_bp.route("/")
@login_required
def get_alerts():
    """
    Retourne toutes les alertes, classées par niveau de priorité.
    Compatible SQLite.
    """

    rows = fetch_all("""
        SELECT
            id_alerte,
            niveau,
            titre,
            message,
            statut,
            date_creation
        FROM alertes
        ORDER BY
            CASE niveau
                WHEN 'CRITIQUE' THEN 1
                WHEN 'ATTENTION' THEN 2
                WHEN 'INFO' THEN 3
                ELSE 4
            END,
            id_alerte DESC
    """)

    return jsonify(rows)


@alerts_bp.route("/open")
@login_required
def open_alerts():
    """
    Retourne uniquement les alertes ouvertes.
    """

    rows = fetch_all("""
        SELECT
            id_alerte,
            niveau,
            titre,
            message,
            statut,
            date_creation
        FROM alertes
        WHERE statut = 'OUVERTE'
        ORDER BY
            CASE niveau
                WHEN 'CRITIQUE' THEN 1
                WHEN 'ATTENTION' THEN 2
                WHEN 'INFO' THEN 3
                ELSE 4
            END,
            id_alerte DESC
    """)

    return jsonify(rows)


@alerts_bp.route("/critical")
@login_required
def critical_alerts():
    """
    Retourne les alertes critiques ouvertes.
    """

    rows = fetch_all("""
        SELECT
            id_alerte,
            niveau,
            titre,
            message,
            statut,
            date_creation
        FROM alertes
        WHERE niveau = 'CRITIQUE'
          AND statut = 'OUVERTE'
        ORDER BY id_alerte DESC
    """)

    return jsonify(rows)