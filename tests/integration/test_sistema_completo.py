import pytest
import asyncio
import aiohttp
import json
from typing import Dict, Any

class TestSistemaCompleto:
    """Suite de pruebas de integración para el sistema SAAM completo"""
    
    @pytest.fixture(autouse=True)
    async def setup_sistema(self):
        """Fixture para inicializar el sistema de pruebas"""
        self.base_url = "http://localhost:8000"
        self.session = aiohttp.ClientSession()
        yield
        await self.session.close()
    
    async def test_flujo_completo_exitoso(self):
        """Prueba un flujo completo de objetivo exitoso"""
        # 1. Enviar objetivo al MCP
        objetivo = "Buscar información sobre inteligencia artificial y crear un resumen"
        
        async with self.session.post(
            f"{self.base_url}/mcp/planificar",
            json={"objetivo": objetivo, "contexto": {}}
        ) as response:
            assert response.status == 200
            planificacion = await response.json()
            assert 'plan' in planificacion
            assert 'id_plan' in planificacion
        
        # 2. Verificar que el plan se almacenó en memoria
        plan_id = planificacion['id_plan']
        
        async with self.session.get(
            f"{self.base_url}/sm3/plan/{plan_id}"
        ) as response:
            assert response.status == 200
            plan_almacenado = await response.json()
            assert plan_almacenado['id'] == plan_id
        
        # 3. Ejecutar el plan through MET
        async with self.session.post(
            f"{self.base_url}/met/ejecutar-plan",
            json={"plan_id": plan_id}
        ) as response:
            assert response.status == 202
            ejecucion = await response.json()
            assert 'id_ejecucion' in ejecucion
        
        # 4. Verificar que la ejecución se registró en memoria episódica
        ejecucion_id = ejecucion['id_ejecucion']
        
        async with self.session.get(
            f"{self.base_url}/sm3/episodio/{ejecucion_id}"
        ) as response:
            assert response.status == 200
            episodio = await response.json()
            assert episodio['id'] == ejecucion_id
            assert episodio['estado'] in ['exito', 'procesando']
        
        # 5. Verificar que el MAO procesó el episodio
        await asyncio.sleep(5)  # Dar tiempo al MAO
        
        async with self.session.get(
            f"{self.base_url}/mao/estado"
        ) as response:
            assert response.status == 200
            estado_mao = await response.json()
            assert 'ultimo_analisis' in estado_mao
    
    async def test_sistema_saludable(self):
        """Prueba que todos los módulos responden correctamente"""
        modulos = ['mcp', 'met', 'sm3', 'mao']
        
        for modulo in modulos:
            async with self.session.get(
                f"{self.base_url}/{modulo}/health"
            ) as response:
                assert response.status == 200
                health = await response.json()
                assert health['status'] == 'healthy'