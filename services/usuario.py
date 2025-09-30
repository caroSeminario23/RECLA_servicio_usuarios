from flask import Blueprint, request, jsonify, make_response
from marshmallow import ValidationError
from sqlalchemy.exc import IntegrityError

from utils.db import db
from utils.encriptar_contrasena import encriptar_contrasena, verificar_contrasena
from models.usuario import Usuario
from models.estatus import Estatus
from schemas.usuario import (vendedor_request_schema,
                             vendedor_response_schema,
                             usuario_login_request_schema,
                             usuario_login_response_schema,
                             usuario_registro_schema,
                             email_validacion_schema,
                             username_validacion_schema)

usuario_routes = Blueprint("usuario_routes", __name__)

# REGISTRO DE USUARIO
@usuario_routes.route("/registro_ecoaprendiz", methods=["POST"])
def registro_ecoaprendiz():
    try:
        datos = usuario_registro_schema.load(request.json)
    except ValidationError as err:
        return make_response(jsonify({"errors": err.messages, "status": 400}), 400)

    email = datos["email"]
    contrasena = datos["contrasena"]
    fec_nac = datos["fec_nac"]
    username = datos["username"]
    
    contrasena_encriptada = encriptar_contrasena(contrasena)

    nuevo_usuario = Usuario(
        email=email,
        contrasena=contrasena_encriptada,
        fec_nac=fec_nac,
        username=username
    )

    try:
        db.session.add(nuevo_usuario)
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return make_response(jsonify({
            "message": "El email o username ya está en uso",
            "status": 400
        }), 400)
    
    # Crear un registro de estatus asociado al nuevo usuario
    nuevo_estatus = Estatus(
        id_usuario=nuevo_usuario.id_usuario
    )

    try:
        db.session.add(nuevo_estatus)
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return make_response(jsonify({
            "message": "Error al crear el estatus",
            "status": 500
        }), 500)

    data = {
        "message": "Registro de ecoaprendiz exitoso",
        "status": 201
    }

    return make_response(jsonify(data), 201)


# INICIO DE SESIÓN
@usuario_routes.route("/login_ecoaprendiz", methods=["POST"])
def login_ecoaprendiz():
    try:
        datos = usuario_login_request_schema.load(request.json)
    except ValidationError as err:
        return make_response(jsonify({"errors": err.messages, "status": 400}), 400)

    email = datos["email"]
    contrasena = datos["contrasena"]
    
    usuario = Usuario.query.filter_by(email=email).first()

    if not usuario or not verificar_contrasena(contrasena, usuario.contrasena):
        data = {
            "message": "Credenciales inválidas",
            "status": 401
        }
        return make_response(jsonify(data), 401)

    resultado = usuario_login_response_schema.dump(usuario)

    # Si la respuesta es exitosa, se registra el logeo en estatus
    estatus = Estatus.query.filter_by(id_usuario=usuario.id_usuario).first()

    if estatus:
        try:
            estatus.logeo_hoy = True
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            return make_response(jsonify({
                "message": "Error al actualizar el estado de logeo",
                "status": 500
            }), 500)

    data = {
        "message": "Inicio de sesión exitoso",
        "status": 200,
        "data": resultado
    }

    return make_response(jsonify(data), 200)


# VERIFICAR EMAIL
@usuario_routes.route("/verificar_email", methods=["POST"])
def verificar_email():
    try:
        datos = email_validacion_schema.load(request.json)
    except ValidationError as err:
        return make_response(jsonify({"errors": err.messages, "status": 400}), 400)

    email = datos["email"]
    
    usuario = Usuario.query.filter_by(email=email).first()

    if usuario:
        data = {
            "message": "El email ya está en uso",
            "status": 409
        }
        return make_response(jsonify(data), 409)

    data = {
        "message": "El email está disponible",
        "status": 200
    }

    return make_response(jsonify(data), 200)


# VERIFICAR USERNAME
@usuario_routes.route("/verificar_username", methods=["POST"])
def verificar_username():
    try:
        datos = username_validacion_schema.load(request.json)
    except ValidationError as err:
        return make_response(jsonify({"errors": err.messages, "status": 400}), 400)

    username = datos["username"]

    usuario = Usuario.query.filter_by(username=username).first()

    if usuario:
        data = {
            "message": "El username ya está en uso",
            "status": 409
        }
        return make_response(jsonify(data), 409)

    data = {
        "message": "El username está disponible",
        "status": 200
    }

    return make_response(jsonify(data), 200)


# OBTENER NOMBRE DE USUARIO DEL VENDEDOR
@usuario_routes.route("/obtener_username_vendedor", methods=["POST"])
def obtener_username_vendedor():
    try:
        datos = vendedor_request_schema.load(request.json)
    except ValidationError as err:
        return make_response(jsonify({"errors": err.messages, "status": 400}), 400)

    id_usuario = datos["id_usuario"]

    usuario = Usuario.query.filter_by(id_usuario=id_usuario).first()

    if not usuario:
        data = {
            "message": "Vendedor no encontrado",
            "status": 404
        }
        return make_response(jsonify(data), 404)

    resultado = vendedor_response_schema.dump(usuario)

    data = {
        "message": "Vendedor encontrado",
        "status": 200,
        "data": resultado
    }

    return make_response(jsonify(data), 200)