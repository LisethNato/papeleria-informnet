from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required

from app.extensions import db
from app.models import Producto
from app.utils import admin_required

productos = Blueprint("productos", __name__, url_prefix="/productos")


@productos.route("/")
@login_required
def listar():
    lista = Producto.query.all()
    return render_template("productos/listar.html", productos=lista)


@productos.route("/nuevo", methods=["GET", "POST"])
@login_required
@admin_required
def crear():
    if request.method == "POST":
        nombre = request.form.get("nombre")
        descripcion = request.form.get("descripcion")
        precio = request.form.get("precio")
        stock = request.form.get("stock")

        nuevo = Producto(
            nombre=nombre,
            descripcion=descripcion,
            precio=float(precio),
            stock=int(stock),
        )
        db.session.add(nuevo)
        db.session.commit()

        flash("Producto creado correctamente.", "success")
        return redirect(url_for("productos.listar"))

    return render_template("productos/form.html", producto=None)


@productos.route("/editar/<int:id>", methods=["GET", "POST"])
@login_required
@admin_required
def editar(id):
    producto = Producto.query.get_or_404(id)

    if request.method == "POST":
        producto.nombre = request.form.get("nombre")
        producto.descripcion = request.form.get("descripcion")
        producto.precio = float(request.form.get("precio"))
        producto.stock = int(request.form.get("stock"))

        db.session.commit()

        flash("Producto actualizado correctamente.", "success")
        return redirect(url_for("productos.listar"))

    return render_template("productos/form.html", producto=producto)


@productos.route("/eliminar/<int:id>", methods=["POST"])
@login_required
@admin_required
def eliminar(id):
    producto = Producto.query.get_or_404(id)
    db.session.delete(producto)
    db.session.commit()

    flash("Producto eliminado.", "info")
    return redirect(url_for("productos.listar"))