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

# Archivos de datos
ARCHIVO_DATOS = "entrenamientos.csv"
ARCHIVO_PROGRESOS = "progresos.csv" # NUEVO: Archivo para peso y medidas

# Nombres de Usuarios
USUARIOS = ["Santi", "Mel"]

# Definición de las rutinas semanales (CON SERIES Y DESCANSO)
DICT_RUTINAS = {
    "Santi": {
        "Monday": [
            {"name": "Press Inclinado Barra", "series": 4, "rest": "1:30"},
            {"name": "Press Inclinado Máquina", "series": 4, "rest": "1:30"},
            {"name": "Press Plano Máquina", "series": 4, "rest": "1:30"}, 
            {"name": "Triceps Tras Nuca", "series": 4, "rest": "1:00"}, 
            {"name": "Elevaciones Laterales Polea", "series": 4, "rest": "1:00"},
        ],
        "Tuesday": [
            {"name": "Sentadilla", "series": 3, "rest": "2:00"},
            {"name": "Femoral Sentado", "series": 4, "rest": "1:30"},
            {"name": "Prensa", "series": 3, "rest": "2:00"},
            {"name": "Sillón Cuádriceps", "series": 3, "rest": "1:30"},
            {"name": "Gemelo", "series": 4, "rest": "1:00"},
        ],
        "Wednesday": [
            {"name": "Jalón al Pecho", "series": 4, "rest": "1:30"},
            {"name": "Remo Máquina", "series": 4, "rest": "1:30"},
            {"name": "Remo Gironda", "series": 4, "rest": "1:30"},
            {"name": "Bíceps con Barra", "series": 4, "rest": "1:00"},
            {"name": "Elevaciones Laterales Polea", "series": 4, "rest": "1:00"},
        ],
        "Thursday": [
            {"name": "Press Inclinado Barra", "series": 4, "rest": "1:30"},
            {"name": "Jalón al Pecho", "series": 4, "rest": "1:30"},
            {"name": "Posterior en Polea", "series": 4, "rest": "1:30"},
            {"name": "Triceps Tras Nuca", "series": 4, "rest": "1:00"},
            {"name": "Bíceps en Polea", "series": 4, "rest": "1:00"},
            {"name": "Elevaciones Laterales Polea", "series": 4, "rest": "1:00"},
        ],
        "Friday": [
            {"name": "Peso Muerto Rumano", "series": 3, "rest": "2:00"},
            {"name": "Prensa", "series": 3, "rest": "2:00"},
            {"name": "Camilla Femorales", "series": 4, "rest": "1:30"},
            {"name": "Sillón Cuádriceps", "series": 4, "rest": "1:30"},
        ],
        "Saturday": [{"name": "Descanso", "series": 0, "rest": "N/A"}],
        "Sunday": [{"name": "Descanso", "series": 0, "rest": "N/A"}]
    },
    "Mel": {
        "Monday": [{"name": "Descanso", "series": 0, "rest": "N/A"}],
        "Tuesday": [{"name": "Descanso", "series": 0, "rest": "N/A"}],
        "Wednesday": [{"name": "Descanso", "series": 0, "rest": "N/A"}],
        "Thursday": [{"name": "Descanso", "series": 0, "rest": "N/A"}],
        "Friday": [{"name": "Descanso", "series": 0, "rest": "N/A"}],
        "Saturday": [{"name": "Descanso", "series": 0, "rest": "N/A"}],
        "Sunday": [{"name": "Descanso", "series": 0, "rest": "N/A"}]
    }
}

# Los días de la semana en el orden correcto
DIAS_SEMANA_ORDEN = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
DIAS_SEMANA_ESPANOL = {
    "Monday": "Lunes", "Tuesday": "Martes", "Wednesday": "Miércoles", 
    "Thursday": "Jueves", "Friday": "Viernes", "Saturday": "Sábado", "Sunday": "Domingo"
}


# --- Funciones de Carga de Datos ---

