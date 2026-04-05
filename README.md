# Sistema de Clasificación de Incidentes de Seguridad

Sistema de anonimización y clasificación de IA para reportes disciplinarios de las fuerzas de seguridad de Córdoba.

## Descripción del Proyecto

Este sistema procesa reportes disciplinarios de manera segura y anónima, permitiendo a fiscales y investigadores analizar patrones de violencia institucional o corrupción sin exponer datos personales sensibles.

### Características Clave

- ✓ **Anonimización irreversible** multi-capa (regex → diccionario → spaCy → Presidio)
- ✓ **Clasificación dual con IA** (tipo de delito + urgencia P1-P5)
- ✓ **Human-in-the-loop** - todos los casos requieren validación de fiscal
- ✓ **Vault encriptado** para datos crudos con controles de acceso estrictos
- ✓ **Auditoría inmutable** con hash chaining para cadena de custodia
- ✓ **Infraestructura en contenedores** para fácil despliegue

## Requisitos

- Docker y Docker Compose
- Python 3.12 (para desarrollo local)
- Node.js 18+ (para frontend)
- PostgreSQL 15+ con extensión pgcrypto
- Redis

## Configuración Rápida

1. **Copiar archivo de entorno:**
```bash
cp .env.example .env
```

2. **Editar .env con tus claves:**
```bash
# Requerido: Estas claves DEBEN cambiarse en producción
POSTGRES_PASSWORD=tu_contraseña_segura_aqui
VAULT_MASTER_KEY=$(openssl rand -hex 32)
AUDIT_LOG_SIGNING_KEY=$(openssl rand -hex 32)
JWT_SECRET_KEY=$(openssl rand -hex 32)

# Opcional: OpenAI para mejoras futuras
OPENAI_API_KEY=tu_clave_aqui
```

3. **Iniciar el sistema:**

### Windows
```bash
start.bat
```

### Linux/Mac
```bash
./start.sh
```

Esto iniciará:
- PostgreSQL en puerto 5432
- Redis en puerto 6379
- FastAPI backend en http://localhost:8000
- React frontend en http://localhost:3000
- Documentación API en http://localhost:8000/docs

## Desarrollo

### Backend (FastAPI)
```bash
cd backend
source entorno_api/bin/activate  # Linux/Mac
# o\entorno_api\Scripts\activate  # Windows

# Instalar dependencias
pip install -r requirements.txt

# Descargar modelo spaCy
python -c "import spacy; spacy.load('es_core_news_lg')"

# Instalar Presidio
pip install presidio-analyzer presidio-anonymizer

# Descargar modelo spaCy para Presidio
python -m spacy download es_core_news_lg

# Ejecutar migraciones
alembic upgrade head

# Iniciar servidor
uvicorn app.main:app --reload
```

### Frontend (React)
```bash
cd frontend
npm install
npm run dev
```

## Arquitectura

```
┌─────────────┐    ┌───────────────┐    ┌─────────────┐
│   Frontend  │───▶│  API Gateway  │───▶| Anonymization├──▶ PostgreSQL
│   (React)   │    │  (FastAPI)    │    │   Service   │
└─────────────┘    └───────┬───────┘    └──────┬──────┘
                           │                   │
                           │              ┌────▼──────┐
                           │              │  Redis    │
                           │              └───────────┘
                           │
                           │         ┌──────────────┐
                           └────────▶│ AI Service   ├──▶ Model
                                     └───────┬──────┘           Inference
                                             │
                                     ┌───────▼────────┐
                                     │ Vault Service  │
                                     └───────────────┘
```

## Pipeline de Anonimización

1. **Extracción determinista**: Emails, teléfonos, DNI (regex)
2. **Filtro basado en diccionario**: Nombres argentinos comunes
3. **NER estadístico**: spaCy para personas y lugares
4. **Presidio**: Detección avanzada de PII
5. **Validación de integridad**: Honeytokens para detectar fugas

## Pipeline de Clasificación con IA

- **Modelo**: BERT multilingüe fine-tuneado para español
- **Salidas duales**:
  - Tipo de delito: Robo, Violencia de Género, Abuso de Autoridad, Lesiones, Amenazas, Otros
  - Urgencia: P1 (crítico) a P5 (bajo programa)
- **Explicabilidad**: Pesos de atención y valores SHAP
- **Aprendizaje continuo**: Retroalimentación de validaciones humanas

## Seguridad

### Gestión de Datos
- **Vault encriptado**: Datos crudos con AES-256-GCM
- **Anonimización irreversible**: PII reemplazado, no enmascarado
- **Retención**: 7 años automático para requisitos legales
- **Borrado seguro**: Datos expirados eliminados físicamente

### Acceso
- **RBAC**: 4 roles con permisos granulares
- **Autenticación JWT**: Tokens con rotación
- **MFA opcional**: Para roles privilegiados
- **Principio de mínimo privilegio**

### Auditoría
- **Registros inmutables**: Hash chaining para prevenir manipulación
- **Acceso al vault**: Justificación requerida y loggeada
- **Alertas automáticas**: Patrones de acceso inusuales
- **Integridad**: Verificación de hashes de auditoría

## Desarrollo

### Estructura del Backend
```
backend/
├── app/
│   ├── api/              # Endpoints FastAPI
│   ├── core/             # Configuración
│   ├── db/               # SQLAlchemy models
│   ├── services/         # Lógica de negocio
│   └── utils/            # Funciones de ayuda
├── alembic/              # Migraciones
└── tests/                # Tests unitarios/in
```

## Testing

### Calidad de Anonimización
```bash
cd backend
pytest tests/test_anonymization.py -v
```

**Métricas de calidad:**
- < 0.5% falsos negativos (PII no detectada)
- < 2% falsos positivos (sobre-anonimización)
- Tiempo de procesamiento: < 5 segundos por incidente

### Performance de Clasificación
```bash
pytest tests/test_classification.py -v
```

**Métricas de modelo:**
- Precisión tipo delito: 85%+
- Precisión urgencia: 80%+
- Tiempo inferencia: < 1 segundo

## Licencia

Este proyecto está licenciado bajo los términos de la licencia AGPL-3.0.

## Soporte

Para soporte técnico o cuestiones de seguridad:
- Email: soporte-tecnico@seguridad.cba.gov.ar
- Línea directa (24/7): +54 351 999-9999

## Despliegue a Producción

Para despliegue a producción:

1. **Generar claves de producción** (32 bytes hex):
```bash
openssl rand -hex 32 > .vault-key
openssl rand -hex 32 > .audit-key
```

2. **Configurar reverse proxy** (Nginx):
```nginx
server {
    listen 443 ssl;
    ssl_certificate /etc/ssl/certs/your-cert.pem;
    ssl_certificate_key /etc/ssl/private/your-key.pem;

    location /api {
        proxy_pass http://api:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location / {
        proxy_pass http://frontend:3000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

3. **Despliegue con Docker Compose**:
```bash
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

## Agradecimientos

- Equipo de Fiscales de Córdoba por su retroalimentación
- Ministerio de Seguridad por el acceso a datos históricos
- Fundación Security Research por el asesoramiento técnico

## Aviso Legal

Este sistema maneja datos sensibles bajo regulación PDPL (Ley 25.326). Toda acción queda registrada en logs de auditoría inmutables.