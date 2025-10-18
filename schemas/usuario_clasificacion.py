from utils.ma import ma
from marshmallow import fields

class UsuarioClasificacionSchema(ma.Schema):
    class Meta:
        fields = (
            "posicion",
            "id_usuario",
            "username",
            "ptos_sistema"
        )

    posicion = fields.Int()
    id_usuario = fields.Int()
    username = fields.Str()
    ptos_sistema = fields.Int()


# INSTANCIAS DE SCHEMAS
usuario_clasificacion_schema = UsuarioClasificacionSchema()
usuarios_clasificacion_schema = UsuarioClasificacionSchema(many=True)