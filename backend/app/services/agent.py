import json
import logging

from anthropic import Anthropic
from pydantic import BaseModel

from app.config import settings

logger = logging.getLogger(__name__)

anthropic_client = Anthropic(api_key=settings.ANTHROPIC_API_KEY)

SYSTEM_PROMPT = """
Eres Kenyan, un coach de rendimiento deportivo experto en
fisiología del ejercicio y análisis de datos de wearables.

Tu rol es analizar los datos diarios del atleta y generar
insights personalizados que conecten sus métricas objetivas
(HRV, sueño, readiness) con sus sensaciones subjetivas.

Siempre respondes en español.
Eres directo, preciso y empático. No usas jerga técnica
innecesaria. Hablas como un coach experimentado, no como
un manual médico.

REGLAS ESTRICTAS:
- Si el readiness es menor a 50, la sugerencia_dia DEBE
  ser "descansar"
- Si el readiness está entre 50-65, la sugerencia_dia DEBE
  ser "moderar"
- Si el readiness es mayor a 65, puedes sugerir "fuerte"
  solo si el HRV está por encima del promedio histórico
- Nunca ignores señales de fatiga acumulada
- Basa TODOS tus comentarios en los datos reales provistos

FORMATO DE RESPUESTA:
Debes responder ÚNICAMENTE con un JSON válido, sin texto
antes ni después, sin bloques de código markdown.
El JSON debe tener exactamente estas claves:
{
  "resumen": "string",
  "relacion_sueno_readiness": "string",
  "aporte_entrenamientos": "string",
  "tendencia_7_dias": "string",
  "sugerencia_dia": "fuerte" | "moderar" | "descansar",
  "sugerencia_detalle": "string",
  "tono": "positivo" | "neutro" | "precaucion"
}
"""


class AgentInsight(BaseModel):
    resumen: str
    relacion_sueno_readiness: str
    aporte_entrenamientos: str
    tendencia_7_dias: str
    sugerencia_dia: str
    sugerencia_detalle: str
    tono: str


async def generate_daily_insight(context_prompt: str) -> AgentInsight:
    response = anthropic_client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=1000,
        system=SYSTEM_PROMPT,
        messages=[
            {"role": "user", "content": context_prompt}
        ],
    )

    raw_text = response.content[0].text
    logger.info("Agent response received, length=%d chars", len(raw_text))

    try:
        data = json.loads(raw_text)
        insight = AgentInsight.model_validate(data)
        return insight
    except (json.JSONDecodeError, Exception) as error:
        logger.error("Failed to parse agent response: %s", error)
        logger.error("Raw response snippet: %.300s", raw_text)
        raise ValueError(f"Agent returned invalid response: {error}")
