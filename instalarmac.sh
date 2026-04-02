#!/bin/bash
echo "=================================================="
echo "Instalando dependencias "
echo "=================================================="

# Crear entorno virtual usando python3 

python3 -m venv entorno_seguro

# Activar entorno
source entorno_seguro/bin/activate

# Actualizar pip
python3 -m pip install --upgrade pip

# Instalar librerías
pip install pandas streamlit openpyxl spacy==3.7.5

# Instalar el modelo de SpaCy
pip install https://github.com/explosion/spacy-models/releases/download/es_core_news_lg-3.7.0/es_core_news_lg-3.7.0-py3-none-any.whl

echo "=================================================="
echo "INSTALACIÓN FINALIZADA."
echo "=================================================="