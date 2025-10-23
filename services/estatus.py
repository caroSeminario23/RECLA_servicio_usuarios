from flask import Blueprint, request, jsonify, make_response
import logging

from utils.db import db
from models.estatus import Estatus
from schemas.estatus import (estatus_perfil_schema,
                             estatus_contadores_schema)

# Configurar el logger
logger = logging.getLogger(__name__)

estatus_routes = Blueprint("estatus_routes", __name__)

# MOSTRAR ESTATUS DE PERFIL
@estatus_routes.route("/estatus_perfil", methods=["POST"])
def mostrar_estatus_perfil():
    try:
        logger.info(f"Solicitud de estatus de perfil recibida")
        required_fields = ['id_usuario']
        if not request.json or not all(field in request.json for field in required_fields):
            logger.warning("Solicitud sin id_usuario")
            return make_response(jsonify({
                "message": "id_usuario es requerido",
                "status": 400
            }), 400)
        
        id_usuario = request.json.get('id_usuario')
        logger.info(f"Consultando estatus para usuario: {id_usuario}")

        # Validar que no sea None o vacío
        if not id_usuario:
            logger.warning(f"Solicitud con id_usuario vacío")
            return make_response(jsonify({
                "message": "id_usuario no puede ser None o vacío",
                "status": 400
            }), 400)
        
        estatus = Estatus.query.filter_by(id_usuario=id_usuario).first()
        if not estatus:
            logger.warning(f"Estatus no encontrado para usuario: {id_usuario}")
            return make_response(jsonify({
                "message": "Estatus no encontrado",
                "status": 404
            }), 404)
        
        logger.info(f"Estatus de perfil obtenido exitosamente para usuario: {id_usuario}")
        resultado = estatus_perfil_schema.dump(estatus)

        data = {
            "message": "Estatus de perfil obtenido exitosamente",
            "status": 200,
            "data": resultado
        }

        return make_response(jsonify(data), 200)
    
    except Exception as err:
        logger.error(f"Error en mostrar_estatus_perfil: {err}")  # Para debugging
        return make_response(jsonify({
            'status': 500,
            'message': 'Error procesando la solicitud'
        }), 500)
    

# MOSTRAR ESTATUS DE CONTADORES
@estatus_routes.route("/estatus_contadores", methods=["POST"])
def mostrar_estatus_contadores():
    try:
        logger.info("Solicitud de estatus de contadores recibida")
        required_fields = ['id_usuario']
        if not request.json or not all(field in request.json for field in required_fields):
            logger.warning("Solicitud sin id_usuario en estatus_contadores")
            return make_response(jsonify({
                "message": "id_usuario es requerido",
                "status": 400
            }), 400)

        id_usuario = request.json.get('id_usuario')
        logger.info(f"Consultando contadores para usuario: {id_usuario}")

        # Validar que no sea None o vacío
        if not id_usuario:
            logger.warning(f"Solicitud con id_usuario vacío en estatus_contadores")
            return make_response(jsonify({
                "message": "id_usuario no puede ser None o vacío",
                "status": 400
            }), 400)

        estatus = Estatus.query.filter_by(id_usuario=id_usuario).first()
        if not estatus:
            logger.warning(f"Contadores no encontrados para usuario: {id_usuario}")
            return make_response(jsonify({
                "message": "Estatus no encontrado",
                "status": 404
            }), 404)

        resultado = estatus_contadores_schema.dump(estatus)
        logger.info(f"Contadores obtenidos exitosamente para usuario: {id_usuario}")

        data = {
            "message": "Estatus de contadores obtenido exitosamente",
            "status": 200,
            "data": resultado
        }

        return make_response(jsonify(data), 200)

    except Exception as err:
        logger.error(f"Error en mostrar_estatus_contadores: {err}")  # Para debugging
        return make_response(jsonify({
            'status': 500,
            'message': 'Error procesando la solicitud'
        }), 500)


