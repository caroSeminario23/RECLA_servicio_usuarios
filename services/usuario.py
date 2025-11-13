from flask import Blueprint, request, jsonify, make_response
from marshmallow import ValidationError
from sqlalchemy.exc import IntegrityError
import time
from sqlalchemy import text

from utils.db import db
from utils.logger import get_logger
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

# Configurar el logger
logger = get_logger(__name__)

usuario_routes = Blueprint("usuario_routes", __name__)

# REGISTRO DE USUARIO
@usuario_routes.route("/registro_ecoaprendiz", methods=["POST"])
def registro_ecoaprendiz():
    inicio_tiempo = time.time()
    try:
        logger.info("Solicitud de registro de ecoaprendiz recibida")
        datos = usuario_registro_schema.load(request.json)
        logger.debug("Datos de registro validados correctamente")
    except ValidationError as err:
        logger.warning(f"Error de validación en registro: {err.messages}")
        return make_response(jsonify({"errors": err.messages, "status": 400}), 400)

    email = datos["email"]
    contrasena = datos["contrasena"]
    fec_nac = datos["fec_nac"]
    username = datos["username"]
    
    logger.debug(f"Procesando registro para email: {email}, username: {username}")
    contrasena_encriptada = encriptar_contrasena(contrasena)

    nuevo_usuario = Usuario(
        email=email,
        contrasena=contrasena_encriptada,
        fec_nac=fec_nac,
        username=username
    )

    try:
        logger.debug(f"Guardando nuevo usuario en BD: {username}")
        db.session.add(nuevo_usuario)
        db.session.commit()
        logger.info(f"Usuario creado exitosamente: {username}, ID: {nuevo_usuario.id_usuario}")
    except IntegrityError:
        db.session.rollback()
        logger.warning(f"Error de integridad al crear usuario {username}: Email o username duplicado")
        return make_response(jsonify({
            "message": "El email o username ya está en uso",
            "status": 400
        }), 400)
    
    # Crear un registro de estatus asociado al nuevo usuario
    nuevo_estatus = Estatus(
        id_usuario=nuevo_usuario.id_usuario
    )

    try:
        logger.debug(f"Creando registro de estatus para usuario ID: {nuevo_usuario.id_usuario}")
        db.session.add(nuevo_estatus)
        db.session.commit()
        logger.info(f"Estatus creado exitosamente para usuario ID: {nuevo_usuario.id_usuario}")
    except IntegrityError:
        db.session.rollback()
        logger.error(f"Error al crear el estatus para usuario ID: {nuevo_usuario.id_usuario}")
        return make_response(jsonify({
            "message": "Error al crear el estatus",
            "status": 500
        }), 500)

    tiempo_respuesta = time.time() - inicio_tiempo
    logger.info(f"Registro de ecoaprendiz completado exitosamente. Usuario: {username}. Tiempo: {tiempo_respuesta:.3f}s")

    data = {
        "message": "Registro de ecoaprendiz exitoso",
        "status": 201
    }

    return make_response(jsonify(data), 201)


