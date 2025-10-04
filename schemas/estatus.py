from utils.ma import ma
from marshmallow import fields

from models.estatus import Estatus

# SCHEMAS
class EstatusPerfilSchema(ma.SQLAlchemyAutoSchema):
    id_usuario = fields.Int()
    racha = fields.Int()
    ptos_sistema = fields.Int()

    class Meta:
        model = Estatus
        fields = (
            'id_usuario',
            'racha',
            'ptos_sistema'
        )
        load_instance = False

class EstatusContadoresSchema(ma.SQLAlchemyAutoSchema):
    n_compras = fields.Int()
    n_ventas = fields.Int()
    n_rec_educativos = fields.Int()
    
    class Meta:
        model = Estatus
        fields = (
            'n_compras',
            'n_ventas',
            'n_rec_educativos'
        )
        load_instance = False


# INSTANCIAS DE SCHEMAS
estatus_perfil_schema = EstatusPerfilSchema()
estatus_perfiles_schema = EstatusPerfilSchema(many=True)

estatus_contadores_schema = EstatusContadoresSchema()
estatus_contadores_varios_schema = EstatusContadoresSchema(many=True)