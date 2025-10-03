from utils.ma import ma

from models.estatus import Estatus

# SCHEMAS
class EstatusPerfilSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Estatus
        fields = (
            'id_usuario',
            'racha',
            'ptos_sistema'
        )

'''class EstatusLoginSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Estatus
        fields = (
            'id_usuario',
            'logeo_hoy'
        )
        '''

class EstatusContadoresSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Estatus
        fields = (
            'n_compras',
            'n_ventas',
            'n_rec_educativos'
        )

'''
class EstatusActividadSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Estatus
        fields = (
            'id_usuario',
            'activo_hoy'
        ) '''


# INSTANCIAS DE SCHEMAS
estatus_perfil_schema = EstatusPerfilSchema()
estatus_perfiles_schema = EstatusPerfilSchema(many=True)

#estatus_login_schema = EstatusLoginSchema()
#estatus_logins_schema = EstatusLoginSchema(many=True)

estatus_contadores_schema = EstatusContadoresSchema()
estatus_contadores_varios_schema = EstatusContadoresSchema(many=True)

#estatus_actividad_schema = EstatusActividadSchema()
#estatus_actividades_schema = EstatusActividadSchema(many=True)