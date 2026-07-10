from app.extensions import db


class Cliente(db.Model):
    __tablename__ = "clientes"

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120))
    telefono = db.Column(db.String(20))
    direccion = db.Column(db.String(255))

    ventas = db.relationship("Venta", backref="cliente", lazy=True)

    def __repr__(self):
        return f"<Cliente {self.nombre}>"