# REGISTRAR ACTIVIDAD DIARIA
@estatus_routes.route("/registrar_actividad", methods=["POST"])
def registrar_actividad():
    try:
        logger.info("Solicitud de registro de actividad recibida")
        required_fields = ['id_usuario']
        if not request.json or not all(field in request.json for field in required_fields):
            logger.warning("Solicitud sin id_usuario en registrar_actividad")
            return make_response(jsonify({
                "message": "id_usuario es requerido",
                "status": 400
            }), 400)

        id_usuario = request.json.get('id_usuario')
        logger.debug(f"Procesando registro de actividad para usuario: {id_usuario}")

        # Validar que no sean None o vacíos
        if not id_usuario:
            logger.warning("Solicitud con id_usuario vacío en registrar_actividad")
            return make_response(jsonify({
                "message": "id_usuario no puede ser None o vacío",
                "status": 400
            }), 400)

        estatus = Estatus.query.filter_by(id_usuario=id_usuario).first()
        if not estatus:
            logger.warning(f"Estatus no encontrado para registrar actividad - usuario: {id_usuario}")
            return make_response(jsonify({
                "message": "Estatus no encontrado",
                "status": 404
            }), 404)
        
        if estatus.activo_hoy == False:
            estatus.activo_hoy = True
            db.session.commit()
            logger.info(f"Actividad diaria registrada para usuario: {id_usuario}")
        else:
            logger.debug(f"Usuario {id_usuario} ya tenía actividad registrada hoy")

        data = {
            "message": "Actividad registrada exitosamente",
            "status": 201
        }

        return make_response(jsonify(data), 201)

    except Exception as err:
        logger.error(f"Error en registrar_actividad: {err}")  # Para debugging
        return make_response(jsonify({
            'status': 500,
            'message': 'Error procesando la solicitud'
        }), 500)
    

# VERIFICADOR DE PUNTOS INSIGNIA
@estatus_routes.route("/verificar_puntos_insignia", methods=["POST"])
def verificar_puntos_insignia():
    try:
        logger.info("Solicitud de verificación de puntos insignia recibida")
        required_fields = ['id_usuario', 'tipo_insignia', 'precio_insignia']
        if not request.json or not all(field in request.json for field in required_fields):
            logger.warning("Solicitud incompleta en verificar_puntos_insignia")
            return make_response(jsonify({
                "message": "id_usuario, tipo_insignia y precio_insignia son requeridos",
                "status": 400
            }), 400)

        id_usuario = request.json.get('id_usuario')
        tipo_insignia = request.json.get('tipo_insignia')
        precio_insignia = request.json.get('precio_insignia')

        logger.debug(f"Verificando insignia tipo {tipo_insignia} con precio {precio_insignia} para usuario {id_usuario}")

        # Validar que no sea None o vacío
        if not id_usuario:
            logger.warning("id_usuario vacío en verificar_puntos_insignia")
            return make_response(jsonify({
                "message": "id_usuario no puede ser None o vacío",
                "status": 400
            }), 400)
        
        if not tipo_insignia:
            logger.warning(f"tipo_insignia vacío para usuario {id_usuario}")
            return make_response(jsonify({
                "message": "tipo_insignia no puede ser None o vacío",
                "status": 400
            }), 400)
        
        if not precio_insignia:
            logger.warning(f"precio_insignia vacío para usuario {id_usuario}")
            return make_response(jsonify({
                "message": "precio_insignia no puede ser None o vacío",
                "status": 400
            }), 400)

        estatus = Estatus.query.filter_by(id_usuario=id_usuario).first()
        if not estatus:
            logger.warning(f"Estatus no encontrado para verificar insignia - usuario: {id_usuario}")
            return make_response(jsonify({
                "message": "Estatus no encontrado",
                "status": 404
            }), 404)
        
        contador = 0
        
        if tipo_insignia == 1:  # Insignia por compra
            contador = estatus.n_compras
            logger.debug(f"Usuario {id_usuario} tiene {contador} compras")
        elif tipo_insignia == 2:  # Insignia por venta
            contador = estatus.n_ventas
            logger.debug(f"Usuario {id_usuario} tiene {contador} ventas")
        elif tipo_insignia == 3:  # Insignia por recurso educativo
            contador = estatus.n_rec_educativos
            logger.debug(f"Usuario {id_usuario} tiene {contador} recursos educativos")
        else:
            logger.warning(f"Tipo de insignia inválido ({tipo_insignia}) para usuario {id_usuario}")
        
        if contador >= precio_insignia:
            logger.info(f"Usuario {id_usuario} califica para insignia tipo {tipo_insignia} ({contador} >= {precio_insignia})")
            data = {
                "message": "Usuario califica para obtener la insignia",
                "status": 200
            }
            
            return make_response(jsonify(data), 200)
        
        else:
            logger.info(f"Usuario {id_usuario} NO califica para insignia tipo {tipo_insignia} ({contador} < {precio_insignia})")
            data = {
                "message": "Usuario no califica para obtener la insignia",
                "status": 400
            }

            return make_response(jsonify(data), 400)

    except Exception as err:
        logger.error(f"Error en verificar_puntos_insignias: {err}")  # Para debugging
        return make_response(jsonify({
            'status': 500,
            'message': 'Error procesando la solicitud'
        }), 500)
    

