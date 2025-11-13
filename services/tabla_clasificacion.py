from flask import Blueprint, request, jsonify, make_response
from sqlalchemy import text
import time

from utils.db import db
from utils.logger import get_logger
from schemas.usuario_clasificacion import usuarios_clasificacion_schema

# Configurar el logger
logger = get_logger(__name__)

tabla_clasificacion_routes = Blueprint("tabla_clasificacion_routes", __name__)


# OBTENER TABLA DE CLASIFICACIÓN
@tabla_clasificacion_routes.route("/get_tabla_clasificacion", methods=["GET"])
def get_tabla_clasificacion():
    inicio_tiempo = time.time()

    try:
        logger.info("Solicitud para obtener tabla de clasificación recibida")

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

        logger.debug("Ejecutando consulta de tabla de clasificación")
        usuario_clasificacion = db.session.execute(text(consulta_clasificacion))
        resultado_raw = usuario_clasificacion.mappings().all()
        #resultado_raw = [dict(row) for row in usuario_clasificacion]

        logger.debug(f"Consulta ejecutada exitosamente. Registros obtenidos: {len(resultado_raw)}")
        resultado = usuarios_clasificacion_schema.dump(resultado_raw)

        tiempo_respuesta = time.time() - inicio_tiempo
        logger.info(f"Tabla de clasificación obtenida exitosamente. Usuarios en ranking: {len(resultado)}. Tiempo: {tiempo_respuesta:.3f}s")

        data = {
            "message": "Tabla de clasificación obtenida exitosamente",
            "status": 200,
            "data": resultado
        }

        return make_response(jsonify(data), 200)

    except Exception as err:
        tiempo_respuesta = time.time() - inicio_tiempo
        logger.error(f"Error en get_tabla_clasificacion: {err}. Tiempo: {tiempo_respuesta:.3f}s")
        return make_response(jsonify({
            'status': 500,
            'message': 'Error procesando la solicitud'
        }), 500)
