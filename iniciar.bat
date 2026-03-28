@echo off
echo Iniciando Sistema de Anonimizacion...
call entorno_seguro\Scripts\activate
streamlit run app.py
pause