def cargar_datos(reset_index=True):
    """Carga los datos de entrenamiento."""
    if os.path.exists(ARCHIVO_DATOS):
        df = pd.read_csv(ARCHIVO_DATOS)
        
        # Convertir a datetime y luego a date object
        df['Fecha'] = pd.to_datetime(df['Fecha']).apply(lambda x: x.date()) 
        
        if 'Notas' not in df.columns:
            df['Notas'] = " "
        
        df['Volumen (kg)'] = df['Peso (kg)'] * df['Reps']
        
        if 'Usuario' not in df.columns:
            df['Usuario'] = USUARIOS[0] 
        
        if reset_index:
             return df.sort_values(by='Fecha', ascending=False).reset_index()
        else:
             return df.sort_values(by='Fecha', ascending=False)
    else:
        return pd.DataFrame(columns=["index", "Usuario", "Fecha", "Ejercicio", "Peso (kg)", "Reps", "Notas", "Volumen (kg)"])

def cargar_progresos():
    """NUEVA FUNCIÓN: Carga los datos de peso y medidas."""
    columnas = ["Usuario", "Fecha", "Peso (kg)", "Cintura (cm)", "Pecho (cm)", "Brazo (cm)", "Pierna (cm)"]
    if os.path.exists(ARCHIVO_PROGRESOS):
        df = pd.read_csv(ARCHIVO_PROGRESOS)
        # Asegurar que la columna Fecha sea tipo date
        df['Fecha'] = pd.to_datetime(df['Fecha']).apply(lambda x: x.date())
        return df.sort_values(by='Fecha', ascending=False)
    else:
        return pd.DataFrame(columns=columnas)


df = cargar_datos()
df_progresos = cargar_progresos()

# --- LÓGICA DE RUTINA DEL DÍA ---
hoy = datetime.now()
dia_semana_ingles = hoy.strftime('%A')
dia_semana_espanol = hoy.strftime('%A').capitalize()
fecha_actual = hoy.strftime('%d/%m/%Y')


# --- 2. Menú lateral ---
st.sidebar.header("Menú")

usuario_activo = st.sidebar.selectbox("👤 ¿Quién registra/consulta?", USUARIOS)

menu = st.sidebar.radio("Elige una opción:", ["✍️ Registrar Rutina", "📏 Registro de Progreso", "📅 Ver Rutina Semanal", "📊 Ver Historial"])

