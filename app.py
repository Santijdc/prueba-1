import streamlit as st
import pandas as pd
from datetime import date, datetime
import os
import numpy as np
import locale

# Configuración regional para obtener el día de la semana
try:
    locale.setlocale(locale.LC_TIME, 'es_ES.UTF-8')
except locale.Error:
    pass 

# --- 1. Configuración de la página ---
st.set_page_config(page_title="Mi Diario de Gym", page_icon="🏋️‍♂️", layout="wide")
st.title("🏋️‍♂️ Registro de Entrenamientos")

ARCHIVO_DATOS = "entrenamientos.csv"

# Nombres de Usuarios
USUARIOS = ["Santi", "Mel"]

# ACTUALIZACIÓN: Definición de las rutinas semanales (CON SERIES)
# La rutina ahora es una lista de diccionarios: [{"name": "Ejercicio", "series": 4}, ...]
DICT_RUTINAS = {
    "Santi": {
        "Monday": [
            {"name": "Press Inclinado Barra", "series": 4},
            {"name": "Press Inclinado Máquina", "series": 4},
            {"name": "Press Plano Máquina", "series": 4}, 
            {"name": "Triceps Tras Nuca", "series": 4}, 
            {"name": "Elevaciones Laterales Polea", "series": 4},
        ],
        "Tuesday": [
            {"name": "Sentadilla", "series": 3},
            {"name": "Femoral Sentado", "series": 4},
            {"name": "Prensa", "series": 3},
            {"name": "Sillón Cuádriceps", "series": 3},
            {"name": "Gemelo", "series": 4},
        ],
        "Wednesday": [
            {"name": "Jalón al Pecho", "series": 4},
            {"name": "Remo Máquina", "series": 4},
            {"name": "Remo Gironda", "series": 4},
            {"name": "Bíceps con Barra", "series": 4},
            {"name": "Elevaciones Laterales Polea", "series": 4},
        ],
        "Thursday": [
            {"name": "Press Inclinado Barra", "series": 4},
            {"name": "Jalón al Pecho", "series": 4},
            {"name": "Posterior en Polea", "series": 4},
            {"name": "Triceps Tras Nuca", "series": 4},
            {"name": "Bíceps en Polea", "series": 4},
            {"name": "Elevaciones Laterales Polea", "series": 4},
        ],
        "Friday": [
            {"name": "Peso Muerto Rumano", "series": 3},
            {"name": "Prensa", "series": 3},
            {"name": "Camilla Femorales", "series": 4},
            {"name": "Sillón Cuádriceps", "series": 4},
        ],
        "Saturday": [{"name": "Descanso", "series": 0}],
        "Sunday": [{"name": "Descanso", "series": 0}]
    },
    "Mel": {
        "Monday": [{"name": "Descanso", "series": 0}],
        "Tuesday": [{"name": "Descanso", "series": 0}],
        "Wednesday": [{"name": "Descanso", "series": 0}],
        "Thursday": [{"name": "Descanso", "series": 0}],
        "Friday": [{"name": "Descanso", "series": 0}],
        "Saturday": [{"name": "Descanso", "series": 0}],
        "Sunday": [{"name": "Descanso", "series": 0}]
    }
}

def cargar_datos():
    if os.path.exists(ARCHIVO_DATOS):
        df = pd.read_csv(ARCHIVO_DATOS)
        df['Fecha'] = pd.to_datetime(df['Fecha']).dt.date
        
        df['Volumen (kg)'] = df['Peso (kg)'] * df['Reps']
        
        if 'Usuario' not in df.columns:
            df['Usuario'] = USUARIOS[0] 
        
        return df.sort_values(by='Fecha', ascending=False).reset_index()
    else:
        # Quitamos "Notas" de las columnas de inicialización
        return pd.DataFrame(columns=["index", "Usuario", "Fecha", "Ejercicio", "Peso (kg)", "Reps", "Volumen (kg)"])

df = cargar_datos()

# --- LÓGICA DE RUTINA DEL DÍA ---
hoy = datetime.now()
dia_semana_ingles = hoy.strftime('%A')
dia_semana_espanol = hoy.strftime('%A').capitalize()
fecha_actual = hoy.strftime('%d/%m/%Y')


# --- 2. Menú lateral ---
st.sidebar.header("Menú")

usuario_activo = st.sidebar.selectbox("👤 ¿Quién registra/consulta?", USUARIOS)

menu = st.sidebar.radio("Elige una opción:", ["✍️ Registrar Rutina", "📊 Ver Historial"])

