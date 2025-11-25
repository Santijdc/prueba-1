import streamlit as st
import pandas as pd
from datetime import date
import os
import numpy as np

# --- 1. Configuración de la página ---
st.set_page_config(page_title="Mi Diario de Gym", page_icon="🏋️‍♂️", layout="wide")
st.title("🏋️‍♂️ Registro de Entrenamientos")

ARCHIVO_DATOS = "entrenamientos.csv"

# Opciones de Usuarios
USUARIOS = ["Mi Usuario", "Mi Novia"]

def cargar_datos():
    if os.path.exists(ARCHIVO_DATOS):
        df = pd.read_csv(ARCHIVO_DATOS)
        df['Fecha'] = pd.to_datetime(df['Fecha']).dt.date
        
        # Cálculo de Volumen Total por registro
        df['Volumen (kg)'] = df['Peso (kg)'] * df['Reps']
        
        # Nos aseguramos de que todos los registros tengan una columna 'Usuario'
        if 'Usuario' not in df.columns:
            # Asignamos el primer usuario por defecto a los registros viejos
            df['Usuario'] = USUARIOS[0] 
        
        return df.sort_values(by='Fecha', ascending=False).reset_index()
    else:
        # Creamos una tabla inicial con la columna 'Usuario'
        return pd.DataFrame(columns=["index", "Usuario", "Fecha", "Ejercicio", "Peso (kg)", "Reps", "Notas", "Volumen (kg)"])

df = cargar_datos()

# --- 2. Menú lateral (Registro) ---
st.sidebar.header("Menú")

# AÑADIR CAMPO DE SELECCIÓN DE USUARIO EN EL MENÚ LATERAL
usuario_activo = st.sidebar.selectbox("👤 ¿Quién registra/consulta?", USUARIOS)

menu = st.sidebar.radio("Elige una opción:", ["✍️ Registrar Rutina", "📊 Ver Historial"])

if menu == "✍️ Registrar Rutina":
    st.subheader(f"Nuevo Registro para {usuario_activo}")
    
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
                "Usuario": [usuario_activo], # AÑADIR EL USUARIO
                "Fecha": [fecha],
                "Ejercicio": [ejercicio],
                "Peso (kg)": [peso],
                "Reps": [reps],
                "Notas": [notas]
            })
            
            df = pd.concat([df, nuevo_registro], ignore_index=True)
            df.to_csv(ARCHIVO_DATOS, index=False)
            
            st.success(f"¡Entrenamiento de {usuario_activo} guardado con éxito!")


# --- 3. OPCIÓN B: VER HISTORIAL (Filtrado por usuario) ---
elif menu == "📊 Ver Historial":
    
    # 1. FILTRADO PRINCIPAL POR USUARIO
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

        # Reiniciar índice para que los IDs sean 0, 1, 2... en la vista
        df_filtrado = df_filtrado.reset_index()

        col_metrica1, col_metrica2, col_metrica3, col_metrica4 = st.columns(4)
        
        with col_metrica1:
            st.metric(label="Total de Series", value=f"{len(df_filtrado)} Series")
        
        with col_metrica2:
            max_peso = df_filtrado['Peso (kg)'].max() if not df_filtrado.empty else 0
            st.metric(label="Peso Máximo (kg)", value=f"{max_peso} kg")
            
        with col_metrica3:
            if not df_usuario.empty: # Usamos df_usuario para la fecha, no el filtrado
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
        # Mostrar la columna 'index' (que es el ID real en la tabla principal) como 'ID'
        df_mostrar = df_filtrado[['index', 'Fecha', 'Ejercicio', 'Peso (kg)', 'Reps', 'Notas', 'Volumen (kg)']]
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
                    # El ID seleccionado corresponde al índice real
                    df = df.drop(index=id_a_eliminar).reset_index(drop=True)
                    
                    df.to_csv(ARCHIVO_DATOS, index=False)
                    st.warning(f"✅ ¡Registro ID {id_a_eliminar} de {usuario_activo} eliminado! Presiona F5 para actualizar.")
        else:
            st.info(f"No hay registros para eliminar en este filtro para {usuario_activo}.")

        # D. Gráfico
        if ejercicio_elegido != "TODOS" and len(df_filtrado) > 1:
            st.markdown("### Gráfico de Progreso")
            st.line_chart(df_filtrado.set_index('Fecha')['Peso (kg)'])
