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
    ejercicios_del_dia = DICT_RUTINAS[usuario_activo].get(dia_semana_ingles, [{"name": "Descanso", "series": 0, "rest": "N/A"}])
    
    st.subheader(f"🗓️ {dia_semana_espanol}, {fecha_actual}")
    
    # Construir la lista de ejercicios para mostrar y para el selectbox
    ejercicios_opciones = []
    
    if ejercicios_del_dia[0]["name"] == "Descanso":
         st.info(f"¡Hola {usuario_activo}! Hoy es **{dia_semana_espanol}**. Te toca: **¡Descanso!** 🧘", icon="💪")
         ejercicios_opciones = ["Descanso"]
    else:
        # NUEVA LÓGICA: Usamos "\n" y "*" para formatear como lista Markdown
        rutina_display_partes = [f"* **{e['name']}** ({e['series']} series, ⏳ {e['rest']})" for e in ejercicios_del_dia]
        rutina_display = "\n".join(rutina_display_partes)
        st.info(f"¡Hola {usuario_activo}! Hoy te toca:\n\n{rutina_display}", icon="💪") # CORRECCIÓN: Eliminado <br> extra aquí
        
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
                    # Cargar los datos existentes directamente del CSV (sin las columnas temporales 'index' y 'Volumen')
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

        col_metrica1, col_metrica2, col_metrica3, col_metrica4 = st.columns(4)
        
        with col_metrica1:
            st.metric(label="Total de Series", value=f"{len(df_filtrado)} Series")
        
        with col_metrica2:
            max_peso = df_filtrado['Peso (kg)'].max() if not df_filtrado.empty else 0
            st.metric(label="Peso Máximo (kg)", value=f"{max_peso} kg")
            
        with col_metrica3:
            if not df_usuario.empty: 
                 ultima_fecha = df_actual['Fecha'].iloc[0].strftime('%d %b') 
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
                    # Cargar los datos sin el index temporal para poder borrar por el índice real
                    df_base = cargar_datos(reset_index=False)
                    # Asegurarse de que el índice a borrar exista
                    if id_a_eliminar in df_base.index:
                        df_base = df_base.drop(index=id_a_eliminar)
                        df_base.to_csv(ARCHIVO_DATOS, index=False)
                        st.warning(f"✅ ¡Registro ID {id_a_eliminar} de {usuario_activo} eliminado! Presiona F5 para actualizar.")
                        st.rerun()
                    else:
                        st.error("Error: El ID seleccionado no existe.")
        else:
            st.info(f"No hay registros para eliminar en este filtro para {usuario_activo}.")

        # D. Gráfico
        if ejercicio_elegido != "TODOS" and len(df_filtrado) > 1:
            st.markdown("### Gráfico de Progreso") 
            st.line_chart(df_filtrado.set_index('Fecha')['Peso (kg)'])
