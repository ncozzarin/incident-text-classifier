# -*- coding: utf-8 -*-
"""
Created on Sat Mar 28 19:49:33 2026

@author: Nicolas Cozzarin
"""

import streamlit as st
import pandas as pd
import io
from anonymizer import anonimizar_df

st.set_page_config(page_title="Sistema IA - Casos", layout="wide")

st.title("🛡️ Sistema de Procesamiento de Casos")

# Arquitectura de Pestañas (Tab 1 para hoy, Tab 2 para el futuro)
tab_anonimizador, tab_clasificador = st.tabs(["1. Anonimizador de Datos", "2. Clasificador IA (Próximamente)"])

with tab_anonimizador:
    st.markdown("### Configuración de Seguridad")
    col1, col2 = st.columns(2)
    with col1:
        # El usuario ingresa su clave
        salt_usuario = st.text_input("Clave secreta (Salt) para Hash:", value="ClaveDefault123", type="password")
    with col2:
        # El usuario elige cuántos días mover las fechas
        dias_usuario = st.number_input("Días de perturbación de fechas:", min_value=1, max_value=365, value=45)

    st.markdown("### Carga de Archivos")
    archivos = st.file_uploader("Sube tus archivos CSV o Excel", type=['csv', 'xlsx'], accept_multiple_files=True)

    if archivos and st.button("🚀 Iniciar Anonimización"):
        for archivo in archivos:
            with st.spinner(f'Procesando {archivo.name}...'):
                try:
                    df = pd.read_csv(archivo) if archivo.name.endswith('.csv') else pd.read_excel(archivo)
                    
                    df_listo = anonimizar_df(df, salt_usuario, dias_usuario)
                    
                    st.success(f"✅ {archivo.name} procesado.")
                    st.dataframe(df_listo.head(2))
                    
                    buffer = io.StringIO()
                    df_listo.to_csv(buffer, index=False)
                    
                    st.download_button(
                        label=f"⬇️ Descargar {archivo.name} Seguro",
                        data=buffer.getvalue(),
                        file_name=f"seguro_{archivo.name}",
                        mime="text/csv"
                    )
                except Exception as e:
                    st.error(f"Error en {archivo.name}: {e}")

with tab_clasificador:
    st.info("Aquí conectaremos el LLM en la próxima fase para clasificar los archivos seguros.")