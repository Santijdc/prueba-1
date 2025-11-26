import streamlit as st
import pandas as pd
from datetime import date, datetime
import os
import locale
from streamlit_gsheets import GSheetsConnection # NUEVA LIBRERÍA

# Configuración regional para obtener el día de la semana
try:
    locale.setlocale(locale.LC_TIME, 'es_ES.UTF-8')
except locale.Error:
    pass 

# --- 1. Configuración de la página ---
st.set_page_config(page_title="Mi Diario de Gym", page_icon="🏋️‍♂️", layout="wide")
st.title("🏋️‍♂️ Registro de Entrenamientos")

# --- CONEXIÓN A GOOGLE SHEETS ---
# Utiliza el ID de las hojas definido en .streamlit/secrets.toml
# Conexión principal para Registros de Entrenamiento
conn_entrenamientos = st.connection("gsheets_entrenamientos", type=GSheetsConnection, 
                                    spreadsheet=st.secrets["ENTRENAMIENTOS_SHEET_ID"], 
                                    worksheet="Registros")

# Conexión secundaria para Progresos (Peso y Medidas)
conn_progresos = st.connection("gsheets_progresos", type=GSheetsConnection, 
                               spreadsheet=st.secrets["PROGRESOS_SHEET_ID"], 
                               worksheet="Medidas")


# Nombres de Usuarios
USUARIOS = ["Santi", "Mel"]

