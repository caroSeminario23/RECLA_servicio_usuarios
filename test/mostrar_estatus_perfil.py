import unittest
import requests
import concurrent.futures
import time
import random

class TestMostrarEstatusPerfil(unittest.TestCase):
    """
    Pruebas de carga para el servicio de obtención de estatus de perfil
    """
    
    BASE_URL = "http://localhost:5000/estatus_routes"
    ENDPOINT_ESTATUS_PERFIL = f"{BASE_URL}/estatus_perfil"
    
    # Rango de IDs de usuarios existentes en la base de datos
    ID_USUARIOS_INICIO = 1
    ID_USUARIOS_FIN = 100
    
    @staticmethod
    def obtener_id_usuario_aleatorio():
        """Genera un ID de usuario aleatorio existente"""
        return random.randint(
            TestMostrarEstatusPerfil.ID_USUARIOS_INICIO,
            TestMostrarEstatusPerfil.ID_USUARIOS_FIN
        )
    
    @staticmethod
    def obtener_estatus_perfil_individual(url, id_usuario, numero_intento):
        """Obtiene el estatus de perfil de un usuario individual y retorna el resultado"""
        try:
            inicio = time.time()
            datos_request = {
                "id_usuario": id_usuario
            }
            respuesta = requests.post(url, json=datos_request, timeout=10)
            tiempo_respuesta = time.time() - inicio
            
            return {
                "intento": numero_intento,
                "id_usuario": id_usuario,
                "status_code": respuesta.status_code,
                "tiempo_respuesta": tiempo_respuesta,
                "respuesta": respuesta.json(),
                "exito": respuesta.status_code == 200,
                "error": None,
                "racha": respuesta.json().get("data", {}).get("racha") if respuesta.status_code == 200 else None,
                "ptos_sistema": respuesta.json().get("data", {}).get("ptos_sistema") if respuesta.status_code == 200 else None
            }
        except Exception as e:
            tiempo_respuesta = time.time() - inicio
            return {
                "intento": numero_intento,
                "id_usuario": id_usuario,
                "status_code": None,
                "tiempo_respuesta": tiempo_respuesta,
                "respuesta": None,
                "exito": False,
                "error": str(e),
                "racha": None,
                "ptos_sistema": None
            }
    
    def simular_obtenciones_estatus_simultaneas(self, cantidad_usuarios):
        """
        Simula la obtención de estatus de perfil por múltiples usuarios de forma simultánea
        
        Args:
            cantidad_usuarios (int): Cantidad de usuarios concurrentes (1-20)
        
        Returns:
            dict: Estadísticas del test de carga
        """
        
        if not (1 <= cantidad_usuarios <= 20):
            raise ValueError("La cantidad de usuarios debe estar entre 1 y 20")
        
        print(f"\n{'='*70}")
        print(f"INICIANDO TEST DE CARGA: {cantidad_usuarios} obtenciones de estatus simultáneas")
        print(f"Endpoint: POST {self.ENDPOINT_ESTATUS_PERFIL}")
        print(f"{'='*70}\n")
        
        # Generar IDs de usuarios aleatorios
        ids_usuarios = [self.obtener_id_usuario_aleatorio() for _ in range(cantidad_usuarios)]
        
        # Ejecutar obtenciones en paralelo
        tiempo_inicio_total = time.time()
        resultados = []
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=cantidad_usuarios) as executor:
            futures = [
                executor.submit(
                    self.obtener_estatus_perfil_individual,
                    self.ENDPOINT_ESTATUS_PERFIL,
                    ids_usuarios[i],
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
        racha_promedio = sum(r["racha"] for r in resultados if r["racha"] is not None) / exitosos if exitosos > 0 else 0
        ptos_promedio = sum(r["ptos_sistema"] for r in resultados if r["ptos_sistema"] is not None) / exitosos if exitosos > 0 else 0
        
        # Mostrar resultados
        self._mostrar_resultados(
            cantidad_usuarios, exitosos, fallidos, 
            tiempo_total, tiempo_promedio, tiempo_maximo, 
            tiempo_minimo, racha_promedio, ptos_promedio, resultados
        )
        
        return {
            "cantidad_usuarios": cantidad_usuarios,
            "exitosos": exitosos,
            "fallidos": fallidos,
            "tiempo_total": tiempo_total,
            "tiempo_promedio": tiempo_promedio,
            "tiempo_maximo": tiempo_maximo,
            "tiempo_minimo": tiempo_minimo,
            "racha_promedio": racha_promedio,
            "ptos_promedio": ptos_promedio,
            "resultados_detallados": resultados
        }
    
    @staticmethod
    def _mostrar_resultados(cantidad, exitosos, fallidos, tiempo_total, 
                            tiempo_promedio, tiempo_maximo, tiempo_minimo, 
                            racha_promedio, ptos_promedio, resultados):
        """Muestra los resultados en formato legible"""
        print(f"RESUMEN DE RESULTADOS:")
        print(f"-" * 70)
        print(f"Total de intentos:        {cantidad}")
        print(f"Obtenciones exitosas:     {exitosos} ✓")
        print(f"Obtenciones fallidas:     {fallidos} ✗")
        print(f"Tasa de éxito:            {(exitosos/cantidad)*100:.1f}%")
        print(f"\nDATOS RETORNADOS:")
        print(f"-" * 70)
        print(f"Racha promedio:           {racha_promedio:.1f}")
        print(f"Puntos sistema promedio:  {ptos_promedio:.1f}")
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
            usuario_info = f"U:{resultado['id_usuario']}"
            racha_info = f"R:{resultado['racha']}" if resultado["racha"] is not None else "R:N/A"
            ptos_info = f"P:{resultado['ptos_sistema']}" if resultado["ptos_sistema"] is not None else "P:N/A"
            
            print(f"Intento {resultado['intento']:2d}: {estado} | "
                  f"Status: {resultado['status_code'] or 'ERROR':>3} | "
                  f"{usuario_info:>6} | {racha_info:>5} | {ptos_info:>6} | "
                  f"Tiempo: {resultado['tiempo_respuesta']:.3f}s", end="")
            if resultado["error"]:
                print(f" | Error: {resultado['error']}")
            else:
                print()
        
        print(f"{'='*70}\n")
    
    def test_1_usuario(self):
        """Test con 1 usuario"""
        resultado = self.simular_obtenciones_estatus_simultaneas(1)
        self.assertEqual(resultado["exitosos"], 1)
    
    def test_5_usuarios(self):
        """Test con 5 usuarios"""
        resultado = self.simular_obtenciones_estatus_simultaneas(5)
        self.assertGreaterEqual(resultado["exitosos"], 4)
    
    def test_10_usuarios(self):
        """Test con 10 usuarios"""
        resultado = self.simular_obtenciones_estatus_simultaneas(10)
        self.assertGreaterEqual(resultado["exitosos"], 8)

    def test_15_usuarios(self):
        """Test con 15 usuarios"""
        resultado = self.simular_obtenciones_estatus_simultaneas(15)
        self.assertGreaterEqual(resultado["exitosos"], 12)
    
    def test_20_usuarios(self):
        """Test con 20 usuarios (máximo)"""
        resultado = self.simular_obtenciones_estatus_simultaneas(20)
        self.assertGreaterEqual(resultado["exitosos"], 15)


if __name__ == "__main__":
    # Ejecutar pruebas
    unittest.main(verbosity=2)
    
    # O ejecutar directamente sin unittest:
    # test = TestMostrarEstatusPerfil()
    # test.simular_obtenciones_estatus_simultaneas(10)