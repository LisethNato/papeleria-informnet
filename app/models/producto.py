from app.extensions import db


class Producto(db.Model):
    __tablename__ = "productos"

    id = db.Column(db.Integer, primary_key=True)

    nombre = db.Column(db.String(100), nullable=False)

    descripcion = db.Column(db.String(255))

    precio = db.Column(db.Float, nullable=False)

    stock = db.Column(db.Integer, nullable=False)

    def __repr__(self):
        return f"<Producto {self.nombre}>"