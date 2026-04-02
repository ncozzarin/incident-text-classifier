import pandas as pd
import hashlib
import re
from datetime import timedelta
import spacy
import streamlit as st

@st.cache_resource
def cargar_modelo():
    try:
        return spacy.load("es_core_news_lg")
    except OSError:
        try:
            import es_core_news_lg
            return es_core_news_lg.load()
        except ImportError:
            st.error("El modelo 'es_core_news_lg' no está instalado. Ejecutar el instalador de nuevo.")
            return None
        
nlp = cargar_modelo()

REGLAS = {
    "hash": ["id", "caso_id", "id_investigado", "id_involucramiento", "id_persona_investigada", "sac", "numero_sumario", "dni", "cuil", "dni_involucrado"],
    "supresion": ["enlace_carpeta", "nombre_apellido", "relator", "coordinador_responsable", "detective", "asignadoA", "nombre_involucrado", "apellido_involucrado", "nombre", "apellido", "link_resolucion", "link_prorroga", "interviniente", "correo_electronico", "email"],
    "fechas": ["created_at", "updated_at", "fecha", "fecha_notificacion", "fecha_asignacion", "fechaIngresoMdt", "fechaEntrega", "fecha_remision", "fechaSalidaReqMdt", "fecha_alta_caso", "fecha_baja_caso", "fecha_incorporacion", "fecha_baja_del_caso", "fecha_hecho", "fecha_audiencia", "fecha_notificacion_decreto", "fecha_recepcion_declaracion", "fecha_privacion", "fecha_liberacion", "fecha_sanc_sob", "fecha_de_cierre_cumplimiento", "fecha_medida", "fecha_req", "fecha_prorroga", "fecha_vencimiento_prorroga"],
    "texto": ["resena", "observaciones_investigacion", "incidencias", "comentarios", "observaciones", "motivo", "fijacionHecho", "detalleProcedimiento", "observaciones_req_sanc"]
}

def anonimizar_df(df: pd.DataFrame, salt: str, dias_perturbacion: int) -> pd.DataFrame:
    df_anon = df.copy()
    columnas = df_anon.columns

    # Procesar columnas
    for col in columnas:
        if col in REGLAS["supresion"]:
            df_anon = df_anon.drop(columns=[col])
            
        elif col in REGLAS["hash"]:
            df_anon[col] = df_anon[col].apply(
                lambda x: hashlib.sha256(f"{str(x).strip()}{salt}".encode('utf-8')).hexdigest() if pd.notna(x) and str(x).strip()!="" else x
            )
            
        elif col in REGLAS["fechas"]:
            df_anon[col] = pd.to_datetime(df_anon[col], errors='coerce') + timedelta(days=dias_perturbacion)
            
        elif col in REGLAS["texto"]:
            def enmascarar(texto):
                if pd.isna(texto) or not isinstance(texto, str): return texto
                t = texto
                # Detectar Emails
                t = re.sub(r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+', '[EMAIL]', t)
                # Detectar DNI: Exactamente 7 u 8 cifras limitados por \b
                t = re.sub(r'\b\d{7,8}\b', '[DNI]', t)
                # Detectar cualquier otro número
                t = re.sub(r'\d+', '[N]', t)
                # 3. NER Spacy
                doc = nlp(t)
                tokens = ["[PERSONA]" if token.ent_type_ == "PER" else "[LUGAR]" if token.ent_type_ == "LOC" else token.text for token in doc]
                return spacy.tokens.doc.Doc(nlp.vocab, words=tokens, spaces=[tok.whitespace_ for tok in doc]).text
                
            df_anon[col] = df_anon[col].apply(enmascarar)

    return df_anon