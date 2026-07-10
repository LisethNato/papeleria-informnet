from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user

from app.extensions import db
from app.models import Usuario
from app.utils import admin_required

usuarios = Blueprint("usuarios", __name__, url_prefix="/usuarios")


@usuarios.route("/")
@login_required
@admin_required
def listar():
    lista = Usuario.query.all()
    return render_template("usuarios/listar.html", usuarios=lista)


@usuarios.route("/nuevo", methods=["GET", "POST"])
@login_required
@admin_required
def crear():
    if request.method == "POST":
        nombre = request.form.get("nombre")
        email = request.form.get("email")
        password = request.form.get("password")
        rol = request.form.get("rol")

        if Usuario.query.filter_by(email=email).first():
            flash("Ya existe un usuario con ese correo.", "danger")
            return redirect(url_for("usuarios.crear"))

        nuevo = Usuario(nombre=nombre, email=email, rol=rol)
        nuevo.set_password(password)

        db.session.add(nuevo)
        db.session.commit()

        flash("Usuario creado correctamente.", "success")
        return redirect(url_for("usuarios.listar"))

    return render_template("usuarios/form.html", usuario=None)


@usuarios.route("/editar/<int:id>", methods=["GET", "POST"])
@login_required
@admin_required
def editar(id):
    usuario = Usuario.query.get_or_404(id)

    if request.method == "POST":
        usuario.nombre = request.form.get("nombre")
        usuario.email = request.form.get("email")
        usuario.rol = request.form.get("rol")

        nueva_password = request.form.get("password")
        if nueva_password:
            usuario.set_password(nueva_password)

        db.session.commit()

        flash("Usuario actualizado correctamente.", "success")
        return redirect(url_for("usuarios.listar"))

    return render_template("usuarios/form.html", usuario=usuario)


@usuarios.route("/eliminar/<int:id>", methods=["POST"])
@login_required
@admin_required
def eliminar(id):
    usuario = Usuario.query.get_or_404(id)

    if usuario.id == current_user.id:
        flash("No puedes eliminar tu propia cuenta.", "danger")
        return redirect(url_for("usuarios.listar"))

    db.session.delete(usuario)
    db.session.commit()

    flash("Usuario eliminado.", "info")
    return redirect(url_for("usuarios.listar"))