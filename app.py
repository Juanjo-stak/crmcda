import math
import urllib.parse
from io import BytesIO
from html import escape

import pandas as pd
import plotly.express as px
import streamlit as st
from supabase_config import supabase


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
            supabase
            .table("usuarios")
            .select("*")
            .eq("usuario", usuario)
            .eq("password", password)
            .execute()
        )

        if len(resultado.data) > 0:
            datos = resultado.data[0]

            st.session_state.login = True
            st.session_state.usuario = datos["usuario"]
            st.session_state.rol = datos["rol"]

            st.rerun()

        else:
            st.error("Usuario o contraseña incorrectos")


# ======================================================
# CONFIGURACION
# ======================================================

st.set_page_config(
    page_title="CRM CDA",
    page_icon="🚗",
    layout="wide",
    initial_sidebar_state="expanded",
)

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

    .action-whatsapp{
        background:linear-gradient(145deg,#22c55e,#16a34a);
    }

    .action-call{
        background:linear-gradient(145deg,#3b82f6,#2563eb);
    }

    .manage-button{
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

if not bases_dict:
    st.error("No hay bases creadas. Crea una base en Supabase antes de continuar.")
    st.stop()

st.sidebar.divider()
st.sidebar.caption("BASE ACTIVA")

base_seleccionada = st.sidebar.selectbox(
    "Base activa",
    list(bases_dict.keys()),
    label_visibility="collapsed",
)

base_id = bases_dict[base_seleccionada]

st.sidebar.markdown(
    f"""
    <div class="sidebar-footer">
        <div class="user-chip">👤 {st.session_state.usuario}</div>
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
    telefono = telefono.replace("-", "")

    if not telefono.startswith("57"):
        telefono = "57" + telefono

    mensaje = f"""
Hola {nombre}

Te escribimos del CDA Occidente.

Tu vehículo con placa {placa} tiene vencimiento próximo.

¿Deseas agendar tu revisión?
"""

    mensaje = urllib.parse.quote(mensaje)

    return f"https://wa.me/{telefono}?text={mensaje}"


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
            <div class="user-chip">👤 {st.session_state.usuario}</div>
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
    telefono = telefono.replace("-", "")
    return telefono


def texto_html(valor):
    return escape(str(valor or ""))


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


def pantalla_importar_base():
    header("Importar Base de Clientes", "📥")

    st.markdown(
        f"""
        <div class="metric-card" style="margin-bottom:1rem;">
            <div style="font-size:.78rem;color:#64748b;font-weight:700;">BASE DESTINO</div>
            <div style="font-size:1.35rem;font-weight:800;color:#0f172a;">{texto_html(base_seleccionada)}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    columnas = [
        "placa",
        "cliente",
        "telefono",
        "sede",
        "fecha_renovacion",
        "estado",
    ]

    archivo_excel = st.file_uploader(
        "Seleccione archivo Excel",
        type=["xlsx", "xls"],
        key="importar_clientes_tab",
    )

    if archivo_excel is None:
        c1, c2, c3 = st.columns(3)
        with c1:
            render_metric("Columnas requeridas", len(columnas))
        with c2:
            render_metric("Base activa", base_seleccionada)
        with c3:
            render_metric("Estados válidos", "3")

        st.info("Carga un archivo Excel con las columnas: placa, cliente, telefono, sede, fecha_renovacion y estado.")
        return

    try:
        df_importar = pd.read_excel(archivo_excel)

        total_filas = len(df_importar)
        faltantes = [
            c for c in columnas
            if c not in df_importar.columns
        ]

        c1, c2, c3 = st.columns(3)
        with c1:
            render_metric("Filas detectadas", total_filas)
        with c2:
            render_metric("Columnas", len(df_importar.columns))
        with c3:
            render_metric("Faltantes", len(faltantes))

        st.subheader("Vista previa")
        st.dataframe(df_importar.head(20), use_container_width=True)

        if faltantes:
            st.error(f"Faltan columnas: {', '.join(faltantes)}")
            return

        df_limpio = df_importar[columnas].copy()
        df_limpio = df_limpio.dropna(how="all")
        df_limpio["estado"] = df_limpio["estado"].fillna("Pendiente")
        df_limpio["fecha_renovacion"] = pd.to_datetime(
            df_limpio["fecha_renovacion"],
            errors="coerce",
        )
        df_limpio = df_limpio.dropna(subset=["fecha_renovacion"])
        df_limpio["fecha_renovacion"] = df_limpio["fecha_renovacion"].dt.strftime("%Y-%m-%d")
        df_limpio["base_id"] = base_id

        st.success(f"{len(df_limpio)} clientes listos para importar en {base_seleccionada}.")

        if st.button("Importar clientes", use_container_width=True):
            registros = df_limpio.to_dict(orient="records")

            supabase.table("clientes").insert(registros).execute()

            st.success(f"{len(registros)} clientes importados correctamente")
            st.rerun()

    except Exception as e:
        st.error(str(e))


# ======================================================
# CLIENTES
# ======================================================

resultado = (
    supabase
    .table("clientes")
    .select("*")
    .eq("base_id", base_id)
    .execute()
)

df = pd.DataFrame(resultado.data)

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
    por_pagina = 5
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

        st.markdown(
            f"""
            <div class="client-card">
                <div class="client-card-grid">
                    <div class="client-main">
                        <div class="vehicle-avatar" style="background:{color_avatar(index)};">🚗</div>
                        <div style="min-width:0;">
                            <div class="plate">{placa_html}</div>
                            <div class="client-name">{cliente_html}</div>
                            <div class="last-note">📝 {nota}</div>
                        </div>
                    </div>
                    <div class="card-separator">
                        <div class="cell-title">Vencimiento</div>
                        <div class="due-date">{vencimiento_html}</div>
                    </div>
                    <div class="card-separator">
                        <div class="cell-title">Estado</div>
                        <span class="status-pill {estado_clase(estado_actual)}">{estado_html}</span>
                    </div>
                    <a class="action-link" href="{url}" target="_blank">
                        <span class="action-icon action-whatsapp">☏</span>
                        <span>WhatsApp</span>
                    </a>
                    <a class="action-link" href="tel:+57{telefono}">
                        <span class="action-icon action-call">☎</span>
                        <span>Llamar</span>
                    </a>
                    <div class="manage-button">
                        <div style="font-size:1.45rem;">📋</div>
                        <div>Gestión</div>
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        with st.expander(f"📋 Gestión - {placa}"):
            col_estado, col_obs = st.columns([1, 2])

            with col_estado:
                nuevo_estado = st.selectbox(
                    "Estado",
                    estados,
                    index=estados.index(estado_actual),
                    key=f"estado_nuevo_{row['id']}",
                )

                if nuevo_estado != row["estado"]:
                    supabase.table("clientes").update({"estado": nuevo_estado}).eq("id", row["id"]).execute()
                    st.rerun()

            with col_obs:
                observacion = st.text_area("Observación", key=f"obs_nueva_{row['id']}")

            if st.button("Guardar gestión", key=f"guardar_nueva_{row['id']}", use_container_width=True):
                if observacion:
                    supabase.table("gestiones").insert({
                        "cliente_id": row["id"],
                        "observacion": observacion,
                    }).execute()

                    st.success("Gestión guardada")
                    st.rerun()
                else:
                    st.warning("Escribe una observación antes de guardar.")

            historial = (
                supabase
                .table("gestiones")
                .select("*")
                .eq("cliente_id", row["id"])
                .order("fecha", desc=True)
                .execute()
            )

            if len(historial.data) > 0:
                st.write("### Historial")

                for g in historial.data:
                    st.write(f"📅 {g['fecha'][:10]} - {g['observacion']}")


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

        df_usuarios = pd.DataFrame(usuarios.data)

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

        st.subheader("Bases")

        nombre_base = st.text_input("Nombre de la nueva base")

        if st.button("Crear Base"):
            if nombre_base:
                supabase.table("bases").insert({
                    "nombre": nombre_base,
                }).execute()

                st.success("Base creada")
                st.rerun()

        base_eliminar = st.selectbox(
            "Eliminar base",
            list(bases_dict.keys()),
        )

        if st.button("Eliminar Base"):
            if len(bases_dict) <= 1:
                st.error("No se puede eliminar la última base.")
            else:
                id_base = bases_dict[base_eliminar]

                supabase.table("clientes").delete().eq(
                    "base_id",
                    id_base,
                ).execute()

                supabase.table("bases").delete().eq(
                    "id",
                    id_base,
                ).execute()

                st.success("Base eliminada")
                st.rerun()

        st.divider()

        st.subheader("Crear usuario")

        nuevo_usuario = st.text_input("Usuario nuevo")
        nuevo_password = st.text_input("Contraseña nueva", type="password")
        nuevo_rol = st.selectbox("Rol", ["admin", "asesor"])

        if st.button("Crear usuario"):
            supabase.table("usuarios").insert({
                "usuario": nuevo_usuario,
                "password": nuevo_password,
                "rol": nuevo_rol,
            }).execute()

            st.success("Usuario creado correctamente")
            st.rerun()


