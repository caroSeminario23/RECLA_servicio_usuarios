import unittest
import requests
import concurrent.futures
import time
from datetime import date
import random
import string

class TestLoginEcoaprendizCarga(unittest.TestCase):
    """
    Pruebas de carga para el servicio de login de ecoaprendiz
    """
    
    BASE_URL = "http://localhost:5000/usuario_routes"
    ENDPOINT_LOGIN = f"{BASE_URL}/login_ecoaprendiz"
    ENDPOINT_REGISTRO = f"{BASE_URL}/registro_ecoaprendiz"
    
    @staticmethod
    def generar_usuario_aleatorio():
        """Genera datos aleatorios para un usuario único"""
        random_suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
        return {
            "email": f"usuario_{random_suffix}@test.com",
            "username": f"user_{random_suffix}",
            "contrasena": "123456",
            "fec_nac": "1990-01-15"
        }
    
    @staticmethod
    def registrar_usuario_previo(url_registro, datos_usuario):
        """Registra un usuario previo al test de login"""
        try:
            respuesta = requests.post(url_registro, json=datos_usuario, timeout=10)
            if respuesta.status_code == 201:
                return True
            return False
        except Exception as e:
            print(f"Error al registrar usuario previo: {e}")
            return False
    
    @staticmethod
    def realizar_login_individual(url, credenciales_login, numero_intento):
        """Realiza un login individual y retorna el resultado"""
        try:
            inicio = time.time()
            respuesta = requests.post(url, json=credenciales_login, timeout=10)
            tiempo_respuesta = time.time() - inicio
            
            return {
                "intento": numero_intento,
                "status_code": respuesta.status_code,
                "tiempo_respuesta": tiempo_respuesta,
                "respuesta": respuesta.json(),
                "exito": respuesta.status_code == 200,
                "error": None
            }
        except Exception as e:
            tiempo_respuesta = time.time() - inicio
            return {
                "intento": numero_intento,
                "status_code": None,
                "tiempo_respuesta": tiempo_respuesta,
                "respuesta": None,
                "exito": False,
                "error": str(e)
            }
    
    def simular_logins_simultaneos(self, cantidad_usuarios):
        """
        Simula el login de múltiples usuarios de forma simultánea
        
        Args:
            cantidad_usuarios (int): Cantidad de usuarios a loguear (1-20)
        
        Returns:
            dict: Estadísticas del test de carga
        """
        
        if not (1 <= cantidad_usuarios <= 20):
            raise ValueError("La cantidad de usuarios debe estar entre 1 y 20")
        
        print(f"\n{'='*70}")
        print(f"INICIANDO TEST DE CARGA: {cantidad_usuarios} logins simultáneos")
        print(f"{'='*70}\n")
        
        # Paso 1: Generar y registrar usuarios previos
        print("Registrando usuarios previos...")
        usuarios = []
        credenciales_login = []
        
        for i in range(cantidad_usuarios):
            usuario_data = self.generar_usuario_aleatorio()
            usuarios.append(usuario_data)
            
            # Registrar el usuario
            if self.registrar_usuario_previo(self.ENDPOINT_REGISTRO, usuario_data):
                # Preparar credenciales de login
                credenciales_login.append({
                    "email": usuario_data["email"],
                    "contrasena": usuario_data["contrasena"]
                })
            else:
                print(f"⚠ Advertencia: No se pudo registrar usuario {i+1}")
        
        print(f"✓ {len(credenciales_login)} usuarios registrados exitosamente\n")
        
        # Paso 2: Ejecutar logins en paralelo
        print("Iniciando logins simultáneos...")
        tiempo_inicio_total = time.time()
        resultados = []
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=cantidad_usuarios) as executor:
            futures = [
                executor.submit(
                    self.realizar_login_individual,
                    self.ENDPOINT_LOGIN,
                    credenciales_login[i],
                    i + 1
                )
                for i in range(len(credenciales_login))
            ]
            
            for future in concurrent.futures.as_completed(futures):
                resultados.append(future.result())
        
        tiempo_total = time.time() - tiempo_inicio_total
        
        # Procesar estadísticas
        exitosos = sum(1 for r in resultados if r["exito"])
        fallidos = len(resultados) - exitosos
        tiempo_promedio = sum(r["tiempo_respuesta"] for r in resultados) / len(resultados) if resultados else 0
        tiempo_maximo = max(r["tiempo_respuesta"] for r in resultados) if resultados else 0
        tiempo_minimo = min(r["tiempo_respuesta"] for r in resultados) if resultados else 0
        
        # Mostrar resultados
        self._mostrar_resultados(
            len(resultados), exitosos, fallidos, 
            tiempo_total, tiempo_promedio, tiempo_maximo, 
            tiempo_minimo, resultados
        )
        
        return {
            "cantidad_usuarios": len(resultados),
            "exitosos": exitosos,
            "fallidos": fallidos,
            "tiempo_total": tiempo_total,
            "tiempo_promedio": tiempo_promedio,
            "tiempo_maximo": tiempo_maximo,
            "tiempo_minimo": tiempo_minimo,
            "resultados_detallados": resultados
        }
    
    @staticmethod
    def _mostrar_resultados(cantidad, exitosos, fallidos, tiempo_total, 
                            tiempo_promedio, tiempo_maximo, tiempo_minimo, resultados):
        """Muestra los resultados en formato legible"""
        print(f"RESUMEN DE RESULTADOS:")
        print(f"-" * 70)
        print(f"Total de intentos:        {cantidad}")
        print(f"Logins exitosos:          {exitosos} ✓")
        print(f"Logins fallidos:          {fallidos} ✗")
        print(f"Tasa de éxito:            {(exitosos/cantidad)*100:.1f}%")
        print(f"\nTIEMPOS DE RESPUESTA:")
        print(f"-" * 70)
        print(f"Tiempo total:             {tiempo_total:.3f}s")
        print(f"Tiempo promedio/usuario:  {tiempo_promedio:.3f}s")
        print(f"Tiempo máximo:            {tiempo_maximo:.3f}s")
        print(f"Tiempo mínimo:            {tiempo_minimo:.3f}s")
        print(f"\nDETALLES POR INTENTO:")
        print(f"-" * 70)
        
        for resultado in sorted(resultados, key=lambda x: x["intento"]):
            estado = "✓" if resultado["exito"] else "✗"
            print(f"Intento {resultado['intento']:2d}: {estado} | "
                  f"Status: {resultado['status_code'] or 'ERROR':>3} | "
                  f"Tiempo: {resultado['tiempo_respuesta']:.3f}s", end="")
            if resultado["error"]:
                print(f" | Error: {resultado['error']}")
            else:
                print()
        
        print(f"{'='*70}\n")
    
    def test_1_usuario(self):
        """Test con 1 usuario"""
        resultado = self.simular_logins_simultaneos(1)
        self.assertEqual(resultado["exitosos"], 1)
    
    def test_5_usuarios(self):
        """Test con 5 usuarios"""
        resultado = self.simular_logins_simultaneos(5)
        self.assertGreaterEqual(resultado["exitosos"], 4)
    
    def test_10_usuarios(self):
        """Test con 10 usuarios"""
        resultado = self.simular_logins_simultaneos(10)
        self.assertGreaterEqual(resultado["exitosos"], 8)

    def test_15_usuarios(self):
        """Test con 15 usuarios"""
        resultado = self.simular_logins_simultaneos(15)
        self.assertGreaterEqual(resultado["exitosos"], 12)
    
    def test_20_usuarios(self):
        """Test con 20 usuarios (máximo)"""
        resultado = self.simular_logins_simultaneos(20)
        self.assertGreaterEqual(resultado["exitosos"], 15)


if __name__ == "__main__":
    # Ejecutar pruebas
    unittest.main(verbosity=2)
    
    # O ejecutar directamente sin unittest:
    # test = TestLoginEcoaprendizCarga()
    # test.simular_logins_simultaneos(10)