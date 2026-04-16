import re
import unicodedata

# =========================
# CATÁLOGO ESTADOS
# =========================
ESTADOS = {
    "AGUASCALIENTES",
    "BAJA CALIFORNIA",
    "BAJA CALIFORNIA SUR",
    "CAMPECHE",
    "CHIAPAS",
    "CHIHUAHUA",
    "CDMX",
    "CIUDAD DE MEXICO",
    "COAHUILA",
    "COLIMA",
    "DURANGO",
    "GUANAJUATO",
    "GUERRERO",
    "HIDALGO",
    "JALISCO",
    "MEXICO",
    "MICHOACAN",
    "MORELOS",
    "NAYARIT",
    "NUEVO LEON",
    "OAXACA",
    "PUEBLA",
    "QUERETARO",
    "QUINTANA ROO",
    "SAN LUIS POTOSI",
    "SINALOA",
    "SONORA",
    "TABASCO",
    "TAMAULIPAS",
    "TLAXCALA",
    "VERACRUZ",
    "YUCATAN",
    "ZACATECAS"
}

# =========================
# NORMALIZACIÓN GENERAL
# =========================
def limpiar_texto(txt):
    if not txt:
        return ""

    txt = str(txt).upper().strip()

    txt = unicodedata.normalize("NFKD", txt)
    txt = txt.encode("ASCII", "ignore").decode("ASCII")

    txt = re.sub(r"[^\w\s]", "", txt)
    txt = re.sub(r"\s+", " ", txt)

    return txt


# =========================
# CALLE
# =========================
def validar_calle(calle):
    calle = limpiar_texto(calle)

    reemplazos = {
        "AV ": "AVENIDA ",
        "AVENIDA.": "AVENIDA",
        "CALLE.": "CALLE",
    }

    for k, v in reemplazos.items():
        calle = calle.replace(k, v)

    return calle


# =========================
# NÚMEROS
# =========================
def validar_numero(num):
    if not num:
        return ""

    num = limpiar_texto(num)

    # deja solo letras y números
    num = re.sub(r"[^A-Z0-9]", "", num)

    return num


# =========================
# CP
# =========================
def validar_cp(cp):
    if not cp:
        return ""

    cp = re.sub(r"\D", "", str(cp))

    if len(cp) == 5:
        return cp

    if len(cp) < 5:
        return cp.zfill(5)

    return cp[:5]


# =========================
# ESTADO
# =========================
def validar_estado(estado):
    estado = limpiar_texto(estado)

    equivalencias = {
        "QRO": "QUERETARO",
        "CDMX": "CIUDAD DE MEXICO",
        "EDOMEX": "MEXICO"
    }

    estado = equivalencias.get(estado, estado)

    if estado in ESTADOS:
        return estado

    return ""


# =========================
# FUNCIÓN PRINCIPAL
# =========================
def validar_direccion(d):

    if not isinstance(d, dict):
        return {
            "calle": "",
            "numero_exterior": "",
            "numero_interior": "",
            "colonia": "",
            "municipio": "",
            "estado": "",
            "codigo_postal": ""
        }

    return {
        "calle": validar_calle(d.get("calle")),
        "numero_exterior": validar_numero(d.get("numero_exterior")),
        "numero_interior": validar_numero(d.get("numero_interior")),
        "colonia": limpiar_texto(d.get("colonia")),
        "municipio": limpiar_texto(d.get("municipio")),
        "estado": validar_estado(d.get("estado")),
        "codigo_postal": validar_cp(d.get("codigo_postal"))
    }