from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash

from utils import (
    fetch_all,
    fetch_one,
    execute,
    login_required,
    admin_required,
    log_action
)

users_bp = Blueprint(
    "users",
    __name__,
    url_prefix="/api/users"
)

# =====================================================
# LISTE UTILISATEURS
# =====================================================

@users_bp.route("/")
@login_required
def list_users():

    rows = fetch_all("""

        SELECT

            id_user,
            nom,
            prenom,
            login,
            email,
            role,
            statut,
            derniere_connexion

        FROM utilisateurs

        ORDER BY nom

    """)

    return jsonify(rows)


# =====================================================
# DETAIL UTILISATEUR
# =====================================================

@users_bp.route("/<int:id_user>")
@login_required
def get_user(id_user):

    row = fetch_one("""

        SELECT

            id_user,
            nom,
            prenom,
            login,
            email,
            role,
            statut,
            derniere_connexion

        FROM utilisateurs

        WHERE id_user=%s

    """, (id_user,))

    if not row:

        return jsonify({
            "error":"Utilisateur introuvable"
        }),404

    return jsonify(row)


# =====================================================
# AJOUT UTILISATEUR
# =====================================================

@users_bp.route(
    "/add",
    methods=["POST"]
)
@admin_required
def add_user():

    data = (
        request.json
        if request.is_json
        else request.form
    )

    existing = fetch_one("""

        SELECT id_user

        FROM utilisateurs

        WHERE login=%s

    """, (

        data.get("login"),

    ))

    if existing:

        return jsonify({

            "success":False,

            "error":
            "Login déjà utilisé"

        }),400

    password_hash = generate_password_hash(
        data.get("mot_de_passe")
    )

    user_id = execute("""

        INSERT INTO utilisateurs
        (

            nom,
            prenom,

            login,

            mot_de_passe,

            email,

            role,

            statut

        )

        VALUES
        (
            %s,%s,
            %s,%s,
            %s,%s,
            %s
        )

    """, (

        data.get("nom"),

        data.get("prenom"),

        data.get("login"),

        password_hash,

        data.get("email"),

        data.get(
            "role",
            "LECTEUR"
        ),

        "ACTIF"

    ))

    log_action(
        "Création utilisateur",
        "users",
        f"id_user={user_id}"
    )

    return jsonify({

        "success":True,

        "id_user":user_id

    })


# =====================================================
# MODIFICATION
# =====================================================

@users_bp.route(
    "/edit/<int:id_user>",
    methods=["POST"]
)
@admin_required
def edit_user(id_user):

    data = (
        request.json
        if request.is_json
        else request.form
    )

    execute("""

        UPDATE utilisateurs

        SET

            nom=%s,

            prenom=%s,

            email=%s,

            role=%s,

            statut=%s

        WHERE id_user=%s

    """, (

        data.get("nom"),

        data.get("prenom"),

        data.get("email"),

        data.get("role"),

        data.get("statut"),

        id_user

    ))

    log_action(
        "Modification utilisateur",
        "users",
        f"id_user={id_user}"
    )

    return jsonify({
        "success":True
    })


# =====================================================
# RESET PASSWORD
# =====================================================

@users_bp.route(
    "/reset-password/<int:id_user>",
    methods=["POST"]
)
@admin_required
def reset_password(id_user):

    data = (
        request.json
        if request.is_json
        else request.form
    )

    password = data.get(
        "mot_de_passe"
    )

    password_hash = generate_password_hash(
        password
    )

    execute("""

        UPDATE utilisateurs

        SET mot_de_passe=%s

        WHERE id_user=%s

    """, (

        password_hash,

        id_user

    ))

    log_action(
        "Réinitialisation mot de passe",
        "users",
        f"id_user={id_user}"
    )

    return jsonify({
        "success":True
    })


# =====================================================
# ACTIVER
# =====================================================

@users_bp.route(
    "/activate/<int:id_user>",
    methods=["POST"]
)
@admin_required
def activate_user(id_user):

    execute("""

        UPDATE utilisateurs

        SET statut='ACTIF'

        WHERE id_user=%s

    """, (id_user,))

    return jsonify({
        "success":True
    })


# =====================================================
# DESACTIVER
# =====================================================

@users_bp.route(
    "/disable/<int:id_user>",
    methods=["POST"]
)
@admin_required
def disable_user(id_user):

    execute("""

        UPDATE utilisateurs

        SET statut='INACTIF'

        WHERE id_user=%s

    """, (id_user,))

    return jsonify({
        "success":True
    })


# =====================================================
# SUPPRESSION
# =====================================================

@users_bp.route(
    "/delete/<int:id_user>",
    methods=["POST","DELETE"]
)
@admin_required
def delete_user(id_user):

    execute("""

        DELETE FROM utilisateurs

        WHERE id_user=%s

    """, (id_user,))

    log_action(
        "Suppression utilisateur",
        "users",
        f"id_user={id_user}"
    )

    return jsonify({
        "success":True
    })


# =====================================================
# STATISTIQUES
# =====================================================

@users_bp.route("/stats")
@login_required
def user_stats():

    total = fetch_one("""

        SELECT COUNT(*) total

        FROM utilisateurs

    """)["total"]

    actifs = fetch_one("""

        SELECT COUNT(*) total

        FROM utilisateurs

        WHERE statut='ACTIF'

    """)["total"]

    admins = fetch_one("""

        SELECT COUNT(*) total

        FROM utilisateurs

        WHERE role='ADMIN'

    """)["total"]

    editeurs = fetch_one("""

        SELECT COUNT(*) total

        FROM utilisateurs

        WHERE role='EDITEUR'

    """)["total"]

    lecteurs = fetch_one("""

        SELECT COUNT(*) total

        FROM utilisateurs

        WHERE role='LECTEUR'

    """)["total"]

    return jsonify({

        "total":
            total,

        "actifs":
            actifs,

        "admins":
            admins,

        "editeurs":
            editeurs,

        "lecteurs":
            lecteurs

    })