# INICIO DE SESIÓN
@usuario_routes.route("/login_ecoaprendiz", methods=["POST"])
def login_ecoaprendiz():
    inicio_tiempo = time.time()
    try:
        logger.info("Solicitud de login de ecoaprendiz recibida")
        datos = usuario_login_request_schema.load(request.json)
        logger.debug("Datos de login validados correctamente")
    except ValidationError as err:
        logger.warning(f"Error de validación en login: {err.messages}")
        return make_response(jsonify({"errors": err.messages, "status": 400}), 400)

    email = datos["email"]
    contrasena = datos["contrasena"]
    
    logger.debug(f"Verificando credenciales para email: {email}")
    usuario = Usuario.query.filter_by(email=email).first()

    if not usuario or not verificar_contrasena(contrasena, usuario.contrasena):
        tiempo_respuesta = time.time() - inicio_tiempo
        logger.warning(f"Intento de login fallido para email: {email}. Tiempo: {tiempo_respuesta:.3f}s")
        data = {
            "message": "Credenciales inválidas",
            "status": 401
        }
        return make_response(jsonify(data), 401)

    logger.info(f"Login exitoso para usuario ID: {usuario.id_usuario}, email: {email}")
    resultado = usuario_login_response_schema.dump(usuario)

    # Si la respuesta es exitosa, se registra el logeo en estatus
    estatus = Estatus.query.filter_by(id_usuario=usuario.id_usuario).first()

    if estatus:
        try:
            # 1. LLAMAMOS A LA FUNCIÓN DE RESETEO DIARIO
            # Esto se ejecutará en la misma transacción
            logger.debug("Ejecutando verificación de reseteo diario...")
            db.session.execute(text("SELECT fn_verificar_reinicio()"))
            
            # 2. AHORA ACTUALIZAMOS EL ESTATUS DEL USUARIO ACTUAL
            logger.debug(f"Actualizando estatus de logeo para usuario ID: {usuario.id_usuario}")
            estatus.logeo_hoy = True

            # 3. HACEMOS COMMIT DE AMBAS OPERACIONES
            db.session.commit()
            logger.info(f"Estatus de logeo actualizado para usuario ID: {usuario.id_usuario}")
            
        except IntegrityError as e:
            db.session.rollback()
            logger.error(f"Error al actualizar estatus de logeo para usuario ID: {usuario.id_usuario}: {e}")
            return make_response(jsonify({
                "message": "Error al actualizar el estado de logeo",
                "status": 500
            }), 500)

    tiempo_respuesta = time.time() - inicio_tiempo
    logger.info(f"Proceso de login completado exitosamente. Usuario ID: {usuario.id_usuario}. Tiempo: {tiempo_respuesta:.3f}s")

    data = {
        "message": "Inicio de sesión exitoso",
        "status": 200,
        "data": resultado
    }

    return make_response(jsonify(data), 200)


# VERIFICAR EMAIL
@usuario_routes.route("/verificar_email", methods=["POST"])
def verificar_email():
    inicio_tiempo = time.time()
    try:
        logger.info("Solicitud de verificación de email recibida")
        datos = email_validacion_schema.load(request.json)
        logger.debug("Datos de email validados correctamente")
    except ValidationError as err:
        logger.warning(f"Error de validación en verificación de email: {err.messages}")
        return make_response(jsonify({"errors": err.messages, "status": 400}), 400)

    email = datos["email"]
    logger.debug(f"Verificando disponibilidad de email: {email}")
    
    usuario = Usuario.query.filter_by(email=email).first()

    tiempo_respuesta = time.time() - inicio_tiempo

    if usuario:
        logger.info(f"Email {email} ya está en uso. Tiempo: {tiempo_respuesta:.3f}s")
        data = {
            "message": "El email ya está en uso",
            "status": 409
        }
        return make_response(jsonify(data), 409)

    logger.info(f"Email {email} está disponible. Tiempo: {tiempo_respuesta:.3f}s")
    data = {
        "message": "El email está disponible",
        "status": 200
    }

    return make_response(jsonify(data), 200)


# VERIFICAR USERNAME
@usuario_routes.route("/verificar_username", methods=["POST"])
def verificar_username():
    inicio_tiempo = time.time()
    try:
        logger.info("Solicitud de verificación de username recibida")
        datos = username_validacion_schema.load(request.json)
        logger.debug("Datos de username validados correctamente")
    except ValidationError as err:
        logger.warning(f"Error de validación en verificar_username: {err.messages}")
        return make_response(jsonify({"errors": err.messages, "status": 400}), 400)

    username = datos["username"]
    logger.debug(f"Verificando disponibilidad de username: {username}")

    usuario = Usuario.query.filter_by(username=username).first()

    tiempo_respuesta = time.time() - inicio_tiempo

    if usuario:
        logger.info(f"Username {username} ya está en uso. Tiempo: {tiempo_respuesta:.3f}s")
        data = {
            "message": "El username ya está en uso",
            "status": 409
        }
        return make_response(jsonify(data), 409)

    logger.info(f"Username {username} está disponible. Tiempo: {tiempo_respuesta:.3f}s")
    data = {
        "message": "El username está disponible",
        "status": 200
    }

    return make_response(jsonify(data), 200)


