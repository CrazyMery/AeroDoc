from flask import Blueprint, request, jsonify, send_file
from werkzeug.utils import secure_filename

import os

from utils import (
    fetch_all,
    fetch_one,
    execute,
    login_required,
    editor_required,
    admin_required,
    log_action,
    safe_upload_folder,
    parse_date,
    compute_document_status
)

documents_bp = Blueprint(
    "documents",
    __name__,
    url_prefix="/api/documents"
)

# =====================================================
# LISTE DOCUMENTS
# =====================================================

@documents_bp.route("/")
@login_required
def list_documents():

    rows = fetch_all("""

        SELECT
            d.*,
            e.nom,
            e.prenom,
            c.nom_societe

        FROM documents d

        LEFT JOIN employes e
            ON e.id_employe = d.id_employe

        LEFT JOIN clients c
            ON c.id_client = d.id_client

        ORDER BY d.id_document DESC

    """)

    return jsonify(rows)


# =====================================================
# RECHERCHE
# =====================================================

@documents_bp.route("/search")
@login_required
def search_documents():

    q = request.args.get("q","")

    rows = fetch_all("""

        SELECT *

        FROM documents

        WHERE

            nom_fichier LIKE %s

            OR type_document LIKE %s

            OR statut LIKE %s

        ORDER BY id_document DESC

    """,(

        f"%{q}%",

        f"%{q}%",

        f"%{q}%"

    ))

    return jsonify(rows)


# =====================================================
# DETAIL DOCUMENT
# =====================================================

@documents_bp.route("/<int:id_document>")
@login_required
def get_document(id_document):

    row = fetch_one("""

        SELECT *

        FROM documents

        WHERE id_document=%s

    """,(id_document,))

    if not row:

        return jsonify({
            "error":"Document introuvable"
        }),404

    return jsonify(row)


# =====================================================
# AJOUT DOCUMENT
# =====================================================

@documents_bp.route(
    "/add",
    methods=["POST"]
)
@editor_required
def add_document():

    data = request.form

    uploaded = request.files.get("file")

    nom_fichier = None
    chemin_fichier = None

    if uploaded:

        folder = safe_upload_folder(
            "documents"
        )

        filename = secure_filename(
            uploaded.filename
        )

        filepath = os.path.join(
            folder,
            filename
        )

        uploaded.save(filepath)

        nom_fichier = filename

        chemin_fichier = filepath

    expiration = None

    if data.get("date_expiration"):

        expiration = parse_date(
            data.get(
                "date_expiration"
            )
        )

    statut = compute_document_status(
        expiration
    )

    doc_id = execute("""

        INSERT INTO documents
        (

            id_employe,

            id_client,

            type_document,

            nom_fichier,

            chemin_fichier,

            date_expiration,

            statut,

            commentaire

        )

        VALUES
        (
            %s,%s,%s,%s,
            %s,%s,%s,%s
        )

    """,(

        data.get("id_employe"),

        data.get("id_client"),

        data.get("type_document"),

        nom_fichier,

        chemin_fichier,

        data.get(
            "date_expiration"
        ),

        statut,

        data.get(
            "commentaire"
        )

    ))

    log_action(
        "Ajout document",
        "documents",
        f"id_document={doc_id}"
    )

    return jsonify({

        "success":True,

        "id_document":doc_id

    })


# =====================================================
# MODIFICATION
# =====================================================

@documents_bp.route(
    "/edit/<int:id_document>",
    methods=["POST"]
)
@editor_required
def edit_document(id_document):

    data = (
        request.json
        if request.is_json
        else request.form
    )

    expiration = None

    if data.get("date_expiration"):

        expiration = parse_date(
            data.get(
                "date_expiration"
            )
        )

    statut = compute_document_status(
        expiration
    )

    execute("""

        UPDATE documents

        SET

            type_document=%s,

            date_expiration=%s,

            statut=%s,

            commentaire=%s

        WHERE id_document=%s

    """,(

        data.get("type_document"),

        data.get("date_expiration"),

        statut,

        data.get("commentaire"),

        id_document

    ))

    log_action(
        "Modification document",
        "documents",
        f"id_document={id_document}"
    )

    return jsonify({
        "success":True
    })


# =====================================================
# TELECHARGEMENT
# =====================================================

@documents_bp.route(
    "/download/<int:id_document>"
)
@login_required
def download_document(id_document):

    doc = fetch_one("""

        SELECT *

        FROM documents

        WHERE id_document=%s

    """,(id_document,))

    if not doc:

        return jsonify({
            "error":"Document introuvable"
        }),404

    if not doc["chemin_fichier"]:

        return jsonify({
            "error":"Fichier absent"
        }),404

    return send_file(

        doc["chemin_fichier"],

        as_attachment=True

    )


# =====================================================
# SUPPRESSION
# =====================================================

@documents_bp.route(
    "/delete/<int:id_document>",
    methods=["POST","DELETE"]
)
@admin_required
def delete_document(id_document):

    execute("""

        DELETE

        FROM documents

        WHERE id_document=%s

    """,(id_document,))

    log_action(
        "Suppression document",
        "documents",
        f"id_document={id_document}"
    )

    return jsonify({
        "success":True
    })


# =====================================================
# STATS
# =====================================================

@documents_bp.route("/stats")
@login_required
def document_stats():

    total = fetch_one("""

        SELECT COUNT(*) total

        FROM documents

    """)["total"]

    expires = fetch_one("""

        SELECT COUNT(*) total

        FROM documents

        WHERE statut='EXPIRE'

    """)["total"]

    renouveler = fetch_one("""

        SELECT COUNT(*) total

        FROM documents

        WHERE statut='A_RENOUVELER'

    """)["total"]

    return jsonify({

        "total":total,

        "expires":expires,

        "renouveler":renouveler

    })