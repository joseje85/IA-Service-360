import unicodedata
import re
from rapidfuzz import fuzz
from app.services.ollama_service import generate_response
from app.utils.direccion_validator import validar_direccion
import json


# ==============================
# 🔹 Normalizar texto base
# ==============================
def limpiar_texto(texto: str) -> str:
    texto = texto.upper()
    texto = ''.join(
        c for c in unicodedata.normalize('NFD', texto)
        if unicodedata.category(c) != 'Mn'
    )

    reemplazos = {
        "AV.": "AVENIDA",
        "AV ": "AVENIDA ",
        "COL.": "COLONIA",
        "COL ": "COLONIA ",
        "QRO": "QUERETARO"
    }

    for k, v in reemplazos.items():
        texto = texto.replace(k, v)

    texto = re.sub(r'[^A-Z0-9\s]', '', texto)
    texto = re.sub(r'\s+', ' ', texto).strip()

    return texto


# ==============================
# 🔹 Agrupar direcciones similares
# ==============================
def agrupar_direcciones(direcciones):
    grupos = []

    for direccion in direcciones:
        agregado = False

        for grupo in grupos:
            similitud = fuzz.token_sort_ratio(direccion, grupo[0])

            if similitud > 85:
                grupo.append(direccion)
                agregado = True
                break

        if not agregado:
            grupos.append([direccion])

    return grupos

def extraer_json(texto):

    try:
        # intenta parse directo
        return json.loads(texto)
    except:
        pass

    # 🔥 buscar JSON dentro del texto
    match = re.search(r"\{.*\}", texto, re.DOTALL)

    if match:
        try:
            return json.loads(match.group())
        except:
            pass

    return None

# ==============================
# 🔹 IA para estructurar dirección
# ==============================
def normalizar_con_ia(grupo):

    prompt = f"""
Eres un experto en direcciones fiscales en México.

Analiza estas direcciones y genera UNA sola dirección normalizada:

{grupo}

Responde SOLO en JSON con esta estructura:

{{
  "calle": "",
  "numero_exterior": "",
  "numero_interior": "",
  "colonia": "",
  "municipio": "",
  "estado": "",
  "codigo_postal": ""
}}
"""

    respuesta = generate_response(prompt)

    data = extraer_json(respuesta)

    if not data:
        print("⚠️ No se pudo parsear JSON:", respuesta)
        return {}

    return data


# ==============================
# 🔹 Proceso completo
# ==============================
def procesar_direcciones(rfc, direcciones):

    # 1. limpiar
    direcciones_limpias = [limpiar_texto(d) for d in direcciones]

    # 2. agrupar
    grupos = agrupar_direcciones(direcciones_limpias)

    resultado = []

    for grupo in grupos:
        direccion_ia = normalizar_con_ia(grupo)

        direccion_limpia = validar_direccion(direccion_ia)

        resultado.append({
            "direccion_normalizada": direccion_limpia,
            "similares_detectadas": len(grupo)
        })

    return {
        "rfc": rfc,
        "direcciones_originales": len(direcciones),
        "direcciones_unicas": len(resultado),
        "resultado": resultado
    }