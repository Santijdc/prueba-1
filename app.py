import streamlit as st
import pandas as pd
from datetime import date
import os

# 1. Configuración de la página
st.set_page_config(page_title="Mi Diario de Gym", page_icon="🏋️‍♂️")
st.title("🏋️‍♂️ Registro de Entrenamientos")

# Nombre del archivo donde guardaremos los datos (como un Excel interno)
ARCHIVO_DATOS = "entrenamientos.csv"

# 2. Función para cargar los datos existentes
def cargar_datos():
    if os.path.exists(ARCHIVO_DATOS):
        return pd.read_csv(ARCHIVO_DATOS)
    else:
        # Si no existe, creamos una tabla vacía con estas columnas
        return pd.DataFrame(columns=["Fecha", "Ejercicio", "Peso (kg)", "Reps", "Notas"])

# Cargamos los datos al iniciar
df = cargar_datos()

# 3. Menú lateral
menu = st.sidebar.radio("Menú", ["Registrar Rutina", "Ver Historial"])

# --- OPCIÓN A: REGISTRAR ---
if menu == "Registrar Rutina":
    st.subheader("Nuevo Registro")
    
    # Formulario de entrada
    col1, col2 = st.columns(2) # Dividimos en dos columnas para que se vea mejor
    
    with col1:
        fecha = st.date_input("Fecha", date.today())
        ejercicio = st.selectbox("Ejercicio", ["Sentadilla", "Press Banca", "Peso Muerto", "Dominadas", "Press Militar", "Otro"])
    
    with col2:
        peso = st.number_input("Peso (kg)", min_value=0.0, step=0.5)
        reps = st.number_input("Repeticiones", min_value=1, step=1)
    
    notas = st.text_area("Notas o sensaciones", placeholder="Ej: Me sentí con mucha energía...")

    # Botón para guardar
    if st.button("Guardar Serie"):
        # Creamos una nueva fila de datos
        nuevo_registro = pd.DataFrame({
            "Fecha": [fecha],
            "Ejercicio": [ejercicio],
            "Peso (kg)": [peso],
            "Reps": [reps],
            "Notas": [notas]
        })
        
        # Unimos la nueva fila con los datos anteriores
        df = pd.concat([df, nuevo_registro], ignore_index=True)
        
        # Guardamos en el archivo CSV
        df.to_csv(ARCHIVO_DATOS, index=False)
        
        st.success("¡Entrenamiento guardado con éxito!")

# --- OPCIÓN B: VER HISTORIAL ---
elif menu == "Ver Historial":
    st.subheader("Tu Progreso")
    
    # Mostramos la tabla
    if df.empty:
        st.info("Aún no has registrado entrenamientos. Ve a la pestaña 'Registrar Rutina'.")
    else:
        st.dataframe(df, use_container_width=True)
        
        # Un pequeño gráfico de barras si hay datos
        if not df.empty:
            st.line_chart(df.set_index("Fecha")["Peso (kg)"])
