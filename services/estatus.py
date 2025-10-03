from flask import Blueprint, request, jsonify, make_response

from utils.db import db
from models.estatus import Estatus
from models.usuario import Usuario
from schemas.estatus import (estatus_perfil_schema,
                             estatus_contadores_schema)

estatus_routes = Blueprint("estatus_routes", __name__)

# MOSTRAR ESTATUS DE PERFIL
@estatus_routes.route("/estatus_perfil", methods=["POST"])
def mostrar_estatus_perfil():
    try:
        required_fields = ['id_usuario']
        if not request.json or not all(field in request.json for field in required_fields):
            return make_response(jsonify({
                "message": "id_usuario es requerido",
                "status": 400
            }), 400)
        
        id_usuario = request.json.get('id_usuario')

        # Validar que no sea None o vacío
        if not id_usuario:
            return make_response(jsonify({
                "message": "id_usuario no puede ser None o vacío",
                "status": 400
            }), 400)
        
        estatus = Estatus.query.filter_by(id_usuario=id_usuario).first()
        if not estatus:
            return make_response(jsonify({
                "message": "Estatus no encontrado",
                "status": 404
            }), 404)
        
        resultado = estatus_perfil_schema.dump(estatus)

        data = {
            "message": "Estatus de perfil obtenido exitosamente",
            "status": 200,
            "data": resultado
        }

        return make_response(jsonify(data), 200)
    
    except Exception as err:
        print(f"Error en mostrar_estatus_perfil: {err}")  # Para debugging
        return make_response(jsonify({
            'status': 500,
            'message': 'Error procesando la solicitud'
        }), 500)
    

# MOSTRAR ESTATUS DE CONTADORES
@estatus_routes.route("/estatus_contadores", methods=["POST"])
def mostrar_estatus_contadores():
    try:
        required_fields = ['id_usuario']
        if not request.json or not all(field in request.json for field in required_fields):
            return make_response(jsonify({
                "message": "id_usuario es requerido",
                "status": 400
            }), 400)

        id_usuario = request.json.get('id_usuario')

        # Validar que no sea None o vacío
        if not id_usuario:
            return make_response(jsonify({
                "message": "id_usuario no puede ser None o vacío",
                "status": 400
            }), 400)

        estatus = Estatus.query.filter_by(id_usuario=id_usuario).first()
        if not estatus:
            return make_response(jsonify({
                "message": "Estatus no encontrado",
                "status": 404
            }), 404)

        resultado = estatus_contadores_schema.dump(estatus)

        data = {
            "message": "Estatus de contadores obtenido exitosamente",
            "status": 200,
            "data": resultado
        }

        return make_response(jsonify(data), 200)

    except Exception as err:
        print(f"Error en mostrar_estatus_contadores: {err}")  # Para debugging
        return make_response(jsonify({
            'status': 500,
            'message': 'Error procesando la solicitud'
        }), 500)


# REGISTRAR ACTIVIDAD DIARIA
@estatus_routes.route("/registrar_actividad", methods=["POST"])
def registrar_actividad():
    try:
        required_fields = ['id_usuario']
        if not request.json or not all(field in request.json for field in required_fields):
            return make_response(jsonify({
                "message": "id_usuario es requerido",
                "status": 400
            }), 400)

        id_usuario = request.json.get('id_usuario')

        # Validar que no sean None o vacíos
        if not id_usuario:
            return make_response(jsonify({
                "message": "id_usuario no puede ser None o vacío",
                "status": 400
            }), 400)

        estatus = Estatus.query.filter_by(id_usuario=id_usuario).first()
        if not estatus:
            return make_response(jsonify({
                "message": "Estatus no encontrado",
                "status": 404
            }), 404)
        
        if estatus.activo_hoy == False:
            estatus.activo_hoy = True
            db.session.commit()

        data = {
            "message": "Actividad registrada exitosamente",
            "status": 201
        }

        return make_response(jsonify(data), 201)

    except Exception as err:
        print(f"Error en registrar_actividad: {err}")  # Para debugging
        return make_response(jsonify({
            'status': 500,
            'message': 'Error procesando la solicitud'
        }), 500)
    

# VERIFICADOR DE PUNTOS INSIGNIA
@estatus_routes.route("/verificar_puntos_insignias", methods=["POST"])
def verificar_puntos_insignias():
    try:
        required_fields = ['id_usuario', 'tipo_insignia', 'precio_insignia']
        if not request.json or not all(field in request.json for field in required_fields):
            return make_response(jsonify({
                "message": "id_usuario, tipo_insignia y precio_insignia son requeridos",
                "status": 400
            }), 400)

        id_usuario = request.json.get('id_usuario')
        tipo_insignia = request.json.get('tipo_insignia')
        precio_insignia = request.json.get('precio_insignia')

        # Validar que no sea None o vacío
        if not id_usuario:
            return make_response(jsonify({
                "message": "id_usuario no puede ser None o vacío",
                "status": 400
            }), 400)
        
        if not tipo_insignia:
            return make_response(jsonify({
                "message": "tipo_insignia no puede ser None o vacío",
                "status": 400
            }), 400)
        
        if not precio_insignia:
            return make_response(jsonify({
                "message": "precio_insignia no puede ser None o vacío",
                "status": 400
            }), 400)

        estatus = Estatus.query.filter_by(id_usuario=id_usuario).first()
        if not estatus:
            return make_response(jsonify({
                "message": "Estatus no encontrado",
                "status": 404
            }), 404)
        
        contador = 0
        
        if tipo_insignia == 1:  # Insignia por compra
            contador = estatus.n_compras
        elif tipo_insignia == 2:  # Insignia por venta
            contador = estatus.n_ventas
        elif tipo_insignia == 3:  # Insignia por recurso educativo
            contador = estatus.n_rec_educativos
        
        if contador >= precio_insignia:
            data = {
                "message": "Usuario califica para obtener la insignia",
                "status": 200
            }

            return make_response(jsonify(data), 200)
        else:
            data = {
                "message": "Usuario no califica para obtener la insignia",
                "status": 400
            }

            return make_response(jsonify(data), 400)

    except Exception as err:
        print(f"Error en verificar_puntos_insignias: {err}")  # Para debugging
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
            data = {
                "message": "Usuario califica para obtener el sticker",
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
        print(f"Error en verificar_puntos_sticker: {err}")  # Para debugging
        return make_response(jsonify({
            'status': 500,
            'message': 'Error procesando la solicitud'
        }), 500)
