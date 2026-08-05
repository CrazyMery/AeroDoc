from flask import Blueprint, request, jsonify

from utils import (
    fetch_all,
    fetch_one,
    execute,
    login_required,
    editor_required,
    admin_required,
    log_action
)

stock_bp = Blueprint(
    "stock",
    __name__,
    url_prefix="/api/stock"
)

# =====================================================
# LISTE PIECES
# =====================================================

@stock_bp.route("/pieces")
@login_required
def list_pieces():

    rows = fetch_all("""

        SELECT *

        FROM pieces

        ORDER BY designation

    """)

    return jsonify(rows)


# =====================================================
# DETAIL PIECE
# =====================================================

@stock_bp.route("/piece/<int:id_piece>")
@login_required
def get_piece(id_piece):

    row = fetch_one("""

        SELECT *

        FROM pieces

        WHERE id_piece=%s

    """, (id_piece,))

    if not row:

        return jsonify({
            "error":"Pièce introuvable"
        }),404

    return jsonify(row)


# =====================================================
# RECHERCHE
# =====================================================

@stock_bp.route("/search")
@login_required
def search_piece():

    q = request.args.get("q","")

    rows = fetch_all("""

        SELECT *

        FROM pieces

        WHERE

            reference_piece LIKE %s

            OR designation LIKE %s

            OR categorie LIKE %s

        ORDER BY designation

    """, (

        f"%{q}%",

        f"%{q}%",

        f"%{q}%"

    ))

    return jsonify(rows)


# =====================================================
# AJOUT PIECE
# =====================================================

@stock_bp.route(
    "/piece/add",
    methods=["POST"]
)
@editor_required
def add_piece():

    data = (
        request.json
        if request.is_json
        else request.form
    )

    piece_id = execute("""

        INSERT INTO pieces
        (

            reference_piece,

            designation,

            categorie,

            quantite_stock,

            stock_alerte,

            prix_unitaire

        )

        VALUES
        (
            %s,%s,%s,%s,%s,%s
        )

    """, (

        data.get("reference_piece"),

        data.get("designation"),

        data.get("categorie"),

        data.get("quantite_stock",0),

        data.get("stock_alerte",0),

        data.get("prix_unitaire",0)

    ))

    log_action(
        "Ajout pièce",
        "stock",
        f"id_piece={piece_id}"
    )

    return jsonify({

        "success":True,

        "id_piece":piece_id

    })


# =====================================================
# MODIFICATION PIECE
# =====================================================

@stock_bp.route(
    "/piece/edit/<int:id_piece>",
    methods=["POST"]
)
@editor_required
def edit_piece(id_piece):

    data = (
        request.json
        if request.is_json
        else request.form
    )

    execute("""

        UPDATE pieces

        SET

            reference_piece=%s,

            designation=%s,

            categorie=%s,

            quantite_stock=%s,

            stock_alerte=%s,

            prix_unitaire=%s

        WHERE id_piece=%s

    """, (

        data.get("reference_piece"),

        data.get("designation"),

        data.get("categorie"),

        data.get("quantite_stock"),

        data.get("stock_alerte"),

        data.get("prix_unitaire"),

        id_piece

    ))

    return jsonify({
        "success":True
    })


# =====================================================
# ENTREE STOCK
# =====================================================

@stock_bp.route(
    "/entree",
    methods=["POST"]
)
@editor_required
def stock_in():

    data = (
        request.json
        if request.is_json
        else request.form
    )

    execute("""

        UPDATE pieces

        SET quantite_stock =
            quantite_stock + %s

        WHERE id_piece=%s

    """, (

        data.get("quantite"),

        data.get("id_piece")

    ))

    execute("""

        INSERT INTO mouvements_stock
        (
            id_piece,
            type_mouvement,
            quantite,
            commentaire
        )

        VALUES
        (
            %s,
            'ENTREE',
            %s,
            %s
        )

    """, (

        data.get("id_piece"),

        data.get("quantite"),

        data.get("commentaire")

    ))

    return jsonify({
        "success":True
    })


# =====================================================
# SORTIE STOCK
# =====================================================

@stock_bp.route(
    "/sortie",
    methods=["POST"]
)
@editor_required
def stock_out():

    data = (
        request.json
        if request.is_json
        else request.form
    )

    execute("""

        UPDATE pieces

        SET quantite_stock =
            quantite_stock - %s

        WHERE id_piece=%s

    """, (

        data.get("quantite"),

        data.get("id_piece")

    ))

    execute("""

        INSERT INTO mouvements_stock
        (
            id_piece,
            type_mouvement,
            quantite,
            commentaire
        )

        VALUES
        (
            %s,
            'SORTIE',
            %s,
            %s
        )

    """, (

        data.get("id_piece"),

        data.get("quantite"),

        data.get("commentaire")

    ))

    return jsonify({
        "success":True
    })


# =====================================================
# ALERTES STOCK
# =====================================================

@stock_bp.route("/alerts")
@login_required
def stock_alerts():

    rows = fetch_all("""

        SELECT *

        FROM pieces

        WHERE quantite_stock
            <= stock_alerte

        ORDER BY quantite_stock

    """)

    return jsonify(rows)


# =====================================================
# MOUVEMENTS
# =====================================================

@stock_bp.route("/movements")
@login_required
def stock_movements():

    rows = fetch_all("""

        SELECT

            m.*,

            p.designation

        FROM mouvements_stock m

        JOIN pieces p
            ON p.id_piece=m.id_piece

        ORDER BY
            m.date_mouvement DESC

    """)

    return jsonify(rows)


# =====================================================
# SUPPRESSION PIECE
# =====================================================

@stock_bp.route(
    "/piece/delete/<int:id_piece>",
    methods=["POST","DELETE"]
)
@admin_required
def delete_piece(id_piece):

    execute("""

        DELETE FROM pieces

        WHERE id_piece=%s

    """, (id_piece,))

    return jsonify({
        "success":True
    })


# =====================================================
# KPI STOCK
# =====================================================

@stock_bp.route("/stats")
@login_required
def stock_stats():

    total_pieces = fetch_one("""

        SELECT COUNT(*) total

        FROM pieces

    """)["total"]

    stock_total = fetch_one("""

        SELECT
            COALESCE(
                SUM(quantite_stock),
                0
            ) total

        FROM pieces

    """)["total"]

    stock_critique = fetch_one("""

        SELECT COUNT(*) total

        FROM pieces

        WHERE quantite_stock
            <= stock_alerte

    """)["total"]

    rupture = fetch_one("""

        SELECT COUNT(*) total

        FROM pieces

        WHERE quantite_stock <= 0

    """)["total"]

    return jsonify({

        "total_pieces":
            total_pieces,

        "stock_total":
            stock_total,

        "stock_critique":
            stock_critique,

        "rupture":
            rupture

    })