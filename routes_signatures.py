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

signatures_bp = Blueprint(
    "signatures",
    __name__,
    url_prefix="/api/signatures"
)

# =====================================================
# LISTE SIGNATURES
# =====================================================

@signatures_bp.route("/")
@login_required
def list_signatures():

    rows = fetch_all("""

        SELECT *

        FROM signatures

        ORDER BY date_signature DESC

    """)

    return jsonify(rows)


# =====================================================
# DETAIL SIGNATURE
# =====================================================

@signatures_bp.route(
    "/<int:id_signature>"
)
@login_required
def get_signature(id_signature):

    row = fetch_one("""

        SELECT *

        FROM signatures

        WHERE id_signature=%s

    """, (id_signature,))

    if not row:

        return jsonify({
            "error":"Signature introuvable"
        }),404

    return jsonify(row)


# =====================================================
# SIGNER DOCUMENT
# =====================================================

@signatures_bp.route(
    "/document/sign",
    methods=["POST"]
)
@editor_required
def sign_document():

    data = (
        request.json
        if request.is_json
        else request.form
    )

    signature_id = execute("""

        INSERT INTO signatures
        (

            type_signature,

            id_document,

            id_employe,

            id_client,

            nom_signataire,

            fonction_signataire,

            signature_base64,

            commentaire,

            date_signature

        )

        VALUES
        (
            %s,%s,%s,%s,%s,%s,%s,%s,NOW()
        )

    """, (

        "DOCUMENT",

        data.get("id_document"),

        data.get("id_employe"),

        data.get("id_client"),

        data.get("nom_signataire"),

        data.get("fonction_signataire"),

        data.get("signature_base64"),

        data.get("commentaire")

    ))

    execute("""

        UPDATE documents

        SET document_signe=1

        WHERE id_document=%s

    """, (

        data.get("id_document"),

    ))

    log_action(

        "Signature document",

        "signature",

        f"id_signature={signature_id}"

    )

    return jsonify({

        "success":True,

        "id_signature":signature_id

    })


# =====================================================
# SIGNER MAINTENANCE
# =====================================================

@signatures_bp.route(
    "/maintenance/sign",
    methods=["POST"]
)
@editor_required
def sign_maintenance():

    data = (
        request.json
        if request.is_json
        else request.form
    )

    signature_id = execute("""

        INSERT INTO signatures
        (

            type_signature,

            id_maintenance,

            id_employe,

            id_client,

            nom_signataire,

            fonction_signataire,

            signature_base64,

            commentaire,

            date_signature

        )

        VALUES
        (
            %s,%s,%s,%s,%s,%s,%s,%s,NOW()
        )

    """, (

        "MAINTENANCE",

        data.get("id_maintenance"),

        data.get("id_employe"),

        data.get("id_client"),

        data.get("nom_signataire"),

        data.get("fonction_signataire"),

        data.get("signature_base64"),

        data.get("commentaire")

    ))

    execute("""

        UPDATE maintenances

        SET statut='TERMINEE'

        WHERE id_maintenance=%s

    """, (

        data.get("id_maintenance"),

    ))

    log_action(

        "Validation maintenance",

        "signature",

        f"id_signature={signature_id}"

    )

    return jsonify({

        "success":True,

        "id_signature":signature_id

    })


# =====================================================
# SIGNATURE CLIENT
# =====================================================

@signatures_bp.route(
    "/client/sign",
    methods=["POST"]
)
@editor_required
def sign_client_document():

    data = (
        request.json
        if request.is_json
        else request.form
    )

    signature_id = execute("""

        INSERT INTO signatures
        (

            type_signature,

            id_client,

            nom_signataire,

            fonction_signataire,

            signature_base64,

            commentaire,

            date_signature

        )

        VALUES
        (
            'CLIENT',
            %s,
            %s,
            %s,
            %s,
            %s,
            NOW()
        )

    """, (

        data.get("id_client"),

        data.get("nom_signataire"),

        data.get("fonction_signataire"),

        data.get("signature_base64"),

        data.get("commentaire")

    ))

    return jsonify({

        "success":True,

        "id_signature":signature_id

    })


# =====================================================
# HISTORIQUE DOCUMENT
# =====================================================

@signatures_bp.route(
    "/document/<int:id_document>"
)
@login_required
def document_signatures(id_document):

    rows = fetch_all("""

        SELECT *

        FROM signatures

        WHERE id_document=%s

        ORDER BY date_signature DESC

    """, (id_document,))

    return jsonify(rows)


# =====================================================
# HISTORIQUE MAINTENANCE
# =====================================================

@signatures_bp.route(
    "/maintenance/<int:id_maintenance>"
)
@login_required
def maintenance_signatures(id_maintenance):

    rows = fetch_all("""

        SELECT *

        FROM signatures

        WHERE id_maintenance=%s

        ORDER BY date_signature DESC

    """, (id_maintenance,))

    return jsonify(rows)


# =====================================================
# VERIFICATION SIGNATURE
# =====================================================

@signatures_bp.route(
    "/verify/<int:id_signature>"
)
@login_required
def verify_signature(id_signature):

    row = fetch_one("""

        SELECT *

        FROM signatures

        WHERE id_signature=%s

    """, (id_signature,))

    if not row:

        return jsonify({
            "valid":False
        })

    return jsonify({

        "valid":True,

        "date_signature":
            row["date_signature"],

        "nom_signataire":
            row["nom_signataire"]

    })


# =====================================================
# SUPPRESSION
# =====================================================

@signatures_bp.route(
    "/delete/<int:id_signature>",
    methods=["POST","DELETE"]
)
@admin_required
def delete_signature(id_signature):

    execute("""

        DELETE FROM signatures

        WHERE id_signature=%s

    """, (id_signature,))

    return jsonify({
        "success":True
    })


# =====================================================
# STATS
# =====================================================

@signatures_bp.route("/stats")
@login_required
def signatures_stats():

    total = fetch_one("""

        SELECT COUNT(*) total

        FROM signatures

    """)["total"]

    documents = fetch_one("""

        SELECT COUNT(*) total

        FROM signatures

        WHERE type_signature='DOCUMENT'

    """)["total"]

    maintenances = fetch_one("""

        SELECT COUNT(*) total

        FROM signatures

        WHERE type_signature='MAINTENANCE'

    """)["total"]

    return jsonify({

        "total":
            total,

        "documents":
            documents,

        "maintenances":
            maintenances

    })