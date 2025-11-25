import streamlit as st
import pandas as pd
from datetime import date
import os
import numpy as np # Necesario para algunas operaciones de DataFrame

# --- 1. Configuración de la página ---
st.set_page_config(page_title="Mi Diario de Gym", page_icon="🏋️‍♂️", layout="wide")
st.title("🏋️‍♂️ Registro de Entrenamientos")

ARCHIVO_DATOS = "entrenamientos.csv"

def cargar_datos():
    if os.path.exists(ARCHIVO_DATOS):
        df = pd.read_csv(ARCHIVO_DATOS)
        df['Fecha'] = pd.to_datetime(df['Fecha']).dt.date # Convertir a solo fecha
        return df.sort_values(by='Fecha', ascending=False).reset_index(drop=True)
    else:
        return pd.DataFrame(columns=["Fecha", "Ejercicio", "Peso (kg)", "Reps", "Notas"])

df = cargar_datos()

# --- 2. Menú lateral (Registro) ---
st.sidebar.header("Menú")
menu = st.sidebar.radio("Elige una opción:", ["✍️ Registrar Rutina", "📊 Ver Historial"])

if menu == "✍️ Registrar Rutina":
    st.subheader("Nuevo Registro")
    
    with st.form("registro_form"):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            fecha = st.date_input("Fecha", date.today(), key='date')
            ejercicio = st.selectbox("Ejercicio", ["Sentadilla", "Press Banca", "Peso Muerto", "Dominadas", "Press Militar", "Otro"], key='ej')
        
        with col2:
            peso = st.number_input("Peso (kg)", min_value=0.0, step=0.5, key='peso')
            reps = st.number_input("Repeticiones", min_value=1, step=1, key='reps')

        with col3:
            st.markdown(" ")
            notas = st.text_area("Notas o sensaciones", height=100, placeholder="Ej: Récord personal, me sentí cansado...", key='notas')

        st.markdown("---")
        guardar_button = st.form_submit_button("✅ Guardar Serie")

        if guardar_button:
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


# --- 3. OPCIÓN B: VER HISTORIAL (Con función de ELIMINAR) ---
elif menu == "📊 Ver Historial":
    st.subheader("Tu Progreso Detallado")
    
    if df.empty:
        st.info("Aún no has registrado entrenamientos.")
    else:
        # A. FILTRADO Y MÉTRICAS
        ejercicios_unicos = df['Ejercicio'].unique().tolist()
        ejercicio_elegido = st.selectbox("Filtrar por Ejercicio:", ["TODOS"] + ejercicios_unicos)
        
        df_filtrado = df
        if ejercicio_elegido != "TODOS":
            df_filtrado = df[df['Ejercicio'] == ejercicio_elegido].reset_index(drop=True)

        col_metrica1, col_metrica2, col_metrica3 = st.columns(3)
        
        with col_metrica1:
            st.metric(label="Total de Series", value=f"{len(df_filtrado)} Series")
        with col_metrica2:
            max_peso = df_filtrado['Peso (kg)'].max() if not df_filtrado.empty else 0
            st.metric(label="Peso Máximo (kg)", value=f"{max_peso} kg")
        with col_metrica3:
            ultima_fecha = df['Fecha'].dt.strftime('%d %b').iloc[0] if not df.empty else "N/A"
            st.metric(label="Último Entrenamiento", value=ultima_fecha)

        st.markdown("---")
        st.write(f"Historial de {ejercicio_elegido}:")
        
        # B. TABLA CON ÍNDICES PARA ELIMINAR
        # Añadimos una columna 'ID' temporal para que el usuario pueda referenciar la fila
        df_mostrar = df_filtrado.copy()
        df_mostrar.insert(0, 'ID', df_mostrar.index)
        st.dataframe(df_mostrar, use_container_width=True, hide_index=True)
        
        # C. SECCIÓN DE ELIMINACIÓN
        st.markdown("---")
        st.error("🚨 ¿Quieres eliminar un registro?")
        
        # Obtenemos los IDs disponibles en la tabla filtrada
        opciones_id = df_mostrar['ID'].tolist()
        
        # Si hay datos
        if opciones_id:
            col_del1, col_del2 = st.columns([1, 4])
            
            with col_del1:
                # El usuario elige el ID (número) que quiere eliminar
                id_a_eliminar = st.selectbox("Selecciona el ID a eliminar:", opciones_id)
            
            with col_del2:
                # Botón de eliminación
                st.markdown('<br>', unsafe_allow_html=True) # Espacio para alinear el botón
                if st.button("🔴 CONFIRMAR ELIMINACIÓN"):
                    # Obtenemos el índice real del DataFrame original que corresponde al ID
                    indice_real = df_filtrado.index[df_filtrado['ID'] == id_a_eliminar].tolist()[0]
                    
                    # Eliminar la fila del DataFrame original
                    df = df.drop(index=indice_real).reset_index(drop=True)
                    
                    # Guardamos el nuevo DataFrame sin la fila eliminada
                    df.to_csv(ARCHIVO_DATOS, index=False)
                    st.warning(f"✅ ¡Registro ID {id_a_eliminar} eliminado! Presiona F5 para actualizar.")
        else:
            st.info("No hay registros para eliminar en este filtro.")

        # D. Gráfico
        if ejercicio_elegido != "TODOS" and len(df_filtrado) > 1:
            st.markdown("### Gráfico de Progreso")
            st.line_chart(df_filtrado.set_index('Fecha')['Peso (kg)'])
