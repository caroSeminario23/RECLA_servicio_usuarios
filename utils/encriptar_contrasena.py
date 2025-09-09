# ENCRIPTAR CONTRASEÑA
import bcrypt

def encriptar_contrasena(contrasena):
    contrasena_bytes = contrasena.encode('utf-8')
    salt = bcrypt.gensalt() # Convierte la cadena en bytes
    contrasena_encriptada = bcrypt.hashpw(contrasena_bytes, salt) # Asegura contraseña única
    return contrasena_encriptada.decode('utf-8') # Encripta la contraseña

def verificar_contrasena(contrasena, contrasena_encriptada):
    contrasena_bytes = contrasena.encode('utf-8')
    contrasena_encriptada_bytes = contrasena_encriptada.encode('utf-8')
    return bcrypt.checkpw(contrasena_bytes, contrasena_encriptada_bytes) # Verifica la contraseña