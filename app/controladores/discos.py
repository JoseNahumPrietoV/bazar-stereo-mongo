from math import ceil

from flask import Blueprint, render_template, request
from flask_login import current_user

from app.models.disco import Disco

discos_bp = Blueprint("discos", __name__)
PER_PAGE = 12

@discos_bp.route("/discos")
def discos():
    formatos_select = [f for f in request.args.getlist("formato") if f]
    generos_select = request.args.getlist("generos")

    qs = Disco.objects(estado=0)

    if current_user.is_authenticated:
        qs = qs.filter(id_usuario__ne=current_user.id_usuario)

    if formatos_select:
        filtros = []
        if "cd" in formatos_select:
            filtros.append(False)
        if "vinilo" in formatos_select:
            filtros.append(True)
        if filtros:
            qs = qs.filter(formato__in=filtros)

    if generos_select:
        mapa_inverso = {v: k for k, v in Disco.MAPA_GENEROS.items()}
        generos_ids = [
            mapa_inverso.get(g)
            for g in generos_select
            if mapa_inverso.get(g) is not None
        ]
        if generos_ids:
            qs = qs.filter(genero__in=generos_ids)

    page = request.args.get("page", 1, type=int)
    page = max(page,1)

    total_discos = qs.count()

    total_pages = ceil(total_discos / PER_PAGE) if total_discos > 0 else 1
    page = min(page, total_pages)

    skip = (page - 1) * PER_PAGE
    discos_result = qs.skip(skip).limit(PER_PAGE)

    context = {
        "discos": discos_result,  # El QuerySet es iterable directamente en Jinja2
        "lista_generos": list(Disco.MAPA_GENEROS.values()),
        "formatos_select": formatos_select,
        "generos_select": generos_select,
        "page": page,
        "total_pages": total_pages,
        "total_discos": total_discos,
        "per_page": PER_PAGE,
    }

    if request.headers.get("HX-Request"):
        return render_template("partials/_discos_grid.html", **context)

    return render_template("discos.html", **context)
