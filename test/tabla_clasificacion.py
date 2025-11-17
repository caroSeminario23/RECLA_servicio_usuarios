import unittest
import requests
import concurrent.futures
import time
import random

class TestTablaClasificacionCarga(unittest.TestCase):
    """
    Pruebas de carga para el servicio de obtención de tabla de clasificación
    """
    
    BASE_URL = "http://localhost:5000/tabla_clasificacion_routes"
    ENDPOINT_TABLA_CLASIFICACION = f"{BASE_URL}/get_tabla_clasificacion"
    
    @staticmethod
    def obtener_tabla_clasificacion_individual(url, numero_intento):
        """Obtiene la tabla de clasificación individual y retorna el resultado"""
        try:
            inicio = time.time()
            respuesta = requests.get(url, timeout=10)
            tiempo_respuesta = time.time() - inicio
            
            return {
                "intento": numero_intento,
                "status_code": respuesta.status_code,
                "tiempo_respuesta": tiempo_respuesta,
                "respuesta": respuesta.json(),
                "exito": respuesta.status_code == 200,
                "error": None,
                "cantidad_registros": len(respuesta.json().get("data", []))
            }
        except Exception as e:
            inicio = time.time()
            tiempo_respuesta = time.time() - inicio
            return {
                "intento": numero_intento,
                "status_code": None,
                "tiempo_respuesta": tiempo_respuesta,
                "respuesta": None,
                "exito": False,
                "error": str(e),
                "cantidad_registros": 0
            }
    
    def simular_obtenciones_simultaneas(self, cantidad_usuarios):
        """
        Simula la obtención de tabla de clasificación por múltiples usuarios de forma simultánea
        
        Args:
            cantidad_usuarios (int): Cantidad de usuarios concurrentes (1-20)
        
        Returns:
            dict: Estadísticas del test de carga
        """
        
        if not (1 <= cantidad_usuarios <= 20):
            raise ValueError("La cantidad de usuarios debe estar entre 1 y 20")
        
        print(f"\n{'='*70}")
        print(f"INICIANDO TEST DE CARGA: {cantidad_usuarios} obtenciones simultáneas")
        print(f"Endpoint: GET {self.ENDPOINT_TABLA_CLASIFICACION}")
        print(f"{'='*70}\n")
        
        # Ejecutar obtenciones en paralelo
        tiempo_inicio_total = time.time()
        resultados = []
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=cantidad_usuarios) as executor:
            futures = [
                executor.submit(
                    self.obtener_tabla_clasificacion_individual,
                    self.ENDPOINT_TABLA_CLASIFICACION,
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
        
        # Obtener información sobre los datos retornados
        registros_totales = sum(r["cantidad_registros"] for r in resultados if r["exito"])
        registros_promedio = registros_totales / exitosos if exitosos > 0 else 0
        
        # Mostrar resultados
        self._mostrar_resultados(
            cantidad_usuarios, exitosos, fallidos, 
            tiempo_total, tiempo_promedio, tiempo_maximo, 
            tiempo_minimo, registros_promedio, resultados
        )
        
        return {
            "cantidad_usuarios": cantidad_usuarios,
            "exitosos": exitosos,
            "fallidos": fallidos,
            "tiempo_total": tiempo_total,
            "tiempo_promedio": tiempo_promedio,
            "tiempo_maximo": tiempo_maximo,
            "tiempo_minimo": tiempo_minimo,
            "registros_promedio": registros_promedio,
            "resultados_detallados": resultados
        }
    
    @staticmethod
    def _mostrar_resultados(cantidad, exitosos, fallidos, tiempo_total, 
                            tiempo_promedio, tiempo_maximo, tiempo_minimo, 
                            registros_promedio, resultados):
        """Muestra los resultados en formato legible"""
        print(f"RESUMEN DE RESULTADOS:")
        print(f"-" * 70)
        print(f"Total de intentos:        {cantidad}")
        print(f"Obtenciones exitosas:     {exitosos} ✓")
        print(f"Obtenciones fallidas:     {fallidos} ✗")
        print(f"Tasa de éxito:            {(exitosos/cantidad)*100:.1f}%")
        print(f"\nDATOS RETORNADOS:")
        print(f"-" * 70)
        print(f"Registros promedio/req:   {registros_promedio:.1f}")
        print(f"\nTIEMPOS DE RESPUESTA:")
        print(f"-" * 70)
        print(f"Tiempo total:             {tiempo_total:.3f}s")
        print(f"Tiempo promedio/request:  {tiempo_promedio:.3f}s")
        print(f"Tiempo máximo:            {tiempo_maximo:.3f}s")
        print(f"Tiempo mínimo:            {tiempo_minimo:.3f}s")
        print(f"\nDETALLES POR INTENTO:")
        print(f"-" * 70)
        
        for resultado in sorted(resultados, key=lambda x: x["intento"]):
            estado = "✓" if resultado["exito"] else "✗"
            registros = resultado["cantidad_registros"]
            print(f"Intento {resultado['intento']:2d}: {estado} | "
                  f"Status: {resultado['status_code'] or 'ERROR':>3} | "
                  f"Registros: {registros:2d} | "
                  f"Tiempo: {resultado['tiempo_respuesta']:.3f}s", end="")
            if resultado["error"]:
                print(f" | Error: {resultado['error']}")
            else:
                print()
        
        print(f"{'='*70}\n")
    
    def test_1_usuario(self):
        """Test con 1 usuario"""
        resultado = self.simular_obtenciones_simultaneas(1)
        self.assertEqual(resultado["exitosos"], 1)
    
    def test_5_usuarios(self):
        """Test con 5 usuarios"""
        resultado = self.simular_obtenciones_simultaneas(5)
        self.assertGreaterEqual(resultado["exitosos"], 4)
    
    def test_10_usuarios(self):
        """Test con 10 usuarios"""
        resultado = self.simular_obtenciones_simultaneas(10)
        self.assertGreaterEqual(resultado["exitosos"], 8)

    def test_15_usuarios(self):
        """Test con 15 usuarios"""
        resultado = self.simular_obtenciones_simultaneas(15)
        self.assertGreaterEqual(resultado["exitosos"], 12)
    
    def test_20_usuarios(self):
        """Test con 20 usuarios (máximo)"""
        resultado = self.simular_obtenciones_simultaneas(20)
        self.assertGreaterEqual(resultado["exitosos"], 15)


if __name__ == "__main__":
    # Ejecutar pruebas
    unittest.main(verbosity=2)
    
    # O ejecutar directamente sin unittest:
    # test = TestTablaClasificacionCarga()
    # test.simular_obtenciones_simultaneas(10)