from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    session,
    jsonify
)

from werkzeug.security import (
    check_password_hash,
    generate_password_hash
)

from datetime import datetime

from utils import (
    fetch_one,
    execute,
    current_user,
    login_required,
    log_action
)

auth_bp = Blueprint("auth", __name__)


# ==========================
# LOGIN
# ==========================

@auth_bp.route("/login", methods=["GET", "POST"])
def login():

    if session.get("user_id"):
        return redirect(url_for("index"))

    if request.method == "GET":
        return render_template("login.html")

    login_value = (
        request.form.get("login", "")
        .strip()
    )

    password = request.form.get(
        "password",
        ""
    )

    user = fetch_one("""

        SELECT *
        FROM utilisateurs

        WHERE login=%s

    """, (login_value,))

    if not user:

        return render_template(
            "login.html",
            error="Identifiant ou mot de passe incorrect."
        )

    if user["statut"] != "ACTIF":

        return render_template(
            "login.html",
            error="Compte désactivé."
        )

    stored_password = (
        user["mot_de_passe"] or ""
    )

    valid_password = False

    if stored_password.startswith(
        ("pbkdf2:", "scrypt:")
    ):

        valid_password = check_password_hash(
            stored_password,
            password
        )

    else:
        valid_password = (
            stored_password == password
        )

    if not valid_password:

        execute("""

            UPDATE utilisateurs

            SET tentatives_connexion=
                COALESCE(
                    tentatives_connexion,
                    0
                ) + 1

            WHERE id_user=%s

        """, (user["id_user"],))

        log_action(
            "Echec connexion",
            "auth",
            login_value
        )

        return render_template(
            "login.html",
            error="Mot de passe incorrect."
        )

    execute("""

        UPDATE utilisateurs

        SET

            derniere_connexion=NOW(),

            tentatives_connexion=0

        WHERE id_user=%s

    """, (user["id_user"],))

    session["user_id"] = user["id_user"]
    session["role"] = user["role"]
    session["nom"] = user["nom"]

    log_action(
        "Connexion utilisateur",
        "auth",
        user["login"]
    )

    return redirect(
        url_for("index")
    )


# ==========================
# LOGOUT
# ==========================

@auth_bp.route("/logout")
def logout():

    user_id = session.get(
        "user_id"
    )

    if user_id:

        log_action(
            "Déconnexion utilisateur",
            "auth",
            f"id_user={user_id}"
        )

    session.clear()

    return redirect(
        url_for("auth.login")
    )


# ==========================
# UTILISATEUR CONNECTE
# ==========================

@auth_bp.route("/api/auth/me")
@login_required
def auth_me():

    user = current_user()

    if not user:

        return jsonify({
            "error":"Utilisateur introuvable"
        }),404

    return jsonify({

        "id_user":
            user["id_user"],

        "nom":
            user["nom"],

        "prenom":
            user["prenom"],

        "email":
            user["email"],

        "role":
            user["role"],

        "login":
            user["login"],

        "statut":
            user["statut"]

    })


# ==========================
# CHANGER MOT DE PASSE
# ==========================

@auth_bp.route(
    "/api/auth/change-password",
    methods=["POST"]
)
@login_required
def change_password():

    user = current_user()

    data = (
        request.json
        if request.is_json
        else request.form
    )

    old_password = data.get(
        "old_password"
    )

    new_password = data.get(
        "new_password"
    )

    if not old_password:

        return jsonify({
            "error":
            "Ancien mot de passe obligatoire."
        }),400

    if not new_password:

        return jsonify({
            "error":
            "Nouveau mot de passe obligatoire."
        }),400

    if len(new_password) < 6:

        return jsonify({
            "error":
            "Minimum 6 caractères."
        }),400

    stored_password = (
        user["mot_de_passe"]
        or ""
    )

    valid = False

    if stored_password.startswith(
        ("pbkdf2:", "scrypt:")
    ):

        valid = check_password_hash(
            stored_password,
            old_password
        )

    else:

        valid = (
            stored_password ==
            old_password
        )

    if not valid:

        return jsonify({
            "error":
            "Ancien mot de passe incorrect."
        }),400

    password_hash = generate_password_hash(
        new_password
    )

    execute("""

        UPDATE utilisateurs

        SET mot_de_passe=%s

        WHERE id_user=%s

    """, (
        password_hash,
        user["id_user"]
    ))

    log_action(
        "Changement mot de passe",
        "auth",
        f"id_user={user['id_user']}"
    )

    return jsonify({
        "success":True
    })


# ==========================
# GENERATEUR HASH
# ==========================

@auth_bp.route(
    "/api/auth/hash",
    methods=["POST"]
)
def api_hash_password():

    data = (
        request.json
        if request.is_json
        else request.form
    )

    password = data.get(
        "password"
    )

    if not password:

        return jsonify({
            "error":
            "password obligatoire"
        }),400

    return jsonify({

        "hash":
        generate_password_hash(
            password
        )

    })


# ==========================
# TEST AUTH
# ==========================

@auth_bp.route("/api/auth/ping")
@login_required
def ping():

    return jsonify({

        "success":True,

        "message":
        "Utilisateur authentifié"

    })