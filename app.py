import hashlib
import json
import math
import re
import secrets
import urllib.error
import urllib.parse
import urllib.request
import unicodedata
from io import BytesIO
from html import escape

import pandas as pd
import plotly.express as px
import streamlit as st
from supabase_config import supabase


st.set_page_config(
    page_title="CRM CDA",
    page_icon="🚗",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ======================================================
# SESSION
# ======================================================

if "login" not in st.session_state:
    st.session_state.login = False

if "usuario" not in st.session_state:
    st.session_state.usuario = ""

if "rol" not in st.session_state:
    st.session_state.rol = ""

if "filtro_estado" not in st.session_state:
    st.session_state.filtro_estado = "Todos"

if "pagina_clientes" not in st.session_state:
    st.session_state.pagina_clientes = 1


def hash_password(password):
    salt = secrets.token_bytes(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, 310_000)
    return "pbkdf2_sha256$310000$" + salt.hex() + "$" + digest.hex()


def verificar_password(password, almacenada):
    if not almacenada:
        return False
    if not str(almacenada).startswith("pbkdf2_sha256$"):
        return secrets.compare_digest(str(almacenada), password)
    try:
        algoritmo, iteraciones, salt_hex, digest_hex = str(almacenada).split("$", 3)
        if algoritmo != "pbkdf2_sha256":
            return False
        digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), bytes.fromhex(salt_hex), int(iteraciones))
        return secrets.compare_digest(digest.hex(), digest_hex)
    except (ValueError, TypeError):
        return False

# ======================================================
# LOGIN
# ======================================================