# Definición de las rutinas semanales
DICT_RUTINAS = {
    "Santi": [
        # (Aquí iría el contenido de tu diccionario DICT_RUTINAS, 
        # lo he omitido para no hacer el código excesivamente largo, 
        # asume que está el mismo código que tenías)
        # ... (Mantén toda la definición de DICT_RUTINAS aquí)
        # ...
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
]

# Los días de la semana en el orden correcto
DIAS_SEMANA_ORDEN = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
DIAS_SEMANA_ESPANOL = {
    "Monday": "Lunes", "Tuesday": "Martes", "Wednesday": "Miércoles", 
    "Thursday": "Jueves", "Friday": "Viernes", "Saturday": "Sábado", "Sunday": "Domingo"
}


# --- Funciones de Carga de Datos (Ahora usan Google Sheets) ---

@st.cache_data(ttl=5) # Cachea los datos por 5 segundos
def cargar_datos_entrenamiento(reset_index=True):
    """Carga los datos de entrenamiento desde Google Sheets."""
    try:
        df = conn_entrenamientos.read(ttl=5, usecols=list(range(6)))
        df = df.dropna(how="all")
        
        # Procesamiento de Datos (Igual que antes)
        df['Fecha'] = pd.to_datetime(df['Fecha']).apply(lambda x: x.date())
        df['Peso (kg)'] = pd.to_numeric(df['Peso (kg)'], errors='coerce')
        df['Reps'] = pd.to_numeric(df['Reps'], errors='coerce', downcast='integer')
        df['Volumen (kg)'] = df['Peso (kg)'] * df['Reps']
        
        # Si la columna 'Notas' es NaN (vacía en sheets), la llena con un espacio
        df['Notas'] = df['Notas'].fillna(" ")
        df['Usuario'] = df['Usuario'].fillna(USUARIOS[0])
        
        # Eliminar filas donde el peso o las reps son 0 o NaN
        df = df[(df['Peso (kg)'] > 0) & (df['Reps'] > 0)]

        if reset_index:
             # Necesario para la eliminación en el historial
             return df.sort_values(by='Fecha', ascending=False).reset_index()
        else:
             return df.sort_values(by='Fecha', ascending=False)
    except Exception as e:
        st.error(f"Error al cargar datos de entrenamiento: {e}")
        return pd.DataFrame(columns=["index", "Usuario", "Fecha", "Ejercicio", "Peso (kg)", "Reps", "Notas", "Volumen (kg)"])


@st.cache_data(ttl=5) # Cachea los datos por 5 segundos
def cargar_progresos():
    """Carga los datos de peso y medidas desde Google Sheets."""
    columnas_progreso = ["Usuario", "Fecha", "Peso (kg)", "Cintura (cm)", "Pecho (cm)", "Brazo (cm)", "Pierna (cm)"]
    try:
        df = conn_progresos.read(ttl=5, usecols=list(range(7)))
        df = df.dropna(how="all")
        
        # Procesamiento de Datos
        df['Fecha'] = pd.to_datetime(df['Fecha']).apply(lambda x: x.date())
        for col in columnas_progreso[2:]:
             df[col] = pd.to_numeric(df[col], errors='coerce')

        return df.sort_values(by='Fecha', ascending=False)
    except Exception as e:
        st.error(f"Error al cargar datos de progreso: {e}")
        return pd.DataFrame(columns=columnas_progreso)


df = cargar_datos_entrenamiento()
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
    # Importante: DICT_RUTINAS debe ser un diccionario de diccionarios
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
                # 4. Lógica de Guardado en Sheets
                nuevos_registros = []
                for i in range(1, series_count + 1):
                    # Recuperar valores del estado de la sesión
                    peso_val = st.session_state.get(f'peso_{i}', 0.0)
                    reps_val = st.session_state.get(f'reps_{i}', 0)
                    
                    # Solo guardar series con valores válidos (mayor a cero)
                    if peso_val > 0.0 and reps_val > 0:
                        nuevos_registros.append({
                            "Usuario": usuario_activo,
                            "Fecha": fecha.strftime('%Y-%m-%d'), # Formato de fecha para Sheets
                            "Ejercicio": ejercicio_a_registrar,
                            "Peso (kg)": peso_val,
                            "Reps": reps_val,
                            "Notas": " ",
                        })
                
                if nuevos_registros:
                    # Guardar en Google Sheets (API de gsheets)
                    conn_entrenamientos.append(data=nuevos_registros, worksheet="Registros")
                    
                    st.success(f"¡{len(nuevos_registros)} series de {ejercicio_a_registrar} guardadas con éxito en Google Sheets!")
                    st.rerun() 
                else:
                    st.warning("No se guardó ninguna serie. Asegúrate de ingresar Peso y Repeticiones mayores a cero.")
    elif ejercicio_a_registrar == "Descanso":
         st.warning("Selecciona un ejercicio válido o disfruta de tu día de descanso.")

# -----------------------------------------------------------------------------------

## --- SECCIÓN: REGISTRO DE PROGRESO (PESO Y MEDIDAS) ---

elif menu == "📏 Registro de Progreso":
    st.header(f"Registro de Peso y Medidas: **{usuario_activo}** 📏")
    st.info("Registra tu peso corporal y tus medidas para seguir tu evolución física.")
    
    with st.form("registro_progresos_form"):
        fecha_progreso = st.date_input("Fecha de Medición", date.today(), key='date_progreso')
        
        st.markdown("---")
        
        # Columna de Peso
        peso_corporal = st.number_input(
            "Peso Corporal (kg)", 
            min_value=0.0, 
            step=0.1, 
            value=0.0, 
            key='peso_corporal',
            help="Tu peso actual en kilogramos."
        )
        
        st.markdown("---")
        st.subheader("Medidas Corporales (cm)")
        
        # Columnas para las medidas
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            cintura = st.number_input("Cintura (cm)", min_value=0.0, step=0.5, value=0.0, key='cintura')
        with col2:
            pecho = st.number_input("Pecho (cm)", min_value=0.0, step=0.5, value=0.0, key='pecho')
        with col3:
            brazo = st.number_input("Brazo (cm)", min_value=0.0, step=0.5, value=0.0, key='brazo')
        with col4:
            pierna = st.number_input("Pierna (cm)", min_value=0.0, step=0.5, value=0.0, key='pierna')
        
        st.markdown("---")
        guardar_progreso_button = st.form_submit_button("💾 Guardar Progreso")

        if guardar_progreso_button:
            if peso_corporal > 0.0:
                nuevo_registro = {
                    "Usuario": usuario_activo,
                    "Fecha": fecha_progreso.strftime('%Y-%m-%d'), # Formato de fecha para Sheets
                    "Peso (kg)": peso_corporal,
                    "Cintura (cm)": cintura,
                    "Pecho (cm)": pecho,
                    "Brazo (cm)": brazo,
                    "Pierna (cm)": pierna,
                }
                
                # Guardar en Google Sheets (API de gsheets)
                conn_progresos.append(data=[nuevo_registro], worksheet="Medidas")
                
                st.success(f"¡Progreso de peso y medidas guardado con éxito en Google Sheets!")
                st.rerun()
            else:
                st.warning("Debes ingresar el Peso Corporal (kg) para guardar el progreso.")

    # Mostrar el historial de progresos (usa la función cargar_progresos ya actualizada)
    st.markdown("### Historial de Medidas")
    df_progreso_usuario = df_progresos[df_progresos['Usuario'] == usuario_activo].drop(columns=['Usuario']).reset_index(drop=True)

    if not df_progreso_usuario.empty:
        df_progreso_usuario_mostrar = df_progreso_usuario.sort_values(by='Fecha', ascending=False)
        st.dataframe(df_progreso_usuario_mostrar, use_container_width=True, hide_index=True)
        
        # Gráfico de Peso
        st.markdown("### Gráfico de Peso Corporal")
        df_progreso_usuario_mostrar = df_progreso_usuario_mostrar.set_index('Fecha')
        st.line_chart(df_progreso_usuario_mostrar['Peso (kg)'])
    else:
        st.info(f"Aún no hay registros de peso o medidas para {usuario_activo}.")


# -----------------------------------------------------------------------------------

## --- SECCIÓN: VER RUTINA SEMANAL ---
# ... (Esta sección no requiere cambios, mantiene la estructura que ya tenías)
# ...

elif menu == "📅 Ver Rutina Semanal":
    
    st.header(f"Plan Semanal de Entrenamiento: **{usuario_activo}** 💪")
    
    # Obtener la rutina completa del usuario activo
    rutina_semanal = DICT_RUTINAS[usuario_activo]
    
    # Iterar sobre los días en orden (Lunes a Domingo)
    for dia_ingles in DIAS_SEMANA_ORDEN:
        dia_espanol = DIAS_SEMANA_ESPANOL.get(dia_ingles, dia_ingles) # Traducir día
        ejercicios_dia = rutina_semanal.get(dia_ingles, [{"name": "Error", "series": 0, "rest": "N/A"}])
        
        # Usar la columna para la presentación del día
        with st.expander(f"**{dia_espanol}**"):
            
            if ejercicios_dia[0]["name"] == "Descanso":
                st.info("¡Descanso! 🧘")
            else:
                # Crear un DataFrame para mostrar el detalle de la rutina
                data = [
                    {
                        "Ejercicio": e['name'],
                        "Series": e['series'],
                        "Descanso ⏳": e['rest'],
                    }
                    for e in ejercicios_dia
                ]
                df_rutina = pd.DataFrame(data)
                # Ocultar el índice y usar el contenedor completo
                st.dataframe(df_rutina, use_container_width=True, hide_index=True)


# -----------------------------------------------------------------------------------

# --- SECCIÓN: VER HISTORIAL ---
elif menu == "📊 Ver Historial":
    
    # Cargar datos con reset_index=True para la visualización
    # Ya no usamos cargar_datos, sino la función de sheets
    df_actual = cargar_datos_entrenamiento(reset_index=True) 
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
                 # La fecha ahora es un objeto date de Python
                 ultima_fecha = df_actual['Fecha'].iloc[0].strftime('%d %b') 
            else:
                 ultima_fecha = "N/A"
            st.metric(label="Último Entrenamiento", value=ultima_fecha)

        with col_metrica4:
            volumen_total = df_filtrado['Volumen (kg)'].sum() if not df_filtrado.empty else 0
            st.metric(label="Volumen Total (kg)", value=f"{volumen_total:,.0f} kg")

        st.markdown("---")
        st.write(f"Historial de {ejercicio_elegido} para {usuario_activo}:")
        
        # B. TABLA CON ÍNDICES PARA ELIMINAR (NOTA: La eliminación es MUY compleja con Sheets, lo simplificamos por ahora)
        df_mostrar = df_filtrado[['index', 'Fecha', 'Ejercicio', 'Peso (kg)', 'Reps', 'Volumen (kg)']]
        df_mostrar = df_mostrar.rename(columns={'index': 'ID'})

        st.dataframe(df_mostrar, use_container_width=True, hide_index=True)
        
        # La sección de eliminación se vuelve MÁS COMPLEJA con Sheets, la dejaremos como nota por ahora:
        st.markdown("---")
        st.warning("⚠️ **Nota de Eliminación:** La eliminación de filas es compleja con Google Sheets. Para simplificar, deshabilitaremos la eliminación temporalmente. Si necesitas borrar algo, hazlo directamente en tu hoja de Google Sheets.")


        # D. Gráfico
        if ejercicio_elegido != "TODOS" and len(df_filtrado) > 1:
            st.markdown("### Gráfico de Progreso") 
            st.line_chart(df_filtrado.set_index('Fecha')['Peso (kg)'])
