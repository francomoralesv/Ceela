import datetime
import os
from httpx import AsyncClient

class Log:
    @staticmethod
    async def save(message: str, level='info', **kwargs):
        """
        Realiza una llamada HTTP y guarda un log de la solicitud y la respuesta.

        :param source: Fuente de la solicitud.
        :param payload: Datos de la solicitud.
        :param kwargs: Parámetros adicionales para la solicitud (headers, data, etc.).
        :return: Respuesta de la solicitud.
        """

        app_env = os.getenv("APP_ENV") or "prod"
        app_name = os.getenv("APP_NAME") or "Ceela Backend"
        source = app_name + " - " + app_env
        payload = {
            "source": source,
            "message": message,
            "level": level,
            "timestamp": datetime.datetime.utcnow().isoformat() + "Z"
        }

        endpoint = os.getenv("LOGGER_ENDPOINT") + "logging"
        print(f"Endpoint logger: {endpoint}")
        try:
            async with AsyncClient() as client:
                response = await client.post(
                    url=endpoint,
                    json=payload,
                    **kwargs
                )
                print(f"[Registry logger]Sending log to Registry Logger with source {source} and message {message}")
                response.raise_for_status()
                return response
        except Exception as e:
            print(f"[Registry logger]Error connecting with Registry Logger {e}")