def pantalla_login():
    st.markdown(
        """
        <div class="login-card">
            <div class="login-logo">🚗</div>
            <h1>CRM CDA</h1>
            <p>Ingresa para gestionar clientes y renovaciones.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    usuario = st.text_input("Usuario")
    password = st.text_input("Contraseña", type="password")

    if st.button("Ingresar", use_container_width=True):
        resultado = (
            supabase.table("usuarios").select("usuario,password,rol")
            .eq("usuario", usuario.strip()).limit(1).execute()
        )
        datos = resultado.data[0] if resultado.data else None
        if datos and verificar_password(password, datos.get("password", "")):
            if not str(datos.get("password", "")).startswith("pbkdf2_sha256$"):
                supabase.table("usuarios").update({"password": hash_password(password)}).eq(
                    "usuario", datos["usuario"]
                ).execute()
            st.session_state.login = True
            st.session_state.usuario = datos["usuario"]
            st.session_state.rol = datos["rol"]
            st.rerun()
        st.error("Usuario o contraseña incorrectos")


# ======================================================
# CONFIGURACION
# ======================================================

st.markdown(
    """
    <style>
    :root{
        --crm-blue:#2563eb;
        --crm-blue-dark:#1d4ed8;
        --crm-border:#e5e7eb;
        --crm-muted:#64748b;
        --crm-text:#0f172a;
        --crm-soft:#f8fafc;
        --crm-shadow:0 12px 32px rgba(15,23,42,.08);
    }

    .stApp{
        background:#ffffff;
        color:var(--crm-text);
    }

    [data-testid="stSidebar"]{
        background:linear-gradient(180deg,#f8fafc 0%,#ffffff 100%);
        border-right:1px solid var(--crm-border);
        box-shadow:6px 0 22px rgba(15,23,42,.04);
    }

    [data-testid="stSidebar"] [data-testid="stSidebarContent"]{
        padding:1.25rem 1rem;
    }

    [data-testid="stSidebar"] label,
    [data-testid="stSidebar"] p,
    [data-testid="stSidebar"] span{
        color:#334155;
    }

    [data-testid="stSidebar"] [role="radiogroup"] label{
        border-radius:8px;
        padding:.65rem .75rem;
        margin:.2rem 0;
    }

    [data-testid="stSidebar"] [role="radiogroup"] label:has(input:checked){
        background:linear-gradient(135deg,var(--crm-blue),#1f6fff);
        color:white;
        box-shadow:0 10px 22px rgba(37,99,235,.22);
    }

    [data-testid="stSidebar"] [role="radiogroup"] label:has(input:checked) span,
    [data-testid="stSidebar"] [role="radiogroup"] label:has(input:checked) p{
        color:white;
    }

    .block-container{
        max-width:1280px;
        padding-top:1.4rem;
        padding-bottom:2rem;
    }

    .main-header{
        display:flex;
        align-items:center;
        justify-content:space-between;
        gap:1rem;
        padding:.15rem 0 1.15rem;
        border-bottom:1px solid var(--crm-border);
        margin-bottom:1rem;
    }

    .main-title{
        display:flex;
        align-items:center;
        gap:.75rem;
        font-size:1.75rem;
        line-height:1.1;
        font-weight:800;
        color:#0b1220;
        margin:0;
    }

    .user-chip{
        display:inline-flex;
        align-items:center;
        gap:.45rem;
        border:1px solid var(--crm-border);
        border-radius:8px;
        padding:.58rem .85rem;
        background:white;
        box-shadow:0 6px 18px rgba(15,23,42,.05);
        font-size:.9rem;
    }

    .sidebar-brand{
        display:flex;
        align-items:center;
        gap:.7rem;
        font-size:1.2rem;
        font-weight:800;
        color:#111827;
        padding:.15rem .25rem 1rem;
        border-bottom:1px solid var(--crm-border);
        margin-bottom:.9rem;
    }

    .sidebar-footer{
        border-top:1px solid var(--crm-border);
        margin-top:2rem;
        padding-top:.9rem;
    }

    .stTextInput input,
    .stDateInput input,
    .stSelectbox [data-baseweb="select"]{
        border-radius:8px !important;
        border-color:#d8dee8 !important;
        min-height:2.55rem;
    }

    div[data-testid="stButton"] > button,
    div[data-testid="stDownloadButton"] > button,
    div[data-testid="stLinkButton"] > a{
        border-radius:8px;
        border:1px solid #d8dee8;
        background:#ffffff;
        color:#0f172a;
        min-height:2.65rem;
        font-weight:600;
        box-shadow:0 5px 14px rgba(15,23,42,.05);
    }

    div[data-testid="stButton"] > button:hover,
    div[data-testid="stDownloadButton"] > button:hover,
    div[data-testid="stLinkButton"] > a:hover{
        border-color:var(--crm-blue);
        color:var(--crm-blue);
    }

    .filter-row div[data-testid="stButton"] > button{
        justify-content:center;
    }

    .metric-card{
        border:1px solid var(--crm-border);
        border-radius:8px;
        padding:1rem;
        background:white;
        box-shadow:var(--crm-shadow);
    }

    .client-card{
        border:1px solid var(--crm-border);
        border-radius:8px;
        padding:1rem;
        background:#ffffff;
        box-shadow:var(--crm-shadow);
        margin-bottom:.75rem;
    }

    .client-card-grid{
        display:grid;
        grid-template-columns:minmax(280px, 1fr) 150px 150px 90px 90px 88px;
        align-items:center;
        gap:1rem;
    }

    .client-main{
        display:flex;
        align-items:center;
        gap:1rem;
        min-width:0;
    }

    .card-separator{
        border-left:1px solid var(--crm-border);
        min-height:4.35rem;
        display:flex;
        flex-direction:column;
        justify-content:center;
        align-items:center;
        padding-left:1rem;
    }

    .vehicle-avatar{
        width:3.7rem;
        height:3.7rem;
        border-radius:999px;
        display:flex;
        align-items:center;
        justify-content:center;
        font-size:1.55rem;
        flex:0 0 auto;
    }

    .plate{
        font-size:1.2rem;
        font-weight:800;
        line-height:1.05;
        color:#0f172a;
        letter-spacing:0;
    }

    .client-name{
        font-size:1rem;
        font-weight:600;
        color:#111827;
        margin-top:.35rem;
        overflow:hidden;
        text-overflow:ellipsis;
        white-space:nowrap;
    }

    .last-note{
        margin-top:.45rem;
        color:#334155;
        font-size:.82rem;
        line-height:1.35;
        overflow:hidden;
        text-overflow:ellipsis;
        white-space:nowrap;
    }

    .cell-title{
        color:#334155;
        font-size:.78rem;
        text-align:center;
        margin-bottom:.28rem;
    }

    .due-date{
        font-size:1.05rem;
        font-weight:800;
        color:#0f172a;
        text-align:center;
    }

    .status-pill{
        display:inline-flex;
        justify-content:center;
        border-radius:8px;
        padding:.45rem .8rem;
        font-size:.86rem;
        font-weight:800;
        min-width:6rem;
    }

    .status-pendiente{
        color:#d97706;
        background:#fef3c7;
    }

    .status-agendado{
        color:#ea580c;
        background:#ffedd5;
    }

    .status-renovado{
        color:#15803d;
        background:#dcfce7;
    }

    .action-link{
        display:flex;
        flex-direction:column;
        align-items:center;
        justify-content:center;
        gap:.22rem;
        text-decoration:none !important;
        color:#0f172a !important;
        font-weight:700;
        font-size:.78rem;
    }

    .action-icon{
        width:3.6rem;
        height:3.6rem;
        border-radius:14px;
        display:flex;
        align-items:center;
        justify-content:center;
        color:white;
        font-size:1.7rem;
        box-shadow:0 10px 22px rgba(15,23,42,.14);
    }

    .action-icon svg{
        width:1.8rem;
        height:1.8rem;
        display:block;
    }
    .action-whatsapp{
        background:linear-gradient(145deg,#22c55e,#16a34a);
    }

    .action-call{
        background:linear-gradient(145deg,#3b82f6,#2563eb);
    }

    div[class*="st-key-abrir_gestion_"] button{
        min-height:4.9rem;
        border-radius:14px;
        border:1px solid var(--crm-border);
        background:white;
        box-shadow:0 8px 20px rgba(15,23,42,.06);
        font-size:.78rem;
        font-weight:700;
    }

    div[class*="st-key-abrir_gestion_"] button:hover{
        border-color:var(--crm-blue);
        color:var(--crm-blue);
    }
    .manage-button{
        display:flex;
        flex-direction:column;
        align-items:center;
        justify-content:center;
        text-decoration:none !important;
        color:#0f172a !important;
        border:1px solid var(--crm-border);
        border-radius:14px;
        padding:.62rem .5rem;
        text-align:center;
        box-shadow:0 8px 20px rgba(15,23,42,.06);
        font-size:.78rem;
        font-weight:700;
        background:white;
    }

    .management-panel{
        margin:-.35rem 0 .75rem;
    }

    .pagination{
        display:flex;
        align-items:center;
        justify-content:center;
        gap:.4rem;
        margin-top:.7rem;
    }

    .page-pill{
        min-width:2.1rem;
        height:2.1rem;
        border:1px solid var(--crm-border);
        border-radius:8px;
        display:flex;
        align-items:center;
        justify-content:center;
        color:#0f172a;
        background:white;
    }

    .page-pill.active{
        background:var(--crm-blue);
        color:white;
        border-color:var(--crm-blue);
    }

    .login-card{
        max-width:430px;
        margin:9vh auto 1.25rem;
        text-align:center;
    }

    .login-card h1{
        margin:.35rem 0 .2rem;
        font-size:2rem;
    }

    .login-card p{
        color:var(--crm-muted);
        margin:0;
    }

    .login-logo{
        display:inline-flex;
        width:4rem;
        height:4rem;
        align-items:center;
        justify-content:center;
        border-radius:18px;
        background:#eef4ff;
        font-size:2rem;
    }

    @media (max-width: 900px){
        .main-header{
            align-items:flex-start;
            flex-direction:column;
        }
        .client-main{
            align-items:flex-start;
        }
        .client-card-grid{
            grid-template-columns:1fr 1fr;
        }
        .card-separator{
            border-left:0;
            border-top:1px solid var(--crm-border);
            padding-left:0;
            padding-top:.8rem;
        }
        .plate{
            font-size:1.05rem;
        }
        .action-icon{
            width:3.1rem;
            height:3.1rem;
        }
    }
    </style>
    """,
    unsafe_allow_html=True,
)

if not st.session_state.login:
    pantalla_login()
    st.stop()

st.sidebar.markdown(
    """
    <div class="sidebar-brand">
        <span>🚗</span>
        <span>CRM CDA</span>
    </div>
    """,
    unsafe_allow_html=True,
)

menu = st.sidebar.radio(
    "Menú",
    ["📊 Dashboard", "📋 CRM", "📥 Importar Base", "👥 Administración"],
    label_visibility="collapsed",
)

bases = (
    supabase
    .table("bases")
    .select("*")
    .order("nombre")
    .execute()
)

bases_dict = {
    b["nombre"]: b["id"]
    for b in bases.data
}

if not bases_dict and menu != "📥 Importar Base":
    st.error("No hay bases creadas. Ve a Importar Base para crear la primera.")
    st.stop()

if bases_dict:
    st.sidebar.divider()
    st.sidebar.caption("BASE ACTIVA")
    base_seleccionada = st.sidebar.selectbox(
        "Base activa", list(bases_dict.keys()), label_visibility="collapsed"
    )
    base_id = bases_dict[base_seleccionada]
else:
    base_seleccionada = None
    base_id = None
    st.sidebar.info("Aún no hay bases")

st.sidebar.markdown(
    f"""
    <div class="sidebar-footer">
        <div class="user-chip">👤 {escape(str(st.session_state.usuario or ""))}</div>
    </div>
    """,
    unsafe_allow_html=True,
)

if st.sidebar.button("↪ Salir", use_container_width=True):
    st.session_state.login = False
    st.session_state.usuario = ""
    st.session_state.rol = ""
    st.rerun()


# ======================================================
# HELPERS
# ======================================================

def link_whatsapp(nombre, placa, telefono):
    telefono = str(telefono).replace(".0", "")
    telefono = telefono.replace(" ", "")
    telefono = re.sub(r"\D", "", telefono)

    if not telefono.startswith("57"):
        telefono = "57" + telefono

    mensaje = f"""
Hola {nombre}

Te escribimos del CDA Occidente.

Tu vehículo con placa {placa} tiene vencimiento próximo.

¿Deseas agendar tu revisión?
"""

    mensaje = urllib.parse.quote(mensaje)

    return f"https://wa.me/{telefono}?text={mensaje}" if telefono.isdigit() and 10 <= len(telefono) <= 12 else "#"


def convertir_excel(dataframe):
    output = BytesIO()

    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        dataframe.to_excel(
            writer,
            index=False,
            sheet_name="Clientes",
        )

    return output.getvalue()


def header(titulo, icono):
    st.markdown(
        f"""
        <div class="main-header">
            <h1 class="main-title"><span>{icono}</span><span>{titulo}</span></h1>
            <div class="user-chip">👤 {texto_html(st.session_state.usuario)}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def estado_clase(estado):
    estado = str(estado or "Pendiente").strip()
    if estado == "Renovado":
        return "status-renovado"
    if estado == "Agendado":
        return "status-agendado"
    return "status-pendiente"


def color_avatar(index):
    colores = ["#dbeafe", "#ddd6fe", "#dcfce7", "#fef3c7", "#fce7f3"]
    return colores[index % len(colores)]


def telefono_limpio(telefono):
    telefono = str(telefono).replace(".0", "")
    telefono = telefono.replace(" ", "")
    telefono = re.sub(r"\D", "", telefono)
    return telefono


def texto_html(valor):
    return escape(str(valor or ""))


def configuracion_whatsapp():
    """Lee secretos de Streamlit sin incluir credenciales en el código fuente."""
    defaults = {
        "token": "", "phone_id": "", "template": "recordatorio_renovacion",
        "language": "es_CO", "api_version": "v27.0",
    }
    try:
        defaults["token"] = st.secrets.get("WHATSAPP_ACCESS_TOKEN", "")
        defaults["phone_id"] = st.secrets.get("WHATSAPP_PHONE_NUMBER_ID", "")
        defaults["template"] = st.secrets.get("WHATSAPP_TEMPLATE_NAME", defaults["template"])
        defaults["language"] = st.secrets.get("WHATSAPP_TEMPLATE_LANGUAGE", defaults["language"])
        defaults["api_version"] = st.secrets.get("WHATSAPP_API_VERSION", defaults["api_version"])
    except Exception:
        pass
    return defaults


def enviar_plantilla_whatsapp(telefono, nombre, placa, fecha):
    config = configuracion_whatsapp()
    telefono = telefono_limpio(telefono)
    if not telefono.startswith("57"):
        telefono = "57" + telefono
    if not telefono.isdigit() or not 11 <= len(telefono) <= 15:
        raise ValueError("El teléfono no tiene un formato internacional válido.")

    payload = {
        "messaging_product": "whatsapp",
        "to": telefono,
        "type": "template",
        "template": {
            "name": config["template"],
            "language": {"code": config["language"]},
            "components": [{
                "type": "body",
                "parameters": [
                    {"type": "text", "text": str(nombre)[:100]},
                    {"type": "text", "text": str(placa)[:30]},
                    {"type": "text", "text": str(fecha)[:30]},
                ],
            }],
        },
    }
    url = "https://graph.facebook.com/{}/{}/messages".format(
        config["api_version"], config["phone_id"]
    )
    request = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Authorization": "Bearer " + config["token"],
            "Content-Type": "application/json",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            result = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as error:
        try:
            details = json.loads(error.read().decode("utf-8"))
            message = details.get("error", {}).get("message", "Error de WhatsApp API")
        except (ValueError, AttributeError):
            message = "Error HTTP {} de WhatsApp API".format(error.code)
        raise RuntimeError(message) from None
    except urllib.error.URLError:
        raise RuntimeError("No se pudo conectar con WhatsApp API.") from None

    message_id = (result.get("messages") or [{}])[0].get("id")
    if not message_id:
        raise RuntimeError("WhatsApp no confirmó la recepción del mensaje.")
    return message_id

def ultima_observacion(cliente_id):
    ultima_gestion = (
        supabase
        .table("gestiones")
        .select("*")
        .eq("cliente_id", cliente_id)
        .order("fecha", desc=True)
        .limit(1)
        .execute()
    )

    if len(ultima_gestion.data) == 0:
        return "Sin gestión registrada"

    obs = ultima_gestion.data[0].get("observacion", "")
    if len(obs) > 86:
        obs = obs[:86] + "..."

    return obs


def render_metric(label, value):
    st.markdown(
        f"""
        <div class="metric-card">
            <div style="font-size:.78rem;color:#64748b;font-weight:700;">{label}</div>
            <div style="font-size:1.65rem;font-weight:800;color:#0f172a;">{value}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_pagination(total, por_pagina):
    total_paginas = max(1, math.ceil(total / por_pagina))
    st.session_state.pagina_clientes = min(st.session_state.pagina_clientes, total_paginas)

    anterior, centro, siguiente = st.columns([1, 8, 1])

    with anterior:
        if st.button("‹", key="pagina_anterior", use_container_width=True, disabled=st.session_state.pagina_clientes == 1):
            st.session_state.pagina_clientes -= 1
            st.rerun()

    with centro:
        paginas = []
        for pagina in range(1, total_paginas + 1):
            if pagina <= 3 or pagina == total_paginas or abs(pagina - st.session_state.pagina_clientes) <= 1:
                clase = "page-pill active" if pagina == st.session_state.pagina_clientes else "page-pill"
                paginas.append(f'<span class="{clase}">{pagina}</span>')
            elif paginas[-1] != '<span class="page-pill">...</span>':
                paginas.append('<span class="page-pill">...</span>')

        st.markdown(
            f'<div class="pagination">{"".join(paginas)}</div>',
            unsafe_allow_html=True,
        )

    with siguiente:
        if st.button("›", key="pagina_siguiente", use_container_width=True, disabled=st.session_state.pagina_clientes == total_paginas):
            st.session_state.pagina_clientes += 1
            st.rerun()


def normalizar_encabezado(valor):
    texto = unicodedata.normalize("NFKD", str(valor or ""))
    texto = texto.encode("ascii", "ignore").decode("ascii").lower()
    return re.sub(r"[^a-z0-9]+", " ", texto).strip()


def mapear_encabezados(encabezados):
    alias = {
        "placa": {
            "placa", "placa vehiculo", "numero placa", "numero de placa", "matricula",
            "patente", "plate", "license plate", "vehiculo placa",
        },
        "cliente": {
            "cliente", "nombre", "nombre cliente", "nombre del cliente", "propietario",
            "nombre propietario", "titular", "razon social", "customer", "client",
        },
        "telefono": {
            "telefono", "telefono cliente", "celular", "movil", "numero celular",
            "telefono movil", "whatsapp", "contacto", "phone", "mobile",
        },
        "sede": {
            "sede", "sucursal", "centro", "centro de servicio", "oficina", "localidad",
            "branch", "site",
        },
        "fecha_renovacion": {
            "fecha", "fecha renovacion", "fecha de renovacion", "vencimiento", "fecha vencimiento",
            "fecha de vencimiento", "fecha proxima revision", "proxima revision",
            "fecha revision", "fecha vencimiento rtm", "fecha rtm", "renewal date",
            "expiration date", "due date",
        },
        "estado": {"estado", "status", "situacion", "estado cliente"},
    }
    resultado = {}
    for encabezado in encabezados:
        normalizado = normalizar_encabezado(encabezado)
        for campo, opciones in alias.items():
            coincide = normalizado in opciones
            if coincide and (
                campo not in resultado
                or (campo == "fecha_renovacion" and normalizado != "fecha")
            ):
                resultado[campo] = encabezado
    return resultado


def nombres_columnas_unicos(valores):
    resultado = []
    usados = set()
    for indice, valor in enumerate(valores, start=1):
        base = str(valor).strip() if pd.notna(valor) else ""
        if not base or base.lower().startswith("unnamed"):
            base = "Columna {}".format(indice)
        nombre = base
        sufijo = 2
        while nombre.lower() in usados:
            nombre = "{} ({})".format(base, sufijo)
            sufijo += 1
        usados.add(nombre.lower())
        resultado.append(nombre)
    return resultado


def convertir_fecha_excel(valor):
    """Interpreta fechas Excel, fechas nativas, texto y seriales comunes."""
    if valor is None or pd.isna(valor):
        return pd.NaT
    if isinstance(valor, (int, float)) and not isinstance(valor, bool):
        numero = float(valor)
        if 20000 <= numero <= 80000:
            return pd.to_datetime(numero, unit="D", origin="1899-12-30", errors="coerce")
        if 1_000_000_000 <= numero < 100_000_000_000:
            return pd.to_datetime(numero, unit="s", errors="coerce")
        if 1_000_000_000_000 <= numero < 100_000_000_000_000:
            return pd.to_datetime(numero, unit="ms", errors="coerce")
        valor = str(int(numero)) if numero.is_integer() else str(numero)

    texto = str(valor).strip()
    if not texto:
        return pd.NaT
    if re.fullmatch(r"\d{8}", texto):
        fecha_compacta = pd.to_datetime(texto, format="%Y%m%d", errors="coerce")
        if pd.notna(fecha_compacta):
            return fecha_compacta
    if re.fullmatch(r"\d{4,6}(?:\.0+)?", texto):
        serial = float(texto)
        if 20000 <= serial <= 80000:
            return pd.to_datetime(serial, unit="D", origin="1899-12-30", errors="coerce")

    texto_es = unicodedata.normalize("NFKD", texto).encode("ascii", "ignore").decode("ascii").lower()
    texto_es = re.sub(
        r"\b(lunes|martes|miercoles|jueves|viernes|sabado|domingo)\b\s*,?\s*",
        "",
        texto_es,
    )
    texto_es = re.sub(r"\s+", " ", texto_es).strip()
    meses = {
        "enero": "jan", "ene": "jan", "febrero": "feb", "feb": "feb",
        "marzo": "mar", "mar": "mar", "abril": "apr", "abr": "apr",
        "mayo": "may", "junio": "jun", "jun": "jun", "julio": "jul",
        "jul": "jul", "agosto": "aug", "ago": "aug", "septiembre": "sep",
        "setiembre": "sep", "sept": "sep", "sep": "sep", "octubre": "oct",
        "oct": "oct", "noviembre": "nov", "nov": "nov", "diciembre": "dec",
        "dic": "dec",
    }
    texto_es = re.sub(r"\b(de|del)\b", " ", texto_es)
    for mes_es, mes_en in meses.items():
        texto_es = re.sub(r"\b{}\b".format(mes_es), mes_en, texto_es)

    formatos = [
        "%d/%m/%Y", "%d-%m-%Y", "%d.%m.%Y", "%d/%m/%y", "%d-%m-%y",
        "%Y-%m-%d", "%Y/%m/%d", "%Y.%m.%d", "%m/%d/%Y", "%m-%d-%Y",
        "%Y%m%d", "%d%m%Y", "%d %b %Y", "%d %B %Y", "%b %d, %Y",
        "%B %d, %Y", "%d %b %Y %H:%M:%S", "%Y-%m-%d %H:%M:%S",
    ]
    for formato in formatos:
        fecha = pd.to_datetime(texto_es, format=formato, errors="coerce")
        if pd.notna(fecha):
            return fecha
    fecha = pd.to_datetime(texto_es, errors="coerce", dayfirst=True)
    if pd.notna(fecha):
        return fecha
    return pd.to_datetime(texto_es, errors="coerce", dayfirst=False)

def pantalla_importar_base():
    header("Importar Base de Clientes", "📥")

    if st.session_state.rol == "admin":
        with st.expander("➕ Crear nueva base", expanded=not bool(bases_dict)):
            nombre_base = st.text_input("Nombre de la nueva base", key="nueva_base_importar")
            if st.button("Crear Base", key="crear_base_importar"):
                nombre_limpio = nombre_base.strip()
                if not nombre_limpio:
                    st.error("Escribe el nombre de la base.")
                elif any(n.lower() == nombre_limpio.lower() for n in bases_dict):
                    st.error("Ya existe una base con ese nombre.")
                else:
                    supabase.table("bases").insert({"nombre": nombre_limpio}).execute()
                    st.success("Base creada correctamente.")
                    st.rerun()
    elif not bases_dict:
        st.warning("No hay bases creadas. Solicita a un administrador que cree la primera.")
        return

    if st.session_state.rol == "admin" and bases_dict:
        with st.expander("🗑️ Eliminar base"):
            base_eliminar = st.selectbox(
                "Base a eliminar", list(bases_dict.keys()), key="base_a_eliminar_importar"
            )
            confirmar_borrado = st.checkbox(
                "Confirmo eliminar la base {} y todos sus clientes".format(base_eliminar),
                key="confirmar_borrado_base_importar",
            )
            if st.button(
                "Eliminar Base", disabled=not confirmar_borrado, key="eliminar_base_importar"
            ):
                if len(bases_dict) <= 1:
                    st.error("No se puede eliminar la última base.")
                else:
                    id_base = bases_dict[base_eliminar]
                    supabase.table("clientes").delete().eq("base_id", id_base).execute()
                    supabase.table("bases").delete().eq("id", id_base).execute()
                    st.success("Base y clientes asociados eliminados.")
                    st.rerun()
    if not base_seleccionada:
        st.info("Crea una base para comenzar a importar clientes.")
        return

    st.markdown(
        f"""
        <div class="metric-card" style="margin-bottom:1rem;">
            <div style="font-size:.78rem;color:#64748b;font-weight:700;">BASE DESTINO</div>
            <div style="font-size:1.35rem;font-weight:800;color:#0f172a;">{texto_html(base_seleccionada)}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    columnas = ["placa", "cliente", "telefono", "sede", "fecha_renovacion", "estado"]
    campos_requeridos = ["placa", "cliente", "telefono", "fecha_renovacion"]

    archivo_excel = st.file_uploader(
        "Seleccione Excel o CSV de clientes", type=["xlsx", "xls", "csv"],
        key="importar_clientes_tab",
    )
    if archivo_excel is None:
        c1, c2, c3 = st.columns(3)
        with c1:
            render_metric("Campos reconocidos", len(columnas))
        with c2:
            render_metric("Base activa", base_seleccionada)
        with c3:
            render_metric("Formatos", "Excel / CSV")
        st.info("Puedes cargar Excel o CSV con columnas en cualquier orden. El sistema detecta nombres habituales y permite corregir el mapeo.")
        return

    try:
        contenido_archivo = archivo_excel.getvalue()
        archivo_id = "{}_{}".format(archivo_excel.name, archivo_excel.size)
        if archivo_excel.name.lower().endswith(".csv"):
            try:
                df_raw = pd.read_csv(BytesIO(contenido_archivo), header=None, sep=None, engine="python", dtype=object)
            except UnicodeDecodeError:
                df_raw = pd.read_csv(BytesIO(contenido_archivo), header=None, sep=None, engine="python", dtype=object, encoding="latin-1")
            hoja = "CSV"
        else:
            libro = pd.ExcelFile(BytesIO(contenido_archivo))
            hoja = st.selectbox("Hoja del archivo", libro.sheet_names, key="hoja_importar_{}".format(archivo_id))
            df_raw = pd.read_excel(BytesIO(contenido_archivo), sheet_name=hoja, header=None, dtype=object)

        if df_raw.empty:
            st.error("El archivo no contiene filas para leer.")
            return

        filas_revision = min(20, len(df_raw))
        evaluaciones = []
        for indice in range(filas_revision):
            mapa = mapear_encabezados(df_raw.iloc[indice].tolist())
            evaluaciones.append((len(mapa), indice))
        mejor_puntaje = max(puntaje for puntaje, _ in evaluaciones)
        fila_sugerida = next(indice for puntaje, indice in evaluaciones if puntaje == mejor_puntaje)

        def etiqueta_fila(indice):
            valores = [str(v) for v in df_raw.iloc[indice].tolist() if pd.notna(v)]
            return "Fila {}: {}".format(indice + 1, " | ".join(valores[:6])[:100])

        fila_encabezados = st.selectbox(
            "Fila donde están los encabezados", options=list(range(filas_revision)),
            index=fila_sugerida, format_func=etiqueta_fila,
            key="fila_encabezados_{}_{}".format(archivo_id, hoja),
        )
        encabezados_originales = df_raw.iloc[fila_encabezados].tolist()
        encabezados = nombres_columnas_unicos(encabezados_originales)
        df_importar = df_raw.iloc[fila_encabezados + 1:].copy().reset_index(drop=True)
        df_importar.columns = encabezados
        mapeo_auto = mapear_encabezados(encabezados_originales)

        st.subheader("Relaciona las columnas del archivo con los campos del CRM")
        st.caption("El orden no importa. Las columnas adicionales se ignorarán.")
        mapeo = {}
        opciones_columnas = ["— No usar —"] + encabezados
        columnas_mapeo = st.columns(3)
        for indice, campo in enumerate(columnas):
            with columnas_mapeo[indice % 3]:
                sugerida = mapeo_auto.get(campo)
                default_index = opciones_columnas.index(sugerida) if sugerida in opciones_columnas else 0
                mapeo[campo] = st.selectbox(
                    "{}{}".format(campo.replace("_", " ").title(), " *" if campo in campos_requeridos else ""),
                    opciones_columnas, index=default_index,
                    key="map_{}_{}_{}".format(campo, archivo_id, hoja),
                )

        faltantes = [campo for campo in campos_requeridos if mapeo[campo] == "— No usar —"]
        st.caption("* Obligatorios: placa, cliente, teléfono y fecha de renovación.")
        if faltantes:
            st.warning("Asigna una columna para: {}.".format(", ".join(faltantes)))
            st.dataframe(df_importar.head(10), use_container_width=True, hide_index=True)
            return

        df_limpio = pd.DataFrame(index=df_importar.index)
        for campo in columnas:
            fuente = mapeo[campo]
            if fuente == "— No usar —":
                df_limpio[campo] = "Pendiente" if campo == "estado" else ""
            else:
                df_limpio[campo] = df_importar[fuente]
        st.subheader("Vista previa del mapeo")
        st.dataframe(df_limpio.head(20), use_container_width=True, hide_index=True)
        df_limpio["placa"] = df_limpio["placa"].fillna("").astype(str).str.strip().str.upper()
        df_limpio["cliente"] = df_limpio["cliente"].fillna("").astype(str).str.strip()
        df_limpio["telefono"] = df_limpio["telefono"].fillna("").astype(str).str.strip()
        df_limpio["sede"] = df_limpio["sede"].fillna("").astype(str).str.strip()
        df_limpio["estado"] = (
            df_limpio["estado"]
            .replace(r"^\s*$", pd.NA, regex=True)
            .fillna("Pendiente")
            .astype(str)
            .str.strip()
            .str.title()
        )
        df_limpio["fecha_renovacion"] = df_limpio["fecha_renovacion"].apply(convertir_fecha_excel)
        estados_validos = {"Pendiente", "Agendado", "Renovado"}
        validas = (
            df_limpio["placa"].ne("") & df_limpio["cliente"].ne("")
            & df_limpio["telefono"].ne("") & df_limpio["fecha_renovacion"].notna()
            & df_limpio["estado"].isin(estados_validos)
        )
        rechazadas = int((~validas).sum())
        df_limpio = df_limpio.loc[validas].copy().drop_duplicates(subset=["placa"], keep="first")
        existentes = supabase.table("clientes").select("placa").eq("base_id", base_id).execute()
        placas_existentes = {str(x.get("placa", "")).strip().upper() for x in existentes.data}
        duplicados = df_limpio["placa"].isin(placas_existentes)
        rechazadas += int(duplicados.sum())
        df_limpio = df_limpio.loc[~duplicados].copy()
        df_limpio["fecha_renovacion"] = df_limpio["fecha_renovacion"].dt.strftime("%Y-%m-%d")
        df_limpio["base_id"] = base_id
        st.caption(f"Filas omitidas por datos inválidos o placa repetida: {rechazadas}.")
        st.success(f"{len(df_limpio)} clientes listos para importar en {base_seleccionada}.")

        if not df_limpio.empty and st.button("Importar clientes", use_container_width=True):
            st.session_state.confirmar_importacion = True
        if st.session_state.get("confirmar_importacion"):
            st.warning(f"Confirma la importación de {len(df_limpio)} clientes en {base_seleccionada}.")
            confirmar = st.checkbox("Confirmo que revisé los datos y deseo importarlos", key="confirmar_importacion_check")
            if st.button("Confirmar importación", disabled=not confirmar, use_container_width=True):
                registros = df_limpio.to_dict(orient="records")
                supabase.table("clientes").insert(registros).execute()
                st.session_state.confirmar_importacion = False
                st.success(f"{len(registros)} clientes importados correctamente")
                st.rerun()

    except Exception as e:
        st.error(str(e))


# ======================================================
# CLIENTES
# ======================================================

if base_id is not None:
    resultado = (
        supabase.table("clientes").select("*").eq("base_id", base_id).execute()
    )
    df = pd.DataFrame(resultado.data)
else:
    df = pd.DataFrame()

for columna, valor_defecto in {
    "placa": "",
    "cliente": "",
    "telefono": "",
    "sede": "",
    "estado": "Pendiente",
    "fecha_renovacion": pd.NaT,
}.items():
    if columna not in df.columns:
        df[columna] = valor_defecto

if not df.empty and "fecha_renovacion" in df.columns:
    df["fecha_renovacion"] = pd.to_datetime(
        df["fecha_renovacion"],
        errors="coerce",
    )


# ======================================================
# DASHBOARD
# ======================================================

if menu == "📊 Dashboard":
    header("Dashboard Ejecutivo", "📊")

    total = len(df)
    pendientes = (df["estado"] == "Pendiente").sum() if not df.empty else 0
    agendados = (df["estado"] == "Agendado").sum() if not df.empty else 0
    renovados = (df["estado"] == "Renovado").sum() if not df.empty else 0
    conversion = round((renovados / total) * 100, 2) if total > 0 else 0

    c1, c2, c3, c4, c5 = st.columns(5)
    with c1:
        render_metric("Clientes", total)
    with c2:
        render_metric("Pendientes", pendientes)
    with c3:
        render_metric("Agendados", agendados)
    with c4:
        render_metric("Renovados", renovados)
    with c5:
        render_metric("Conversión %", conversion)

    st.divider()

    if not df.empty:
        estados_df = df["estado"].value_counts().reset_index()
        estados_df.columns = ["Estado", "Cantidad"]

        col1, col2 = st.columns(2)

        with col1:
            fig = px.bar(estados_df, x="Estado", y="Cantidad", title="Estados")
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            fig2 = px.pie(estados_df, names="Estado", values="Cantidad", title="Distribución")
            st.plotly_chart(fig2, use_container_width=True)

        if "sede" in df.columns:
            sedes_df = df.groupby("sede").size().reset_index(name="Cantidad")
            fig3 = px.bar(sedes_df, x="sede", y="Cantidad", title="Clientes por sede")
            st.plotly_chart(fig3, use_container_width=True)

        hoy = pd.Timestamp.today().normalize()

        vencen_hoy = (df["fecha_renovacion"] == hoy).sum()
        vencen_7 = ((df["fecha_renovacion"] >= hoy) & (df["fecha_renovacion"] <= hoy + pd.Timedelta(days=7))).sum()
        vencen_30 = ((df["fecha_renovacion"] >= hoy) & (df["fecha_renovacion"] <= hoy + pd.Timedelta(days=30))).sum()

        a, b, c = st.columns(3)
        with a:
            render_metric("🔴 Hoy", int(vencen_hoy))
        with b:
            render_metric("🟠 Próximos 7 días", int(vencen_7))
        with c:
            render_metric("🟢 Próximos 30 días", int(vencen_30))
    else:
        st.info("No hay clientes en la base activa.")


# ======================================================
# CRM
# ======================================================

if menu == "📋 CRM":
    header("CRM - Clientes", "📋")

    busqueda = st.text_input(
        "Buscar placa, cliente o teléfono",
        placeholder="Buscar placa, cliente o teléfono",
        label_visibility="collapsed",
    )

    st.markdown('<div class="filter-row">', unsafe_allow_html=True)
    f1, f2, f3, f4 = st.columns(4)

    with f1:
        if st.button("🔴 Pendientes", use_container_width=True):
            st.session_state.filtro_estado = "Pendiente"
            st.session_state.pagina_clientes = 1

    with f2:
        if st.button("🟠 Agendados", use_container_width=True):
            st.session_state.filtro_estado = "Agendado"
            st.session_state.pagina_clientes = 1

    with f3:
        if st.button("🟢 Renovados", use_container_width=True):
            st.session_state.filtro_estado = "Renovado"
            st.session_state.pagina_clientes = 1

    with f4:
        if st.button("🔄 Todos", use_container_width=True):
            st.session_state.filtro_estado = "Todos"
            st.session_state.pagina_clientes = 1
    st.markdown("</div>", unsafe_allow_html=True)

    if df.empty:
        st.info("No hay clientes en la base activa.")
        st.stop()

    if busqueda:
        filtro = (
            df["cliente"].fillna("").astype(str).str.contains(busqueda, case=False, na=False)
            |
            df["placa"].fillna("").astype(str).str.contains(busqueda, case=False, na=False)
            |
            df["telefono"].fillna("").astype(str).str.contains(busqueda, case=False, na=False)
        )

        df = df[filtro]

        if df.empty:
            st.warning("No se encontraron clientes")
            st.stop()

    if st.session_state.filtro_estado != "Todos":
        df = df[df["estado"] == st.session_state.filtro_estado]

    col_f1, col_f2, col_f3, col_export = st.columns([1.2, 1.2, 1.2, 1])

    fechas_validas = df["fecha_renovacion"].dropna()
    fecha_min = fechas_validas.min().date() if not fechas_validas.empty else pd.Timestamp.today().date()
    fecha_max = fechas_validas.max().date() if not fechas_validas.empty else pd.Timestamp.today().date()

    with col_f1:
        fecha_inicio = st.date_input("Desde", fecha_min)

    with col_f2:
        fecha_fin = st.date_input("Hasta", fecha_max)

    with col_f3:
        sedes = ["Todas"]
        if "sede" in df.columns:
            sedes += sorted(df["sede"].dropna().unique().tolist())
        sede_sel = st.selectbox("Sede", sedes)

    df_filtrado = df[
        (df["fecha_renovacion"] >= pd.Timestamp(fecha_inicio))
        &
        (df["fecha_renovacion"] <= pd.Timestamp(fecha_fin))
    ]

    if sede_sel != "Todas":
        df_filtrado = df_filtrado[df_filtrado["sede"] == sede_sel]

    with st.expander("📣 Envío masivo de renovaciones por WhatsApp"):
        config_wa = configuracion_whatsapp()
        if not config_wa["token"] or not config_wa["phone_id"]:
            st.warning("Falta configurar WhatsApp Business API en los secretos de Streamlit.")
            st.code(
                'WHATSAPP_ACCESS_TOKEN = "tu_token_permanente"\n'
                'WHATSAPP_PHONE_NUMBER_ID = "id_del_numero"\n'
                'WHATSAPP_TEMPLATE_NAME = "recordatorio_renovacion"\n'
                'WHATSAPP_TEMPLATE_LANGUAGE = "es_CO"\n'
                'WHATSAPP_API_VERSION = "v27.0"',
                language="toml",
            )
        else:
            candidatos = df_filtrado[
                df_filtrado["estado"].fillna("Pendiente").astype(str).str.lower() != "renovado"
            ].copy()
            candidatos["_telefono_api"] = candidatos["telefono"].apply(telefono_limpio)
            candidatos["_telefono_api"] = candidatos["_telefono_api"].apply(
                lambda t: t if t.startswith("57") else "57" + t
            )
            validos_telefono = candidatos["_telefono_api"].apply(
                lambda t: t.isdigit() and 11 <= len(t) <= 15
            )
            omitidos = int((~validos_telefono).sum())
            candidatos = candidatos.loc[validos_telefono].copy()
            st.caption(
                "Se consideran clientes no renovados dentro de los filtros actuales. "
                "Se excluirán números vacíos o inválidos ({}).".format(omitidos)
            )
            if candidatos.empty:
                st.info("No hay clientes pendientes con teléfono válido en este filtro.")
            else:
                opciones_ids = [str(row["id"]) for _, row in candidatos.iterrows()]
                lookup_clientes = {
                    str(row["id"]): row for _, row in candidatos.iterrows()
                }
                seleccionados = st.multiselect(
                    "Selecciona los destinatarios",
                    options=opciones_ids,
                    format_func=lambda cliente_id: "{} · {} · {}".format(
                        lookup_clientes[cliente_id].get("placa", ""),
                        lookup_clientes[cliente_id].get("cliente", ""),
                        lookup_clientes[cliente_id]["fecha_renovacion"].strftime("%d/%m/%Y")
                        if pd.notna(lookup_clientes[cliente_id].get("fecha_renovacion"))
                        else "Sin fecha",
                    ),
                    key="destinatarios_whatsapp_renovacion",
                )
                if seleccionados:
                    vista = pd.DataFrame([lookup_clientes[i] for i in seleccionados])
                    st.dataframe(
                        vista[["placa", "cliente", "telefono", "fecha_renovacion"]],
                        use_container_width=True,
                        hide_index=True,
                    )
                    st.info(
                        "La plantilla aprobada debe tener tres variables en el cuerpo, en este orden: "
                        "nombre del cliente, placa y fecha de vencimiento."
                    )
                    consentimiento = st.checkbox(
                        "Confirmo que estos clientes autorizaron recibir mensajes por WhatsApp.",
                        key="confirmar_optin_whatsapp",
                    )
                    if st.button(
                        "Enviar {} recordatorio(s)".format(len(seleccionados)),
                        disabled=not consentimiento,
                        type="primary",
                        key="enviar_renovaciones_whatsapp",
                    ):
                        enviados = []
                        fallidos = []
                        no_registrados = []
                        barra = st.progress(0, text="Enviando mensajes...")
                        for posicion, cliente_id in enumerate(seleccionados, start=1):
                            fila = lookup_clientes[cliente_id]
                            fecha_valor = fila.get("fecha_renovacion")
                            fecha_texto = fecha_valor.strftime("%d/%m/%Y") if pd.notna(fecha_valor) else ""
                            try:
                                message_id = enviar_plantilla_whatsapp(
                                    fila.get("telefono", ""),
                                    fila.get("cliente", ""),
                                    fila.get("placa", ""),
                                    fecha_texto,
                                )
                            except Exception as error:
                                fallidos.append({"cliente": fila.get("cliente", ""), "error": str(error)})
                            else:
                                enviados.append(fila.get("cliente", ""))
                                try:
                                    supabase.table("gestiones").insert({
                                        "cliente_id": fila["id"],
                                        "observacion": "Recordatorio de renovación enviado por WhatsApp. ID: {}".format(message_id),
                                    }).execute()
                                except Exception:
                                    no_registrados.append(fila.get("cliente", ""))
                            barra.progress(posicion / len(seleccionados), text="Procesados {} de {}".format(posicion, len(seleccionados)))
                        if enviados:
                            st.success("WhatsApp aceptó {} mensaje(s).".format(len(enviados)))
                        if fallidos:
                            st.error("No se pudieron enviar {} mensaje(s).".format(len(fallidos)))
                            st.dataframe(pd.DataFrame(fallidos), use_container_width=True, hide_index=True)
                        if no_registrados:
                            st.warning("Algunos envíos se completaron, pero no se pudieron anotar en el historial: {}.".format(", ".join(no_registrados)))
                        st.rerun()

    with col_export:
        excel = convertir_excel(df_filtrado)
        st.download_button(
            label="📥 Excel",
            data=excel,
            file_name="clientes_filtrados.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True,
        )

    total_filtrado = len(df_filtrado)
    por_pagina = st.selectbox(
        "Clientes por página", [10, 20, 50], index=0, key="clientes_por_pagina"
    )
    total_paginas = max(1, math.ceil(total_filtrado / por_pagina))
    st.session_state.pagina_clientes = min(st.session_state.pagina_clientes, total_paginas)
    inicio = (st.session_state.pagina_clientes - 1) * por_pagina
    fin = inicio + por_pagina

    estados = ["Pendiente", "Agendado", "Renovado"]

    for index, row in df_filtrado.iloc[inicio:fin].iterrows():
        estado_actual = row.get("estado", "Pendiente")
        if estado_actual not in estados:
            estado_actual = "Pendiente"

        placa = row.get("placa", "")
        cliente = row.get("cliente", "")
        placa_html = texto_html(placa)
        cliente_html = texto_html(cliente)
        vencimiento = row.get("fecha_renovacion")
        vencimiento_texto = vencimiento.strftime("%d/%m/%Y") if pd.notna(vencimiento) else "Sin fecha"
        vencimiento_html = texto_html(vencimiento_texto)
        telefono = telefono_limpio(row.get("telefono", ""))
        url = link_whatsapp(cliente, placa, telefono)
        nota = texto_html(ultima_observacion(row["id"]))
        estado_html = texto_html(estado_actual)

        cliente_id_gestion = str(row["id"])
        with st.container(border=True):
            col_principal, col_vencimiento, col_estado, col_whatsapp, col_llamar, col_gestion = st.columns(
                [4.2, 1.45, 1.35, 1.0, 1.0, 1.05]
            )
            with col_principal:
                st.markdown(
                    f'<div class="client-main"><div class="vehicle-avatar" style="background:{color_avatar(index)};">🚗</div><div style="min-width:0;"><div class="plate">{placa_html}</div><div class="client-name">{cliente_html}</div><div class="last-note">📝 {nota}</div></div></div>',
                    unsafe_allow_html=True,
                )
            with col_vencimiento:
                st.markdown(
                    f'<div class="card-separator"><div class="cell-title">Vencimiento</div><div class="due-date">{vencimiento_html}</div></div>',
                    unsafe_allow_html=True,
                )
            with col_estado:
                st.markdown(
                    f'<div class="card-separator"><div class="cell-title">Estado</div><span class="status-pill {estado_clase(estado_actual)}">{estado_html}</span></div>',
                    unsafe_allow_html=True,
                )
            with col_whatsapp:
                st.markdown(
                    f'<a class="action-link" href="{url}" target="_blank"><span class="action-icon action-whatsapp"><svg viewBox="0 0 32 32" role="img" aria-label="WhatsApp"><path fill="white" d="M16 3.2c-6.8 0-12.3 5.2-12.3 11.6 0 2.2.7 4.2 1.9 5.9l-1.3 6.1 6.2-1.6c1.7.8 3.6 1.2 5.5 1.2 6.8 0 12.3-5.2 12.3-11.6S22.8 3.2 16 3.2z"/><path fill="none" stroke="#16a34a" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round" d="M11 9.5c-.5 0-.9.2-1.2.6-.4.5-1.2 1.5-1.2 3.1 0 1.9 1.5 4.2 3.5 6.1 2.1 2 4.7 3.3 6.1 3.4 1.5.1 2.4-.4 2.9-1 .4-.5.6-1.2.4-1.5-.2-.2-.7-.4-1.4-.7l-2.1-1c-.5-.2-.8-.1-1.1.3l-.9 1.1c-.2.2-.5.3-.9.1-1.5-.6-3-1.6-4.1-2.9-.3-.4-.3-.7-.1-.9l.7-.8c.3-.3.3-.7.1-1.1l-1-2.3c-.3-.8-.6-1.3-1.1-1.3z"/></svg></span><span>WhatsApp</span></a>',
                    unsafe_allow_html=True,
                )
            with col_llamar:
                st.markdown(
                    f'<a class="action-link" href="tel:+57{texto_html(telefono)}"><span class="action-icon action-call">☎</span><span>Llamar</span></a>',
                    unsafe_allow_html=True,
                )
            with col_gestion:
                if st.button(
                    "📋 Gestión",
                    key="abrir_gestion_{}".format(cliente_id_gestion),
                    use_container_width=True,
                ):
                    st.session_state.cliente_gestion_activa = cliente_id_gestion
        if st.session_state.get("cliente_gestion_activa") == cliente_id_gestion:
            st.markdown("#### 📋 Gestión - {}".format(texto_html(placa)))
            col_estado, col_obs = st.columns([1, 2])
            with col_estado:
                nuevo_estado = st.selectbox(
                    "Estado",
                    estados,
                    index=estados.index(estado_actual),
                    key="estado_gestion_{}".format(cliente_id_gestion),
                )
            with col_obs:
                version_form = st.session_state.get("version_form_gestion", 0)
                observacion = st.text_area(
                    "Observación",
                    key="obs_gestion_{}_{}".format(cliente_id_gestion, version_form),
                )

            guardar_col, cerrar_col = st.columns([1, 1])
            with guardar_col:
                guardar = st.button(
                    "Guardar gestión",
                    key="guardar_gestion_{}".format(cliente_id_gestion),
                    use_container_width=True,
                )
            with cerrar_col:
                cerrar = st.button(
                    "Cerrar",
                    key="cerrar_gestion_{}".format(cliente_id_gestion),
                    use_container_width=True,
                )

            if guardar:
                if nuevo_estado == estado_actual and not observacion.strip():
                    st.warning("Cambia el estado o escribe una observación para guardar.")
                else:
                    if nuevo_estado != estado_actual:
                        supabase.table("clientes").update({"estado": nuevo_estado}).eq(
                            "id", row["id"]
                        ).execute()
                    if observacion.strip():
                        supabase.table("gestiones").insert({
                            "cliente_id": row["id"],
                            "observacion": observacion.strip(),
                        }).execute()
                    st.session_state.version_form_gestion = version_form + 1
                    st.success("Gestión guardada.")
                    st.rerun()

            if cerrar:
                st.session_state.cliente_gestion_activa = ""
                st.rerun()

            historial = (
                supabase.table("gestiones").select("*")
                .eq("cliente_id", row["id"]).order("fecha", desc=True).execute()
            )
            if historial.data:
                st.write("**Historial de gestiones**")
                for gestion in historial.data:
                    fecha_gestion = str(gestion.get("fecha", ""))[:10]
                    st.write("📅 {} — {}".format(fecha_gestion, gestion.get("observacion", "")))

    if total_filtrado == 0:
        st.info("No hay clientes con los filtros seleccionados.")
    else:
        desde = inicio + 1
        hasta = min(fin, total_filtrado)
        st.caption(f"Mostrando {desde} a {hasta} de {total_filtrado} clientes")
        render_pagination(total_filtrado, por_pagina)


# ======================================================
# IMPORTAR BASE
# ======================================================

if menu == "📥 Importar Base":
    pantalla_importar_base()


# ======================================================
# ADMINISTRACION
# ======================================================

if menu == "👥 Administración":
    header("Administración", "👥")

    if st.session_state.rol != "admin":
        st.warning("No tienes permisos para acceder.")

    else:
        st.subheader("Usuarios")

        usuarios = (
            supabase
            .table("usuarios")
            .select("*")
            .execute()
        )

        df_usuarios = pd.DataFrame([{k: v for k, v in u.items() if k != "password"} for u in usuarios.data])

        st.dataframe(
            df_usuarios,
            use_container_width=True,
        )

        st.divider()

        st.subheader("Eliminar usuario")

        opciones = [
            u["usuario"]
            for u in usuarios.data
            if u["usuario"] != "admin"
        ]

        if opciones:
            usuario_eliminar = st.selectbox(
                "Seleccione usuario",
                opciones,
            )

            if st.button("Eliminar usuario"):
                supabase.table("usuarios").delete().eq(
                    "usuario",
                    usuario_eliminar,
                ).execute()

                st.success("Usuario eliminado")
                st.rerun()

        st.divider()

        st.subheader("Crear usuario")

        nuevo_usuario = st.text_input("Usuario nuevo")
        nuevo_password = st.text_input("Contraseña nueva", type="password")
        nuevo_rol = st.selectbox("Rol", ["admin", "asesor"])

        if st.button("Crear usuario"):
            usuario_limpio = nuevo_usuario.strip()
            if not usuario_limpio or not nuevo_password:
                st.error("Escribe un usuario y una contraseña.")
            elif len(nuevo_password) < 10:
                st.error("La contraseña debe tener al menos 10 caracteres.")
            else:
                existente = supabase.table("usuarios").select("usuario").eq(
                    "usuario", usuario_limpio
                ).limit(1).execute()
                if existente.data:
                    st.error("Ese usuario ya existe.")
                else:
                    supabase.table("usuarios").insert({
                        "usuario": usuario_limpio,
                        "password": hash_password(nuevo_password),
                        "rol": nuevo_rol,
                    }).execute()
                    st.success("Usuario creado correctamente")
                    st.rerun()