# VERIFICADOR DE PUNTOS STICKER
@estatus_routes.route("/verificar_puntos_sticker", methods=["POST"])
def verificar_puntos_sticker():
    try:
        required_fields = ['id_usuario', 'precio_sticker']
        if not request.json or not all(field in request.json for field in required_fields):
            return make_response(jsonify({
                "message": "id_usuario y precio_sticker son requeridos",
                "status": 400
            }), 400)

        id_usuario = request.json.get('id_usuario')
        precio_sticker = request.json.get('precio_sticker')

        # Validar que no sea None o vacío
        if not id_usuario:
            return make_response(jsonify({
                "message": "id_usuario no puede ser None o vacío",
                "status": 400
            }), 400)
        
        if not precio_sticker:
            return make_response(jsonify({
                "message": "precio_sticker no puede ser None o vacío",
                "status": 400
            }), 400)

        estatus = Estatus.query.filter_by(id_usuario=id_usuario).first()
        if not estatus:
            return make_response(jsonify({
                "message": "Estatus no encontrado",
                "status": 404
            }), 404)
        
        if estatus.ptos_sistema >= precio_sticker:
            estatus.ptos_sistema -= precio_sticker
            db.session.commit()
            data = {
                "message": "Usuario califica para obtener el sticker y se han descontado los puntos",
                "status": 200
            }

            return make_response(jsonify(data), 200)
        else:
            data = {
                "message": "Usuario no califica para obtener el sticker",
                "status": 400
            }

            return make_response(jsonify(data), 400)

    except Exception as err:
        logger.error(f"Error en verificar_puntos_sticker: {err}")  # Para debugging
        return make_response(jsonify({
            'status': 500,
            'message': 'Error procesando la solicitud'
        }), 500)


# AUMENTAR EXPERIENCIA (PUNTOS DEL SISTEMA)
@estatus_routes.route("/aumentar_experiencia", methods=["POST"])
def aumentar_experiencia():
    try:
        required_fields = ['id_usuario', 'motivo']
        if not request.json or not all(field in request.json for field in required_fields):
            return make_response(jsonify({
                "message": "id_usuario y motivo son requeridos",
                "status": 400
            }), 400)

        id_usuario = request.json.get('id_usuario')
        motivo = request.json.get('motivo')

        # Validar que no sean None o vacíos
        if not id_usuario:
            return make_response(jsonify({
                "message": "id_usuario no puede ser None o vacío",
                "status": 400
            }), 400)

        if motivo is None:
            return make_response(jsonify({
                "message": "motivo no puede ser None",
                "status": 400
            }), 400)

        estatus = Estatus.query.filter_by(id_usuario=id_usuario).first()
        if not estatus:
            return make_response(jsonify({
                "message": "Estatus no encontrado",
                "status": 404
            }), 404)
        

        if motivo == 1: # Desbloqueo de insignia
            estatus.ptos_sistema += 30
        elif motivo == 2: # Desbloqueo de certificado
            estatus.ptos_sistema += 50
        elif motivo == 3: # Desbloqueo de sticker 
            estatus.ptos_sistema += 5

        db.session.commit()

        data = {
            "message": "Puntos de experiencia aumentados exitosamente",
            "status": 200
        }

        return make_response(jsonify(data), 200)

    except Exception as err:
        logger.error(f"Error en aumentar_experiencia: {err}")  # Para debugging
        return make_response(jsonify({
            'status': 500,
            'message': 'Error procesando la solicitud'
        }), 500)