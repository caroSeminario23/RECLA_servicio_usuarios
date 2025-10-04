from utils.db import db

class Estatus(db.Model):
    __tablename__ = 'estatus'

    # Características
    id_usuario = db.Column(
        db.Integer,
        db.ForeignKey('usuario.id_usuario'),
        nullable=True,
        primary_key=True
    )

    racha = db.Column(
        db.Integer,
        nullable=True,
        default=0
    )

    activo_hoy = db.Column(
        db.Boolean,
        nullable=True,
        default=False
    )

    logeo_hoy = db.Column(
        db.Boolean,
        nullable=True,
        default=False
    )

    n_compras = db.Column(
        db.Integer,
        nullable=True,
        default=0
    )

    n_ventas = db.Column(
        db.Integer,
        nullable=True,
        default=0
    )

    n_rec_educativos = db.Column(
        db.Integer,
        nullable=True,
        default=0
    )

    ptos_sistema = db.Column(
        db.Integer,
        nullable=True,
        default=0
    )

    # Objeto
    def __init__(self,
                 id_usuario):
        self.id_usuario = id_usuario