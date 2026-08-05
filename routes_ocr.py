from flask import Blueprint, request, jsonify
from werkzeug.utils import secure_filename

import os
import re

import pytesseract

from PIL import Image

from utils import (
    execute,
    fetch_one,
    login_required,
    editor_required,
    log_action,
    safe_upload_folder
)

ocr_bp = Blueprint(
    "ocr",
    __name__,
    url_prefix="/api/ocr"
)


# =====================================================
# EXTRACTION TEXTE
# =====================================================

@ocr_bp.route(
    "/scan",
    methods=["POST"]
)
@login_required
def scan_document():

    uploaded = (
        request.files.get("file")
        or request.files.get("image")
        or request.files.get("scan_mobile")
    )

    if not uploaded:

        return jsonify({
            "success":False,
            "error":"Fichier manquant"
        }),400

    filename = secure_filename(
        uploaded.filename
    )

    folder = safe_upload_folder(
        "ocr"
    )

    filepath = os.path.join(
        folder,
        filename
    )

    uploaded.save(filepath)

    try:

        image = Image.open(
            filepath
        )

        text = pytesseract.image_to_string(
            image,
            lang="fra+eng"
        )

    except Exception as e:

        return jsonify({

            "success":False,

            "error":str(e)

        }),500

    return jsonify({

        "success":True,

        "filename":filename,

        "text":text

    })


# =====================================================
# OCR + EXTRACTION DONNEES
# =====================================================

@ocr_bp.route(
    "/analyse",
    methods=["POST"]
)
@login_required
def analyse_document():

    uploaded = (
        request.files.get("file")
        or request.files.get("image")
    )

    if not uploaded:

        return jsonify({
            "success":False
        }),400

    filename = secure_filename(
        uploaded.filename
    )

    folder = safe_upload_folder(
        "ocr"
    )

    filepath = os.path.join(
        folder,
        filename
    )

    uploaded.save(filepath)

    image = Image.open(
        filepath
    )

    text = pytesseract.image_to_string(
        image,
        lang="fra+eng"
    )

    matricule = None
    licence = None
    expiration = None

    matricule_match = re.search(
        r"(MAT|MATRICULE)\s*[:\-]?\s*([A-Z0-9]+)",
        text,
        re.IGNORECASE
    )

    if matricule_match:
        matricule = matricule_match.group(2)

    licence_match = re.search(
        r"(LICENCE|LICENSE)\s*[:\-]?\s*([A-Z0-9\-]+)",
        text,
        re.IGNORECASE
    )

    if licence_match:
        licence = licence_match.group(2)

    date_match = re.search(
        r"(\d{2}/\d{2}/\d{4})",
        text
    )

    if date_match:
        expiration = date_match.group(1)

    return jsonify({

        "success":True,

        "texte":text,

        "matricule":matricule,

        "licence":licence,

        "expiration":expiration

    })


# =====================================================
# OCR -> DOCUMENT
# =====================================================

@ocr_bp.route(
    "/create-document",
    methods=["POST"]
)
@editor_required
def create_document_from_ocr():

    data = (
        request.json
        if request.is_json
        else request.form
    )

    document_id = execute("""

        INSERT INTO documents
        (

            id_employe,

            type_document,

            nom_fichier,

            date_expiration,

            commentaire,

            statut

        )

        VALUES
        (
            %s,%s,%s,%s,%s,%s
        )

    """, (

        data.get("id_employe"),

        data.get("type_document"),

        data.get("nom_fichier"),

        data.get("date_expiration"),

        "Créé par OCR",

        "VALIDE"

    ))

    log_action(

        "Document créé OCR",

        "ocr",

        f"id_document={document_id}"

    )

    return jsonify({

        "success":True,

        "id_document":document_id

    })


# =====================================================
# VERIFICATION LICENCE
# =====================================================

@ocr_bp.route(
    "/check-license",
    methods=["POST"]
)
@login_required
def check_license():

    text = request.json.get(
        "text",
        ""
    )

    issues = []

    if "licence" not in text.lower():
        issues.append(
            "Licence non détectée"
        )

    if len(text) < 50:
        issues.append(
            "Document incomplet"
        )

    return jsonify({

        "valid":
            len(issues)==0,

        "issues":
            issues

    })


# =====================================================
# IA DOCUMENTAIRE
# =====================================================

@ocr_bp.route(
    "/ai-check",
    methods=["POST"]
)
@login_required
def ai_check():

    text = request.json.get(
        "text",
        ""
    )

    warnings = []

    if "signature" not in text.lower():
        warnings.append(
            "Signature absente"
        )

    if "date" not in text.lower():
        warnings.append(
            "Date absente"
        )

    if len(text) < 100:
        warnings.append(
            "Contenu insuffisant"
        )

    return jsonify({

        "success":True,

        "warnings":warnings

    })


# =====================================================
# STATS OCR
# =====================================================

@ocr_bp.route("/stats")
@login_required
def ocr_stats():

    total_docs = fetch_one("""

        SELECT COUNT(*) total

        FROM documents

    """)

    return jsonify({

        "documents_analyses":
            total_docs["total"]

    })