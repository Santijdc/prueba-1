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


# --- 2.
