from django.shortcuts import render
from .models import Product
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import json
import logging
from agents import Agent, Runner, function_tool, WebSearchTool
import os
from asgiref.sync import sync_to_async
import traceback
from django.conf import settings
import asyncio

# Create your views here.

# Página principal con lista de productos

def product_list(request):
    year = request.GET.get('year')
    categoria = request.GET.get('categoria')
    products = Product.objects.all()
    # Filtrado por año en el nombre
    if year:
        products = products.filter(name__icontains=year)
    # Filtrado por categoría en el nombre
    if categoria:
        products = products.filter(name__icontains=categoria)
    return render(request, 'store/product_list.html', {'products': products})

# Vista para mostrar el detalle de un producto individual
def product_detail(request, pk):
    from django.shortcuts import get_object_or_404
    product = get_object_or_404(Product, pk=pk)
    return render(request, 'store/product_detail.html', {'product': product})

# Configura logging para depuración del agente
logger = logging.getLogger(__name__)

# Tool: función para consultar productos y stock
@function_tool
async def listar_productos() -> str:
    from .models import Product
    import logging
    productos = await sync_to_async(list)(Product.objects.all())
    logging.debug(f"[DEBUG listar_productos] Productos encontrados: {productos}")
    if not productos:
        return "No hay productos disponibles en este momento."
    respuesta = ""
    for p in productos:
        url = f"http://127.0.0.1:8000/producto/{p.pk}/"
        respuesta += f"- {p.name}: {p.description[:40]}... (Stock: {p.stock}) [Ver producto]({url})\n"
    return respuesta

# Agente OpenAI para atención joven y deportiva en español
AGENT = Agent(
    name="WingfoilBot",
    instructions=(
        "Eres un agente de atención al cliente para una tienda de wingfoil. "
        "Cuando uses la herramienta 'listar_productos', muestra los enlaces tal como aparecen en la respuesta (en formato Markdown), sin resumir ni eliminar los links. "
        "Si el usuario pregunta por productos, stock o cualquier duda sobre wingfoil, responde de forma clara y motivadora. "
        "Usa la herramienta 'listar_productos' si necesitas información real de los productos y 'web_search' si necesitas buscar información en internet."
    ),
    tools=[listar_productos, WebSearchTool()],
    model="gpt-4.1",
)

# Chat con el agente (básico, integración posterior)

def chat(request):
    return render(request, 'store/chat.html')

def run_agent_sync(agent, message):
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    return loop.run_until_complete(Runner.run(agent, message))

# Endpoint para chat API con el agente
@csrf_exempt
def chat_api(request):
    try:
        if request.method == 'POST':
            try:
                data = json.loads(request.body)
            except Exception as e:
                tb = traceback.format_exc()
                logger.error(f"Error leyendo el JSON: {e}\n{tb}")
                return JsonResponse({'response': f"ERROR al leer JSON: {e}\n{tb}"}, status=400)

            user_message = data.get('message', '')
            history = data.get('history', [])
            logger.info(f"Mensaje recibido del usuario: {user_message}")
            try:
                # Convierte el historial del frontend al formato OpenAI
                messages = []
                for msg in history:
                    if msg['sender'] == 'user':
                        messages.append({'role': 'user', 'content': msg['text']})
                    elif msg['sender'] == 'agent':
                        messages.append({'role': 'assistant', 'content': msg['text']})
                # Añade el mensaje actual al final
                messages.append({'role': 'user', 'content': user_message})
                result = run_agent_sync(AGENT, messages)
                respuesta = result.final_output
                return JsonResponse({'response': respuesta})
            except Exception as e:
                tb = traceback.format_exc()
                logger.error(f"Error en chat_api: {e}\n{tb}")
                error_msg = str(e)
                if settings.DEBUG:
                    error_msg += "\n" + tb
                return JsonResponse({'response': f"ERROR: {error_msg}"}, status=500)
        else:
            return JsonResponse({'response': 'Método no permitido'}, status=405)
    except Exception as e:
        tb = traceback.format_exc()
        logger.error(f"Error fuera del try principal: {e}\n{tb}")
        return JsonResponse({'response': f"ERROR fuera del try principal: {e}\n{tb}"}, status=500)
