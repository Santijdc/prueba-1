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

# Definición de las rutinas semanales (CON SERIES)
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

# La función cargar_datos ya no es global para evitar problemas de re-ejecución
def cargar_datos(reset_index=True):
    if os.path.exists(ARCHIVO_DATOS):
        df = pd.read_csv(ARCHIVO_DATOS)
        
        # Convertir a datetime y luego a date object
        df['Fecha'] = pd.to_datetime(df['Fecha']).apply(lambda x: x.date()) 
        
        # Asegurar columna Notas para registros antiguos que no la tienen
        if 'Notas' not in df.columns:
            df['Notas'] = " "
        
        # Cálculo de Volumen Total por registro
        df['Volumen (kg)'] = df['Peso (kg)'] * df['Reps']
        
        if 'Usuario' not in df.columns:
            df['Usuario'] = USUARIOS[0] 
        
        if reset_index:
             # Retornamos el index para usarlo como ID de eliminación
             return df.sort_values(by='Fecha', ascending=False).reset_index()
        else:
             # Para guardar, retornamos el DataFrame sin el índice extra
             return df.sort_values(by='Fecha', ascending=False)
    else:
        # Quitamos "Notas" de las columnas de inicialización
        return pd.DataFrame(columns=["index", "Usuario", "Fecha", "Ejercicio", "Peso (kg)", "Reps", "Notas", "Volumen (kg)"])

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
    
    # Construir la lista de ejercicios para mostrar y para el selectbox
    ejercicios_opciones = []
    
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
        

    # --- Formulario de Registro por Múltiples Series ---
    st.subheader(f"Registro de Series para {usuario_activo}")
    
    # 1. Seleccionar el Ejercicio a Registrar
    ejercicio_a_registrar = st.selectbox(
        "Selecciona el Ejercicio que acabas de terminar:", 
        ejercicios_opciones, 
        key='ej_reg'
    )

    # 2. Encontrar el número de series planificadas
    series_count = 0
    if ejercicio_a_registrar != "Descanso":
        for e in ejercicios_del_dia:
            if e["name"] == ejercicio_a_registrar:
                series_count = e["series"]
                break
    
    # 3. Generar el formulario dinámico
    if series_count > 0:
        st.markdown("---")
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
                        label_visibility='collapsed' # Ocultar la etiqueta del número
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
                    # Cargar los datos existentes directamente del CSV (sin las columnas temporales 'index' y 'Volumen')
                    df_existente = pd.read_csv(ARCHIVO_DATOS)
                    nuevo_df = pd.DataFrame(nuevos_registros)
                    
                    # Concatenar y guardar el DataFrame final
                    df_final = pd.concat([df_existente, nuevo_df], ignore_index=True)
                    df_final.to_csv(ARCHIVO_DATOS, index=False)
                    
                    st.success(f"¡{len(nuevos_registros)} series de {ejercicio_a_registrar} guardadas con éxito para {usuario_activo}!")
                    # Recargar la app para limpiar el formulario
                    st.rerun() 
                else:
                    st.warning("No se guardó ninguna serie. Asegúrate de ingresar Peso y Repeticiones mayores a cero.")
    elif ejercicio_a_registrar == "Descanso":
         st.warning("Selecciona un ejercicio válido o disfruta de tu día de descanso.")


# --- 3. OPCIÓN B: VER HISTORIAL ---
elif menu == "📊 Ver Historial":
    
    # Cargar datos con reset_index=True para la visualización
    df_actual = cargar_datos(reset_index=True) 
    df_usuario = df_actual[df_actual['Usuario'] == usuario_activo]
    
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

        col_metrica1, col_met
