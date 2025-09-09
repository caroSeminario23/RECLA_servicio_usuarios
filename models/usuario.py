from utils.db import db

class Usuario(db.Model):
    __tablename__ = 'usuario'

    # Características
    id_usuario = db.Column(
        db.Integer,
        primary_key=True,
        autoincrement=True,
        nullable=True
    )

    email = db.Column(
        db.String(40),
        unique=True,
        nullable=True
    )

    contrasena = db.Column(
        db.String(60),
        nullable=True
    )

    fec_nac = db.Column(
        db.Date,
        nullable=True
    )

    username = db.Column(
        db.String(20),
        unique=True,
        nullable=True
    )

    # Objeto
    def __init__(self, 
                 email,
                 contrasena,
                 fec_nac,
                 username):
        self.email = email
        self.contrasena = contrasena
        self.fec_nac = fec_nac
        self.username = username