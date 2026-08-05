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
    try:
        rows = fetch_all("""
            SELECT *
            FROM alertes
            ORDER BY
                FIELD(
                    niveau,
                    'CRITIQUE',
                    'ATTENTION',
                    'INFO'
                ),
                id_alerte DESC
        """)

        return jsonify(rows)

    except Exception as error:
        print("ERREUR API ALERTES :", repr(error))

        return jsonify({
            "success": False,
            "error": str(error)
        }), 500


@alerts_bp.route("/open")
@login_required
def open_alerts():
    try:
        rows = fetch_all("""
            SELECT *
            FROM alertes
            WHERE statut = 'OUVERTE'
            ORDER BY id_alerte DESC
        """)

        return jsonify(rows)

    except Exception as error:
        print("ERREUR ALERTES OUVERTES :", repr(error))

        return jsonify({
            "success": False,
            "error": str(error)
        }), 500


@alerts_bp.route("/critical")
@login_required
def critical_alerts():
    try:
        rows = fetch_all("""
            SELECT *
            FROM alertes
            WHERE niveau = 'CRITIQUE'
            ORDER BY id_alerte DESC
        """)

        return jsonify(rows)

    except Exception as error:
        print("ERREUR ALERTES CRITIQUES :", repr(error))

        return jsonify({
            "success": False,
            "error": str(error)
        }), 500