if menu == "✍️ Registrar Rutina":
    
    # Obtener la rutina del día (lista de diccionarios)
    ejercicios_del_dia = DICT_RUTINAS[usuario_activo].get(dia_semana_ingles, [{"name": "Descanso", "series": 0}])
    
    st.subheader(f"🗓️ {dia_semana_espanol}, {fecha_actual}")
    
    # NUEVA LÓGICA: Construir la lista de ejercicios para mostrar y para el selectbox
    
    if ejercicios_del_dia[0]["name"] == "Descanso":
         st.info(f"¡Hola {usuario_activo}! Hoy es **{dia_semana_espanol}**. Te toca: **¡Descanso!** 🧘")
         ejercicios_opciones = ["Descanso"]
         rutina_display_partes = []
    else:
        # Construye la cadena de texto para mostrar (ej: Press Inclinado Barra (4 series))
        rutina_display_partes = [f"**{e['name']}** ({e['series']} series)" for e in ejercicios_del_dia]
        rutina_display = ", ".join(rutina_display_partes)
        st.info(f"¡Hola {usuario_activo}! Hoy te toca: {rutina_display}")
        
        # Lista solo con los nombres para el selectbox
        ejercicios_opciones = [e["name"] for e in ejercicios_del_dia]


    # --- Formulario de Registro ---
    st.subheader(f"Registro de Serie")
    
    with st.form("registro_form"):
        col1, col2 = st.columns(2) 
        
        with col1:
            fecha = st.date_input("Fecha", date.today(), key='date')
            
            # FILTRADO DE EJERCICIOS
            ejercicio = st.selectbox("Ejercicio", ejercicios_opciones, key='ej')
        
        with col2:
            peso = st.number_input("Peso (kg)", min_value=0.0, step=0.5, key='peso')
            reps = st.number_input("Repeticiones", min_value=1, step=1, key='reps')

        st.markdown("---")
        guardar_button = st.form_submit_button("✅ Guardar Serie")

        if guardar_button and ejercicio != "Descanso":
            nuevo_registro = pd.DataFrame({
                "Usuario": [usuario_activo],
                "Fecha": [fecha],
                "Ejercicio": [ejercicio],
                "Peso (kg)": [peso],
                "Reps": [reps],
                "Notas": [" "], 
            })
            
            df = pd.concat([df, nuevo_registro], ignore_index=True)
            df.to_csv(ARCHIVO_DATOS, index=False)
            
            st.success(f"¡Entrenamiento de {usuario_activo} guardado con éxito!")
        elif guardar_button and ejercicio == "Descanso":
             st.warning("No puedes registrar una serie si seleccionas 'Descanso'.")


# --- 3. OPCIÓN B: VER HISTORIAL ---
elif menu == "📊 Ver Historial":
    
    df_usuario = df[df['Usuario'] == usuario_activo]
    
    st.subheader(f"Tu Progreso Detallado: {usuario_activo}")
    
    if df_usuario.empty:
        st.info(f"Aún no tienes registros, {usuario_activo}.")
    else:
        # A. FILTRADO SECUNDARIO Y MÉTRICAS
        ejercicios_unicos = df_usuario['Ejercicio'].unique().tolist()
        ejercicio_elegido = st.selectbox("Filtrar por Ejercicio:", ["TODOS"] + ejercicios_unicos)
        
        df_filtrado = df_usuario
        if ejercicio_elegido != "TODOS":
            df_filtrado = df_usuario[df_usuario['Ejercicio'] == ejercicio_elegido]

        df_filtrado = df_filtrado.reset_index()

        col_metrica1, col_metrica2, col_metrica3, col_metrica4 = st.columns(4)
        
        with col_metrica1:
            st.metric(label="Total de Series", value=f"{len(df_filtrado)} Series")
        
        with col_metrica2:
            max_peso = df_filtrado['Peso (kg)'].max() if not df_filtrado.empty else 0
            st.metric(label="Peso Máximo (kg)", value=f"{max_peso} kg")
            
        with col_metrica3:
            if not df_usuario.empty: 
                 ultima_fecha = df_usuario['Fecha'].iloc[0].strftime('%d %b')
            else:
                 ultima_fecha = "N/A"
            st.metric(label="Último Entrenamiento", value=ultima_fecha)

        with col_metrica4:
            volumen_total = df_filtrado['Volumen (kg)'].sum() if not df_filtrado.empty else 0
            st.metric(label="Volumen Total (kg)", value=f"{volumen_total:,.0f} kg")

        st.markdown("---")
        st.write(f"Historial de {ejercicio_elegido} para {usuario_activo}:")
        
        # B. TABLA CON ÍNDICES PARA ELIMINAR
        df_mostrar = df_filtrado[['index', 'Fecha', 'Ejercicio', 'Peso (kg)', 'Reps', 'Volumen (kg)']]
        df_mostrar = df_mostrar.rename(columns={'index': 'ID'})

        st.dataframe(df_mostrar, use_container_width=True, hide_index=True)
        
        # C. SECCIÓN DE ELIMINACIÓN
        st.markdown("---")
        st.error(f"🚨 ¿Quieres eliminar un registro de {usuario_activo}?")
        
        opciones_id = df_mostrar['ID'].tolist()
        
        if opciones_id:
            col_del1, col_del2 = st.columns([1, 4])
            
            with col_del1:
                id_a_eliminar = st.selectbox("Selecciona el ID a eliminar:", opciones_id)
            
            with col_del2:
                st.markdown('<br>', unsafe_allow_html=True)
                if st.button(f"🔴 CONFIRMAR ELIMINACIÓN de ID {id_a_eliminar}"):
                    df = df.drop(index=id_a_eliminar).reset_index(drop=True)
                    
                    df.to_csv(ARCHIVO_DATOS, index=False)
                    st.warning(f"✅ ¡Registro ID {id_a_eliminar} de {usuario_activo} eliminado! Presiona F5 para actualizar.")
        else:
            st.info(f"No hay registros para eliminar en este filtro para {usuario_activo}.")

        # D. Gráfico
        if ejercicio_elegido != "TODOS" and len(df_filtrado) > 1:
            st.markdown("### Gráfico de Progreso") # CORRECCIÓN APLICADA AQUÍ
            st.line_chart(df_filtrado.set_index('Fecha')['Peso (kg)'])
