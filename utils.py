from functools import wraps

from flask import (
    session,
    jsonify,
    current_app
)

import os

import pymysql

from datetime import (
    datetime,
    date,
    timedelta
)


# =====================================================
# CONNEXION MYSQL
# =====================================================

def get_connection():

    return pymysql.connect(

        host=current_app.config["DB_HOST"],

        user=current_app.config["DB_USER"],

        password=current_app.config["DB_PASSWORD"],

        database=current_app.config["DB_NAME"],

        cursorclass=pymysql.cursors.DictCursor,

        autocommit=True

    )


# =====================================================
# FETCH ONE
# =====================================================

def fetch_one(query, params=None):

    conn = get_connection()

    try:

        with conn.cursor() as cur:

            cur.execute(
                query,
                params or ()
            )

            return cur.fetchone()

    finally:

        conn.close()


# =====================================================
# FETCH ALL
# =====================================================

def fetch_all(query, params=None):

    conn = get_connection()

    try:

        with conn.cursor() as cur:

            cur.execute(
                query,
                params or ()
            )

            return cur.fetchall()

    finally:

        conn.close()


# =====================================================
# EXECUTE
# =====================================================

def execute(query, params=None):

    conn = get_connection()

    try:

        with conn.cursor() as cur:

            cur.execute(
                query,
                params or ()
            )

            conn.commit()

            return cur.lastrowid

    finally:

        conn.close()


# =====================================================
# UTILISATEUR CONNECTE
# =====================================================

def current_user():

    user_id = session.get(
        "user_id"
    )

    if not user_id:
        return None

    return fetch_one("""

        SELECT *

        FROM utilisateurs

        WHERE id_user=%s

    """, (user_id,))


# =====================================================
# LOGIN REQUIRED
# =====================================================

def login_required(f):

    @wraps(f)
    def decorated(*args, **kwargs):

        if not session.get(
            "user_id"
        ):

            return jsonify({
                "error":
                "Authentification requise"
            }),401

        return f(
            *args,
            **kwargs
        )

    return decorated


# =====================================================
# EDITEUR
# =====================================================

def editor_required(f):

    @wraps(f)
    def decorated(*args, **kwargs):

        role = session.get(
            "role"
        )

        if role not in (
            "ADMIN",
            "EDITEUR"
        ):

            return jsonify({
                "error":
                "Permission refusée"
            }),403

        return f(
            *args,
            **kwargs
        )

    return decorated


# =====================================================
# ADMIN
# =====================================================

def admin_required(f):

    @wraps(f)
    def decorated(*args, **kwargs):

        if session.get(
            "role"
        ) != "ADMIN":

            return jsonify({
                "error":
                "Accès administrateur requis"
            }),403

        return f(
            *args,
            **kwargs
        )

    return decorated


# =====================================================
# LOG ACTION
# =====================================================

def log_action(
    action,
    module,
    details=None
):

    try:

        execute("""

            INSERT INTO journal_actions
            (

                id_user,

                action,

                module,

                details,

                date_action

            )

            VALUES
            (
                %s,%s,%s,%s,NOW()
            )

        """, (

            session.get(
                "user_id"
            ),

            action,

            module,

            details

        ))

    except:
        pass


# =====================================================
# PARSE DATE
# =====================================================

def parse_date(value):

    if not value:
        return None

    try:

        if isinstance(
            value,
            date
        ):
            return value

        return datetime.strptime(
            value,
            "%Y-%m-%d"
        ).date()

    except:
        return None


# =====================================================
# STATUT DOCUMENT
# =====================================================

def compute_document_status(
    expiration_date
):

    if not expiration_date:

        return "VALIDE"

    today = date.today()

    delta = (
        expiration_date
        - today
    ).days

    if delta < 0:
        return "EXPIRE"

    if delta <= 30:
        return "A_RENOUVELER"

    if delta <= 90:
        return "EXPIRATION_PROCHE"

    return "VALIDE"


# =====================================================
# NIVEAU ALERTE
# =====================================================

def alert_level(status):

    if status == "EXPIRE":
        return "CRITIQUE"

    if status == "A_RENOUVELER":
        return "ATTENTION"

    if status == "EXPIRATION_PROCHE":
        return "INFO"

    return "INFO"


# =====================================================
# DOSSIER UPLOAD
# =====================================================

def safe_upload_folder(
    subfolder
):

    root = current_app.config.get(
        "UPLOAD_FOLDER",
        "uploads"
    )

    folder = os.path.join(
        root,
        subfolder
    )

    os.makedirs(
        folder,
        exist_ok=True
    )

    return folder


# =====================================================
# FORMAT DATE JSON
# =====================================================

def json_date(value):

    if not value:
        return None

    if isinstance(
        value,
        (datetime, date)
    ):
        return value.isoformat()

    return str(value)


# =====================================================
# GENERATE REFERENCE
# =====================================================

def generate_reference(
    prefix
):

    now = datetime.now()

    return (
        f"{prefix}-"
        f"{now.year}-"
        f"{now.strftime('%H%M%S')}"
    )