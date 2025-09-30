from flask import Blueprint, request, jsonify, make_response
from marshmallow import ValidationError
from sqlalchemy.exc import IntegrityError

from utils.db import db
from models.estatus import Estatus
from schemas.estatus import (estatus_perfil_schema,
                             estatus_contadores_schema,
                             estatus_actividad_schema)

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

        # Aquí se registraría la actividad en la base de datos
        # ...

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
