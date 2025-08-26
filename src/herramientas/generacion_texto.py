import openai
import os
import httpx
from typing import Dict, List, Any, Optional
from .base import HerramientaBase
from loguru import logger

class GeneracionTextoTool(HerramientaBase):
    """
    Herramienta de generación de texto utilizando modelos de lenguaje grande.
    Soporta múltiples proveedores y modelos con configuración flexible.
    """
    
    def __init__(self, configuracion: Dict[str, Any]):
        super().__init__(configuracion)
        self.config_llm = configuracion.get('llm', {})
        self.proveedor = self.config_llm.get('proveedor', 'openai')
        self._inicializar_cliente()
    
    def _inicializar_cliente(self):
        """Inicializa el cliente según el proveedor configurado"""
        if self.proveedor == 'openai':
            api_key = self.config_llm.get('openai_api_key')
            if not api_key:
                raise ValueError("OpenAI API key no configurada")
            self.cliente = openai.AsyncOpenAI(api_key=api_key)
        elif self.proveedor == 'openrouter':
            api_key = os.getenv('OPENROUTER_API_KEY') or self.config_llm.get('openrouter_api_key')
            if not api_key:
                raise ValueError("OpenRouter API key no configurada")
            self.openrouter_api_key = api_key
            self.openrouter_url = "https://openrouter.ai/api/v1/chat/completions"
            self.cliente = None  # No cliente específico, usamos httpx
        else:
            raise ValueError(f"Proveedor no soportado: {self.proveedor}")
    
    async def ejecutar(self, prompt: str, modelo: str = None, 
                      temperatura: float = 0.7, max_tokens: int = 1000,
                      **kwargs) -> str:
        """
        Genera texto basado en un prompt utilizando el modelo especificado.
        
        Args:
            prompt: Texto de entrada para la generación
            modelo: Modelo a utilizar (opcional)
            temperatura: Control de creatividad (0-1)
            max_tokens: Máximo número de tokens a generar
            **kwargs: Parámetros adicionales
        
        Returns:
            str: Texto generado por el modelo
        """
        modelo = modelo or self.config_llm.get('modelo_default', 'gpt-3.5-turbo')
        
        try:
            if self.proveedor == 'openai':
                respuesta = await self.cliente.chat.completions.create(
                    model=modelo,
                    messages=[{"role": "user", "content": prompt}],
                    temperature=temperatura,
                    max_tokens=max_tokens,
                    **kwargs
                )
                return respuesta.choices[0].message.content
            elif self.proveedor == 'openrouter':
                async with httpx.AsyncClient() as client:
                    headers = {
                        "Authorization": f"Bearer {self.openrouter_api_key}",
                        "Content-Type": "application/json"
                    }
                    payload = {
                        "model": modelo,
                        "messages": [{"role": "user", "content": prompt}],
                        "temperature": temperatura,
                        "max_tokens": max_tokens
                    }
                    response = await client.post(self.openrouter_url, headers=headers, json=payload)
                    response.raise_for_status()
                    data = response.json()
                    return data["choices"][0]["message"]["content"]
            else:
                raise ValueError(f"Proveedor no implementado: {self.proveedor}")
        except Exception as e:
            logger.error(f"Error en generación de texto: {e}")
            raise