from flask import Blueprint, request, jsonify
from utils import fetch_all, fetch_one, execute, login_required, editor_required, admin_required, log_action

clients_bp = Blueprint("clients", __name__, url_prefix="/api/clients")
@clients_bp.route("/panier", methods=["GET"])
def get_panier():

    rows = fetch_all("""
        SELECT
            pc.id_panier,
            c.nom_societe,
            p.designation,
            pc.quantite,
            pc.statut
        FROM panier_client pc
        LEFT JOIN clients c
            ON pc.id_client = c.id_client
        LEFT JOIN pieces p
            ON pc.id_piece = p.id_piece
        ORDER BY pc.id_panier DESC
    """)

    return jsonify(rows)

@clients_bp.route("/")
@login_required
def list_clients():
    rows = fetch_all("""
        SELECT c.*,
               COUNT(d.id_document) AS document_count,
               COUNT(m.id_maintenance) AS maintenance_count
        FROM clients c
        LEFT JOIN documents d ON d.id_client = c.id_client
        LEFT JOIN maintenances m ON m.id_client = c.id_client
        GROUP BY c.id_client
        ORDER BY c.nom_societe
    """)
    return jsonify(rows)

@clients_bp.route("/<int:id_client>")
@login_required
def get_client(id_client):
    c = fetch_one("SELECT * FROM clients WHERE id_client=%s", (id_client,))
    if not c:
        return jsonify({"error": "Client introuvable"}), 404

    docs = fetch_all("SELECT * FROM documents WHERE id_client=%s ORDER BY date_import DESC", (id_client,))
    panier = fetch_all("""
        SELECT pc.*, p.reference_piece, p.designation, p.quantite_stock
        FROM panier_client pc
        JOIN pieces p ON p.id_piece = pc.id_piece
        WHERE pc.id_client=%s
        ORDER BY pc.date_demande DESC
    """, (id_client,))
    maintenances = fetch_all("SELECT * FROM maintenances WHERE id_client=%s", (id_client,))

    return jsonify({
        "client": c,
        "documents": docs,
        "panier": panier,
        "maintenances": maintenances
    })

@clients_bp.route("/add", methods=["POST"])
@editor_required
def add_client():
    data = request.json if request.is_json else request.form

    client_id = execute("""
        INSERT INTO clients
        (nom_societe, contact_principal, telephone, email, adresse, type_aeronef, numero_contrat)
        VALUES (%s,%s,%s,%s,%s,%s,%s)
    """, (
        data.get("nom_societe"),
        data.get("contact_principal"),
        data.get("telephone"),
        data.get("email"),
        data.get("adresse"),
        data.get("type_aeronef"),
        data.get("numero_contrat")
    ))

    log_action("Création client", "clients", f"id_client={client_id}")
    return jsonify({"success": True, "id_client": client_id})

@clients_bp.route("/edit/<int:id_client>", methods=["POST"])
@editor_required
def edit_client(id_client):
    data = request.json if request.is_json else request.form

    execute("""
        UPDATE clients
        SET nom_societe=%s, contact_principal=%s, telephone=%s, email=%s,
            adresse=%s, type_aeronef=%s, numero_contrat=%s
        WHERE id_client=%s
    """, (
        data.get("nom_societe"),
        data.get("contact_principal"),
        data.get("telephone"),
        data.get("email"),
        data.get("adresse"),
        data.get("type_aeronef"),
        data.get("numero_contrat"),
        id_client
    ))

    log_action("Modification client", "clients", f"id_client={id_client}")
    return jsonify({"success": True})

@clients_bp.route("/delete/<int:id_client>", methods=["POST", "DELETE"])
@admin_required
def delete_client(id_client):
    execute("DELETE FROM clients WHERE id_client=%s", (id_client,))
    log_action("Suppression client", "clients", f"id_client={id_client}")
    return jsonify({"success": True})
