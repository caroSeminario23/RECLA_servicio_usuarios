import unittest
import requests
import concurrent.futures
import time
from datetime import date
import random
import string

class TestRegistroEcoaprendizCarga(unittest.TestCase):
    """
    Pruebas de carga para el servicio de registro de ecoaprendiz
    """
    
    BASE_URL = "http://localhost:5000/usuario_routes"  # Ajusta según tu configuración
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
    def registrar_usuario_individual(url, datos_usuario, numero_intento):
        """Registra un usuario individual y retorna el resultado"""
        try:
            inicio = time.time()
            respuesta = requests.post(url, json=datos_usuario, timeout=10)
            tiempo_respuesta = time.time() - inicio
            
            return {
                "intento": numero_intento,
                "status_code": respuesta.status_code,
                "tiempo_respuesta": tiempo_respuesta,
                "respuesta": respuesta.json(),
                "exito": respuesta.status_code == 201,
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
    
    def simular_registros_simultaneos(self, cantidad_usuarios):
        """
        Simula el registro de múltiples usuarios de forma simultánea
        
        Args:
            cantidad_usuarios (int): Cantidad de usuarios a registrar (1-20)
        
        Returns:
            dict: Estadísticas del test de carga
        """
        
        if not (1 <= cantidad_usuarios <= 20):
            raise ValueError("La cantidad de usuarios debe estar entre 1 y 20")
        
        print(f"\n{'='*70}")
        print(f"INICIANDO TEST DE CARGA: {cantidad_usuarios} usuarios simultáneos")
        print(f"{'='*70}\n")
        
        # Generar datos para los usuarios
        usuarios = [self.generar_usuario_aleatorio() for _ in range(cantidad_usuarios)]
        
        # Ejecutar registros en paralelo
        tiempo_inicio_total = time.time()
        resultados = []
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=cantidad_usuarios) as executor:
            futures = [
                executor.submit(
                    self.registrar_usuario_individual,
                    self.ENDPOINT_REGISTRO,
                    usuarios[i],
                    i + 1
                )
                for i in range(cantidad_usuarios)
            ]
            
            for future in concurrent.futures.as_completed(futures):
                resultados.append(future.result())
        
        tiempo_total = time.time() - tiempo_inicio_total
        
        # Procesar estadísticas
        exitosos = sum(1 for r in resultados if r["exito"])
        fallidos = cantidad_usuarios - exitosos
        tiempo_promedio = sum(r["tiempo_respuesta"] for r in resultados) / cantidad_usuarios
        tiempo_maximo = max(r["tiempo_respuesta"] for r in resultados)
        tiempo_minimo = min(r["tiempo_respuesta"] for r in resultados)
        
        # Mostrar resultados
        self._mostrar_resultados(
            cantidad_usuarios, exitosos, fallidos, 
            tiempo_total, tiempo_promedio, tiempo_maximo, 
            tiempo_minimo, resultados
        )
        
        return {
            "cantidad_usuarios": cantidad_usuarios,
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
        print(f"Registros exitosos:       {exitosos} ✓")
        print(f"Registros fallidos:       {fallidos} ✗")
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
        resultado = self.simular_registros_simultaneos(1)
        self.assertEqual(resultado["exitosos"], 1)
    
    def test_5_usuarios(self):
        """Test con 5 usuarios"""
        resultado = self.simular_registros_simultaneos(5)
        self.assertGreaterEqual(resultado["exitosos"], 4)
    
    def test_10_usuarios(self):
        """Test con 10 usuarios"""
        resultado = self.simular_registros_simultaneos(10)
        self.assertGreaterEqual(resultado["exitosos"], 8)

    def test_15_usuarios(self):
        """Test con 15 usuarios"""
        resultado = self.simular_registros_simultaneos(15)
        self.assertGreaterEqual(resultado["exitosos"], 12)
    
    def test_20_usuarios(self):
        """Test con 20 usuarios (máximo)"""
        resultado = self.simular_registros_simultaneos(20)
        self.assertGreaterEqual(resultado["exitosos"], 15)


if __name__ == "__main__":
    # Ejecutar pruebas
    unittest.main(verbosity=2)
    
    # O ejecutar directamente sin unittest:
    # test = TestRegistroEcoaprendizCarga()
    # test.simular_registros_simultaneos(10)