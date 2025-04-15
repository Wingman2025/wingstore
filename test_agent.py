import os
import django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "wingstore.settings")
django.setup()

import asyncio
from agents import Runner
from store.views import AGENT

async def main():
    pregunta = input("¿Qué quieres preguntarle al agente?: ")
    result = await Runner.run(AGENT, pregunta)
    print("\nRespuesta del agente:")
    print(result.final_output)

if __name__ == "__main__":
    asyncio.run(main())
