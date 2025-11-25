# ...
# -----------------------------------------------------------------------------------

## --- SECCIÓN: VER RUTINA SEMANAL ---

elif menu == "📅 Ver Rutina Semanal":
    
    st.header(f"Plan Semanal de Entrenamiento: **{usuario_activo}** 💪")
    
    # Obtener la rutina completa del usuario activo
    rutina_semanal = DICT_RUTINAS[usuario_activo]
    
    # -----------------------------------------------------
    # LÓGICA DE CÁLCULO DE VOLUMEN SEMANAL POR GRUPO MUSCULAR
    # -----------------------------------------------------
    
    volumen_semanal = {}
    
    # 1. Iterar sobre todos los días y ejercicios
    for dia_ingles in DIAS_SEMANA_ORDEN:
        ejercicios_dia = rutina_semanal.get(dia_ingles, [])
        for ejercicio in ejercicios_dia:
            group = ejercicio.get("group")
            series = ejercicio.get("series", 0)
            
            # 2. Sumar las series al grupo muscular correspondiente
            if group and group != "Descanso":
                if group in volumen_semanal:
                    volumen_semanal[group] += series
                else:
                    volumen_semanal[group] = series

    # 3. Crear el DataFrame para visualización
    df_volumen = pd.DataFrame(
        volumen_semanal.items(), 
        columns=["Grupo Muscular", "Total Series Semanales"]
    ).sort_values(by="Total Series Semanales", ascending=False).reset_index(drop=True)
    
    # 4. Mostrar el resumen en una tabla
    st.subheader("Total de Series (Volumen) Semanal por Grupo Muscular")
    
    # Aplicar formato condicional al DataFrame para resaltado visual
    def highlight_series(s):
        is_high = s > 12  # Define un umbral arbitrario de volumen alto
        return ['background-color: #034f84; color: white' if v else '' for v in is_high]
        
    st.dataframe(
        df_volumen.style.apply(highlight_series, subset=['Total Series Semanales']),
        use_container_width=True, 
        hide_index=True
    )
    
    st.markdown("---")
    st.subheader("Detalle Diario")
    
    # -----------------------------------------------------
    # DETALLE DE LA RUTINA DIARIA (Igual que antes)
    # -----------------------------------------------------
    
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
                        "Grupo": e['group'] # Incluimos el grupo en el detalle
                    }
                    for e in ejercicios_dia if e.get('group') != "Descanso"
                ]
                df_rutina = pd.DataFrame(data)
                # Ocultar el índice y usar el contenedor completo
                st.dataframe(df_rutina, use_container_width=True, hide_index=True)

# ... (El resto del código de la app)
