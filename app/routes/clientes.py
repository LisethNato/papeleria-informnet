from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required

from app.extensions import db
from app.models import Cliente
from app.utils import admin_required

clientes = Blueprint("clientes", __name__, url_prefix="/clientes")


@clientes.route("/")
@login_required
def listar():
    lista = Cliente.query.all()
    return render_template("clientes/listar.html", clientes=lista)


@clientes.route("/nuevo", methods=["GET", "POST"])
@login_required
@admin_required
def crear():
    if request.method == "POST":
        nombre = request.form.get("nombre")
        email = request.form.get("email")
        telefono = request.form.get("telefono")
        direccion = request.form.get("direccion")

        nuevo = Cliente(
            nombre=nombre,
            email=email,
            telefono=telefono,
            direccion=direccion,
        )
        db.session.add(nuevo)
        db.session.commit()

        flash("Cliente creado correctamente.", "success")
        return redirect(url_for("clientes.listar"))

    return render_template("clientes/form.html", cliente=None)


@clientes.route("/editar/<int:id>", methods=["GET", "POST"])
@login_required
@admin_required
def editar(id):
    cliente = Cliente.query.get_or_404(id)

    if request.method == "POST":
        cliente.nombre = request.form.get("nombre")
        cliente.email = request.form.get("email")
        cliente.telefono = request.form.get("telefono")
        cliente.direccion = request.form.get("direccion")

        db.session.commit()

        flash("Cliente actualizado correctamente.", "success")
        return redirect(url_for("clientes.listar"))

    return render_template("clientes/form.html", cliente=cliente)


@clientes.route("/eliminar/<int:id>", methods=["POST"])
@login_required
@admin_required
def eliminar(id):
    cliente = Cliente.query.get_or_404(id)
    db.session.delete(cliente)
    db.session.commit()

    flash("Cliente eliminado.", "info")
    return redirect(url_for("clientes.listar"))