# OBTENER NOMBRE DE USUARIO DEL VENDEDOR
@usuario_routes.route("/obtener_username_vendedor", methods=["POST"])
def obtener_username_vendedor():
    inicio_tiempo = time.time()
    try:
        logger.info("Solicitud de obtención de username vendedor recibida")
        datos = vendedor_request_schema.load(request.json)
        logger.debug("Datos de vendedor validados correctamente")
    except ValidationError as err:
        logger.warning(f"Error de validación en obtener_username_vendedor: {err.messages}")
        return make_response(jsonify({"errors": err.messages, "status": 400}), 400)

    id_usuario = datos["id_usuario"]
    logger.debug(f"Buscando vendedor con ID: {id_usuario}")

    usuario = Usuario.query.filter_by(id_usuario=id_usuario).first()

    tiempo_respuesta = time.time() - inicio_tiempo

    if not usuario:
        logger.warning(f"Vendedor no encontrado para ID: {id_usuario}. Tiempo: {tiempo_respuesta:.3f}s")
        data = {
            "message": "Vendedor no encontrado",
            "status": 404
        }
        return make_response(jsonify(data), 404)

    logger.info(f"Vendedor encontrado: ID {id_usuario}, username: {usuario.username}. Tiempo: {tiempo_respuesta:.3f}s")
    resultado = vendedor_response_schema.dump(usuario)

    data = {
        "message": "Vendedor encontrado",
        "status": 200,
        "data": resultado
    }

    return make_response(jsonify(data), 200)


# OBTENER EMAIL DEL USUARIO
@usuario_routes.route("/obtener_email_usuario", methods=["POST"])
def obtener_email_usuario():
    inicio_tiempo = time.time()
    try:
        logger.info("Solicitud de obtención de email de usuario recibida")
        required_fields = ['id_usuario']
        if not request.json or not all(field in request.json for field in required_fields):
            logger.warning("Solicitud sin id_usuario en obtener_email_usuario")
            return make_response(jsonify({
                'status': 400,
                'message': 'id_usuario es requerido'
            }), 400)

        id_usuario = request.json.get('id_usuario')
        logger.debug(f"Buscando email para usuario ID: {id_usuario}")

        usuario_email = Usuario.query.filter_by(id_usuario=id_usuario).first().email

        if not usuario_email:
            tiempo_respuesta = time.time() - inicio_tiempo
            logger.warning(f"Usuario no encontrado para ID: {id_usuario}. Tiempo: {tiempo_respuesta:.3f}s")
            return make_response(jsonify({
                'status': 404,
                'message': 'Usuario no encontrado'
            }), 404)
        
        tiempo_respuesta = time.time() - inicio_tiempo
        logger.info(f"Email obtenido exitosamente para usuario ID: {id_usuario}. Tiempo: {tiempo_respuesta:.3f}s")

        data = {
            'status': 200,
            'message': 'Email obtenido exitosamente',
            'data': {
                'email': usuario_email
            }
        }
        return make_response(jsonify(data), 200)

    except Exception as e:
        tiempo_respuesta = time.time() - inicio_tiempo
        logger.error(f"Error en obtener_email_usuario: {e}. Tiempo: {tiempo_respuesta:.3f}s")
        return make_response(jsonify({
            'status': 500,
            'message': 'Error interno del servidor',
            'error': str(e)
        }), 500)