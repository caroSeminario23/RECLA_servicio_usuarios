from flask import Blueprint, request, jsonify, make_response
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError

from utils.db import db
from schemas.usuario_clasificacion import usuarios_clasificacion_schema

tabla_clasificacion_routes = Blueprint("tabla_clasificacion_routes", __name__)


# OBTENER TABLA DE CLASIFICACIÓN
@tabla_clasificacion_routes.route("/get_tabla_clasificacion", methods=["GET"])
def get_tabla_clasificacion():
    consulta_clasificacion = """
    SELECT
        ROW_NUMBER() OVER (ORDER BY COALESCE(E.ptos_sistema,0) DESC) AS posicion,
        U.id_usuario,
        U.username,
        E.ptos_sistema
    FROM USUARIO as U
    LEFT JOIN ESTATUS as E
        ON U.id_usuario = E.id_usuario
    ORDER BY E.ptos_sistema DESC
    LIMIT 8;
    """

    usuario_clasificacion = db.session.execute(text(consulta_clasificacion))
    resultado_raw = usuario_clasificacion.mappings().all()
    #resultado_raw = [dict(row) for row in usuario_clasificacion]
    resultado = usuarios_clasificacion_schema.dump(resultado_raw)

    data = {
        "message": "Tabla de clasificación obtenida exitosamente",
        "status": 200,
        "data": resultado
    }

    return make_response(jsonify(data), 200)
