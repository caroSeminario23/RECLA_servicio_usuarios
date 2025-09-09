from utils.ma import ma
from marshmallow import fields, validates, ValidationError

from models.usuario import Usuario


# VALIDACIONES
class BaseUsuarioSchema(ma.SQLAlchemyAutoSchema):
    @validates("email")
    def validate_email(self, value):
        if "@" not in value:
            raise ValidationError("Email inválido")

    @validates("username")
    def validate_username(self, value):
        if not 5 <= len(value) <= 20:
            raise ValidationError("El username debe tener entre 5 y 20 caracteres")

    @validates("contrasena")
    def validate_contrasena(self, value):
        if len(value) != 6:
            raise ValidationError("La contraseña debe tener 6 caracteres")

    class Meta:
        model = Usuario
        load_instance = True


# SCHEMAS
class UsuarioRegistroSchema(BaseUsuarioSchema):
    class Meta(BaseUsuarioSchema.Meta):
        fields = (
            'email',
            'contrasena',
            'fec_nac',
            'username'
        )


class UsuarioLoginRequestSchema(BaseUsuarioSchema):
    class Meta(BaseUsuarioSchema.Meta):
        fields = (
            'email',
            'contrasena'
        )


class UsuarioLoginResponseSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Usuario
        fields = (
            'id_usuario',
            'username'
        )


class EmailValidacionSchema(BaseUsuarioSchema):
    class Meta(BaseUsuarioSchema.Meta):
        fields = ('email',)
        

class UsernameValidacionSchema(BaseUsuarioSchema):
    class Meta(BaseUsuarioSchema.Meta):
        fields = ('username',)


# INSTANCIAS DE SCHEMAS
usuario_registro_schema = UsuarioRegistroSchema()
usuarios_registro_schema = UsuarioRegistroSchema(many=True)

usuario_login_request_schema = UsuarioLoginRequestSchema()
usuarios_login_request_schema = UsuarioLoginRequestSchema(many=True)

usuario_login_response_schema = UsuarioLoginResponseSchema()
usuarios_login_response_schema = UsuarioLoginResponseSchema(many=True)

email_validacion_schema = EmailValidacionSchema()
emails_validacion_schema = EmailValidacionSchema(many=True)

username_validacion_schema = UsernameValidacionSchema()
usernames_validacion_schema = UsernameValidacionSchema(many=True)