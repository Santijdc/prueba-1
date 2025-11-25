import streamlit as st
import pandas as pd
from datetime import date
import os

# --- 1. Configuración de la página ---
# Usamos un tema 'wide' para que ocupe más espacio en la pantalla
st.set_page_config(page_title="Mi Diario de Gym", page_icon="🏋️‍♂️", layout="wide")
st.title("🏋️‍♂️ Registro de Entrenamientos")

ARCHIVO_DATOS = "entrenamientos.csv"

def cargar_datos():
    if os.path.exists(ARCHIVO_DATOS):
        # Aseguramos que la columna 'Fecha' sea de tipo fecha
        df = pd.read_csv(ARCHIVO_DATOS)
        df['Fecha'] = pd.to_datetime(df['Fecha'])
        return df.sort_values(by='Fecha', ascending=False)
    else:
        return pd.DataFrame(columns=["Fecha", "Ejercicio", "Peso (kg)", "Reps", "Notas"])

df = cargar_datos()

# --- 2. Menú lateral (Registro) ---
st.sidebar.header("Menú")
menu = st.sidebar.radio("Elige una opción:", ["✍️ Registrar Rutina", "📊 Ver Historial"])

if menu == "✍️ Registrar Rutina":
    st.subheader("Nuevo Registro")
    
    # Formulario más compacto y limpio
    with st.form("registro_form"):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            fecha = st.date_input("Fecha", date.today(), key='date')
            ejercicio = st.selectbox("Ejercicio", ["Sentadilla", "Press Banca", "Peso Muerto", "Dominadas", "Press Militar", "Otro"], key='ej')
        
        with col2:
            peso = st.number_input("Peso (kg)", min_value=0.0, step=0.5, key='peso')
            reps = st.number_input("Repeticiones", min_value=1, step=1, key='reps')

        with col3:
             # Columna vacía o para notas rápidas
            st.markdown(" ") # Espacio para alinear
            notas = st.text_area("Notas o sensaciones", height=100, placeholder="Ej: Récord personal, me sentí cansado...", key='notas')

        # Botón para guardar, centrado
        st.markdown("---")
        guardar_button = st.form_submit_button("✅ Guardar Serie")

        if guardar_button:
            # Lógica para guardar (igual que antes)
            nuevo_registro = pd.DataFrame({
                "Fecha": [fecha],
                "Ejercicio": [ejercicio],
                "Peso (kg)": [peso],
                "Reps": [reps],
                "Notas": [notas]
            })
            
            df = pd.concat([df, nuevo_registro], ignore_index=True)
            df.to_csv(ARCHIVO_DATOS, index=False)
            
            st.success("¡Entrenamiento guardado con éxito!")


# --- 3. OPCIÓN B: VER HISTORIAL (Diseño mejorado) ---
elif menu == "📊 Ver Historial":
    st.subheader("Tu Progreso Detallado")
    
    if df.empty:
        st.info("Aún no has registrado entrenamientos.")
    else:
        # A. Filtro para la tabla
        ejercicios_unicos = df['Ejercicio'].unique().tolist()
        ejercicio_elegido = st.selectbox("Filtrar por Ejercicio:", ["TODOS"] + ejercicios_unicos)
        
        df_filtrado = df
        if ejercicio_elegido != "TODOS":
            df_filtrado = df[df['Ejercicio'] == ejercicio_elegido]

        # B. Métricas clave (st.metric)
        col_metrica1, col_metrica2, col_metrica3 = st.columns(3)
        
        with col_metrica1:
            total_registros = len(df_filtrado)
            st.metric(label="Total de Series Registradas", value=f"{total_registros} Series")
        
        with col_metrica2:
            max_peso = df_filtrado['Peso (kg)'].max() if not df_filtrado.empty else 0
            st.metric(label="Peso Máximo Levantado", value=f"{max_peso} kg")
            
        with col_metrica3:
            # Calculamos la fecha del último entrenamiento (solo si el DF no está vacío)
            if not df.empty:
                 ultima_fecha = df['Fecha'].dt.strftime('%d %b').iloc[0]
            else:
                 ultima_fecha = "N/A"
            st.metric(label="Último Entrenamiento", value=ultima_fecha)

        # 
        
        st.markdown("---")
        st.write(f"Historial de {ejercicio_elegido}:")
        st.dataframe(df_filtrado, use_container_width=True, hide_index=True)
        
        # C. Gráfico (solo para el ejercicio filtrado si es numérico)
        if ejercicio_elegido != "TODOS" and len(df_filtrado) > 1:
            st.line_chart(df_filtrado.set_index('Fecha')['Peso (kg)'])
