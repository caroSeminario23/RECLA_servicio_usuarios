from utils.db import db

class Estatus(db.Model):
    __tablename__ = 'estatus'

    # Características
    id_usuario = db.Column(
        db.Integer,
        db.ForeignKey('usuario.id_usuario'),
        autoincrement=True,
        nullable=True,
        primary_key=True
    )

    racha = db.Column(
        db.Integer,
        nullable=True
    )

    activo_hoy = db.Column(
        db.Boolean,
        nullable=True
    )

    logeo_hoy = db.Column(
        db.Boolean,
        nullable=True
    )

    n_compras = db.Column(
        db.Integer,
        nullable=True
    )

    n_ventas = db.Column(
        db.Integer,
        nullable=True
    )

    n_rec_educativos = db.Column(
        db.Integer,
        nullable=True
    )

    ptos_sistema = db.Column(
        db.Integer,
        nullable=True
    )

    # Objeto
    def __init__(self,
                 id_usuario):
        self.id_usuario = id_usuario