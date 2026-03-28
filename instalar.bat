@echo off
echo ===============================================
echo Instalando Motor de Anonimizacion IA
echo Por favor, no cierre esta ventana...
echo ===============================================

echo 1. Creando entorno aislado...
python -m venv entorno_seguro

echo 2. Activando entorno...
call entorno_seguro\Scripts\activate

echo 3. Instalando dependencias base (Streamlit, Pandas)...
python -m pip install --upgrade pip
pip install streamlit pandas openpyxl spacy==3.7.4

echo 4. Descargando modelo de Inteligencia Artificial (Esto puede demorar unos minutos)...
pip install https://github.com/explosion/spacy-models/releases/download/es_core_news_lg-3.7.0/es_core_news_lg-3.7.0-py3-none-any.whl

echo ===============================================
echo INSTALACION COMPLETADA CON EXITO.
echo Ya puede hacer doble clic en "iniciar.bat"
echo ===============================================
pause