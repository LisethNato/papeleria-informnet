from datetime import datetime
from app.extensions import db


class Venta(db.Model):
    __tablename__ = "ventas"

    id = db.Column(db.Integer, primary_key=True)
    fecha = db.Column(db.DateTime, default=datetime.utcnow)
    total = db.Column(db.Float, nullable=False, default=0.0)

    cliente_id = db.Column(db.Integer, db.ForeignKey("clientes.id"), nullable=False)
    usuario_id = db.Column(db.Integer, db.ForeignKey("usuarios.id"), nullable=False)

    usuario = db.relationship("Usuario", backref="ventas", lazy=True)
    detalles = db.relationship("DetalleVenta", backref="venta", lazy=True, cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Venta {self.id}>"