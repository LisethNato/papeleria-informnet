from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user

from app.extensions import db
from app.models import Venta, DetalleVenta, Producto, Cliente

ventas = Blueprint("ventas", __name__, url_prefix="/ventas")


@ventas.route("/")
@login_required
def listar():
    lista = Venta.query.order_by(Venta.fecha.desc()).all()
    return render_template("ventas/listar.html", ventas=lista)


@ventas.route("/nueva", methods=["GET", "POST"])
@login_required
def crear():
    clientes = Cliente.query.all()
    productos = Producto.query.all()

    if request.method == "POST":
        cliente_id = request.form.get("cliente_id")

        if not cliente_id:
            flash("Debes seleccionar un cliente.", "danger")
            return redirect(url_for("ventas.crear"))

        nueva_venta = Venta(cliente_id=int(cliente_id), usuario_id=current_user.id, total=0.0)
        db.session.add(nueva_venta)
        db.session.flush()  # para obtener nueva_venta.id antes del commit

        total = 0.0
        huno_producto = False

        for producto in productos:
            cantidad_str = request.form.get(f"cantidad_{producto.id}")
            cantidad = int(cantidad_str) if cantidad_str else 0

            if cantidad > 0:
                if cantidad > producto.stock:
                    db.session.rollback()
                    flash(f"Stock insuficiente para '{producto.nombre}'. Disponible: {producto.stock}", "danger")
                    return redirect(url_for("ventas.crear"))

                subtotal = cantidad * producto.precio

                detalle = DetalleVenta(
                    venta_id=nueva_venta.id,
                    producto_id=producto.id,
                    cantidad=cantidad,
                    precio_unitario=producto.precio,
                    subtotal=subtotal,
                )
                db.session.add(detalle)

                producto.stock -= cantidad
                total += subtotal
                huno_producto = True

        if not huno_producto:
            db.session.rollback()
            flash("Debes agregar al menos un producto con cantidad mayor a 0.", "danger")
            return redirect(url_for("ventas.crear"))

        nueva_venta.total = total
        db.session.commit()

        flash("Venta registrada correctamente.", "success")
        return redirect(url_for("ventas.listar"))

    return render_template("ventas/form.html", clientes=clientes, productos=productos)


@ventas.route("/<int:id>")
@login_required
def detalle(id):
    venta = Venta.query.get_or_404(id)
    return render_template("ventas/detalle.html", venta=venta)