# --- SECCIÓN: REGISTRAR RUTINA ---
if menu == "✍️ Registrar Rutina":
    
    # Obtener la rutina del día (lista de diccionarios)
    ejercicios_del_dia = DICT_RUTINAS[usuario_activo].get(dia_semana_ingles, [{"name": "Descanso", "series": 0, "rest": "N/A"}])
    
    st.subheader(f"🗓️ {dia_semana_espanol}, {fecha_actual}")
    
    # Construir la lista de ejercicios para mostrar y para el selectbox
    ejercicios_opciones = []
    
    if ejercicios_del_dia[0]["name"] == "Descanso":
         st.info(f"¡Hola {usuario_activo}! Hoy es **{dia_semana_espanol}**. Te toca: **¡Descanso!** 🧘", icon="💪")
         ejercicios_opciones = ["Descanso"]
    else:
        # Usamos "\n" y "*" para formatear como lista Markdown
        rutina_display_partes = [f"* **{e['name']}** ({e['series']} series, ⏳ {e['rest']})" for e in ejercicios_del_dia]
        rutina_display = "\n".join(rutina_display_partes)
        st.info(f"¡Hola {usuario_activo}! Hoy te toca:\n\n{rutina_display}", icon="💪")
        
        # Lista solo con los nombres para el selectbox
        ejercicios_opciones = [e["name"] for e in ejercicios_del_dia]
        

    # --- Formulario de Registro por Múltiples Series ---
    st.subheader(f"Registro de Series para {usuario_activo}")
    
    # 1. Seleccionar el Ejercicio a Registrar
    ejercicio_a_registrar = st.selectbox(
        "Selecciona el Ejercicio que acabas de terminar:", 
        ejercicios_opciones, 
        key='ej_reg'
    )

    # 2. Encontrar el número de series planificadas Y el tiempo de descanso
    series_count = 0
    rest_time = ""
    if ejercicio_a_registrar != "Descanso":
        for e in ejercicios_del_dia:
            if e["name"] == ejercicio_a_registrar:
                series_count = e["series"]
                rest_time = e["rest"]
                break
    
    # 3. Generar el formulario dinámico
    if series_count > 0:
        st.markdown("---")
        # Mostrar el tiempo de descanso planificado para el ejercicio seleccionado
        st.markdown(f"⏱️ **Descanso planificado:** **{rest_time}** entre series.")
        st.markdown(f"**Ingresa los datos de tus {series_count} series de {ejercicio_a_registrar}**")
        
        with st.form("registro_multiple_form"):
            fecha = st.date_input("Fecha de Entrenamiento", date.today(), key='date')
            
            st.markdown("---")
            
            # Encabezados de la tabla
            colA, colB, colC = st.columns([1, 2, 2])
            with colA: st.markdown("**Serie**")
            with colB: st.markdown("**Peso (kg)**")
            with colC: st.markdown("**Repeticiones**")

            # Loop para crear campos de entrada para cada serie
            for i in range(1, series_count + 1):
                colA, colB, colC = st.columns([1, 2, 2])
                
                with colA:
                    st.markdown(f"**{i}**")
                with colB:
                    # Input de Peso
                    st.number_input(
                        f"Peso (kg) - S{i}", 
                        min_value=0.0, 
                        step=0.5, 
                        value=0.0, 
                        key=f'peso_{i}', 
                        label_visibility='collapsed' 
                    )
                with colC:
                    # Input de Repeticiones
                    st.number_input(
                        f"Repeticiones - S{i}", 
                        min_value=0, 
                        step=1, 
                        value=10, 
                        key=f'reps_{i}', 
                        label_visibility='collapsed'
                    )
                
            st.markdown("---")
            guardar_button = st.form_submit_button(f"✅ Guardar {series_count} Series de {ejercicio_a_registrar}")

            if guardar_button:
                # 4. Lógica de Guardado por Lotes (Batch Save)
                nuevos_registros = []
                for i in range(1, series_count + 1):
                    # Recuperar valores del estado de la sesión
                    peso_val = st.session_state.get(f'peso_{i}', 0.0)
                    reps_val = st.session_state.get(f'reps_{i}', 0)
                    
                    # Solo guardar series con valores válidos (mayor a cero)
                    if peso_val > 0.0 and reps_val > 0:
                        nuevos_registros.append({
                            "Usuario": usuario_activo,
                            "Fecha": fecha,
                            "Ejercicio": ejercicio_a_registrar,
                            "Peso (kg)": peso_val,
                            "Reps": reps_val,
                            "Notas": " ",
                        })
                
                if nuevos_registros:
                    # Cargar los datos existentes directamente del CSV 
                    try:
                        df_existente = pd.read_csv(ARCHIVO_DATOS)
                    except FileNotFoundError:
                        df_existente = pd.DataFrame(columns=["Usuario", "Fecha", "Ejercicio", "Peso (kg)", "Reps", "Notas"])

                    nuevo_df = pd.DataFrame(nuevos_registros)
                    
                    # Concatenar y guardar el DataFrame final
                    df_final = pd.concat([df_existente, nuevo_df], ignore_index=True)
                    df_final.to_csv(ARCHIVO_DATOS, index=False)
                    
                    st.success(f"¡{len(nuevos_registros)} series de {ejercicio_a_registrar} guardadas con éxito para {usuario_activo}!")
                    st.rerun() 
                else:
                    st.warning("No se guardó ninguna serie. Asegúrate de ingresar Peso y Repeticiones mayores a cero.")
    elif ejercicio_a_registrar == "Descanso":
         st.warning("Selecciona un ejercicio válido o disfruta de tu día de descanso.")

# -----------------------------------------------------------------------------------

## --- NUEVA SECCIÓN: REGISTRO DE PROGRESO (PESO Y MEDIDAS) ---

elif menu == "📏 Registro de Progreso":
    st.header(f
