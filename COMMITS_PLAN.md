# Public Security Classification System - Commit Plan

## Phase 1: Foundation & Database (v0.1.0)

### Commit 1.1: feat(db): initial PostgreSQL schema with pgcrypto
- Add Alembic configuration for database migrations
- Create comprehensive database models (User, Role, RawIncident, AnonymizedIncident, etc.)
- Implement encrypted vault structure for raw data storage
- Add audit logging table with hash chaining support
- Include SQL security functions in init.sql
- Bootstrap default roles and crime categories

Files: backend/alembic/*, backend/app/db/models.py, backend/alembic.ini, init.sql
Impact: Establishes core data model and security infrastructure

### Commit 1.2: chore(docker): container orchestration and environment
- Add docker-compose.yml for multi-service orchestration
- Create multi-stage Dockerfile for backend (dev/prod)
- Configure PostgreSQL with pgcrypto extension
- Set up Redis for async processing queues
- Implement healthchecks for service reliability
- Add .env.example template with security defaults

Files: docker-compose.yml, backend/Dockerfile, backend/.env.example, start.bat, init.sql
Impact: Enables local development and deployment environment

### Commit 1.3: docs: comprehensive README and project documentation
- Document setup instructions for Windows/Linux/Mac
- Detail architecture overview with service diagram
- Include development workflows and API documentation
- Add security considerations and compliance notes
- Provide contribution guidelines and branch strategy

Files: README.md
Impact: Provides clear onboarding and reference documentation

### Commit 1.4: chore(git): repository hygiene and .gitignore
- Add comprehensive .gitignore for Python, Docker, IDE
- Exclude sensitive files (credentials, passwords, env vars)
- Ignore cache files and temporary directories
- Prevent Docker volume data commits

Files: .gitignore
Impact: Maintains clean repository, prevents secret leaks

## Phase 2: Core Services (v0.2.0)

### Commit 2.1: feat(api): FastAPI foundation with async ORM
- Implement FastAPI application structure
- Add database session management with SQLAlchemy async
- Create base API router structure
- Implement health check endpoints
- Add global exception handling
- Configure CORS and middleware

Files: backend/app/main.py, backend/app/api/*, backend/app/db/core.py
Impact: Establishes API foundation for all services

### Commit 2.2: feat(auth): JWT authentication with RBAC
- Implement JWT token generation and validation
- Create role-based access control middleware
- Add password hashing with bcrypt
- Implement token refresh mechanism
- Add login/logout endpoints
- Configure token expiration and blacklisting

Files: backend/app/api/auth.py, backend/app/core/security.py
Impact: Secures API endpoints with role-based permissions

### Commit 2.3: feat(service): multi-layer anonymization pipeline
- Implement core anonymization service with regex layer
- Add dictionary-based name detection (Argentine names)
- Integrate spaCy NER for person/location detection
- Add Microsoft Presidio for advanced PII detection
- Create async processing queue with Redis
- Implement PII leakage detection with honeypots

Files: backend/app/services/anonymization.py, backend/app/utils/pii.py
Impact: Core business logic for irreversible anonymization

### Commit 2.4: feat(service): encrypted vault for raw data
- Implement vault service with AES-256-GCM encryption
- Add access control with role verification
- Implement justification logging
- Create emergency access procedures
- Add retention policy enforcement (7 years)
- Implement secure deletion

Files: backend/app/services/vault.py, backend/app/utils/encryption.py
Impact: Isolates raw data with strict access controls

### Commit 2.5: feat(logs): immutable audit logging with hash chaining
- Implement audit logger with cryptographic signing
- Add hash chaining to prevent tampering
- Log all critical actions (upload, anonymize, classify, validate)
- Store audit data in separate database schema
- Implement audit report generation
- Add log integrity verification

Files: backend/app/core/audit.py, backend/app/middleware/audit.py
Impact: Enables complete transparency and regulatory compliance

## Phase 3: AI Classification (v0.3.0)

### Commit 3.1: feat(ai): dual-head transformer model for classification
- Implement multi-task learning architecture
- Create crime type classification head
- Create urgency regression head (P1-P5)
- Add confidence scoring and calibration
- Implement model versioning system
- Add A/B testing framework

Files: backend/app/models/classifier.py, backend/app/ml/core.py
Impact: Enables AI-powered case triage

### Commit 3.2: feat(api): classification endpoints with explanations
- Add classification request/response endpoints
- Implement batch classification for efficient processing
- Add confidence breakdown and explanation data
- Create model performance monitoring
- Implement fallback strategies

Files: backend/app/api/classify.py, backend/app/services/classification.py
Impact: Exposes classification capabilities via API

### Commit 3.3: feat(validation): human-in-the-loop workflow
- Create prosecutor validation dashboard
- Implement override tracking
- Add confidence level indicators
- Store gold standard validations for training
- Implement reviewer assignments
- Track validation time metrics

Files: backend/app/api/validation.py, backend/app/services/validation.py
Impact: Ensures human oversight and accountability

## Phase 4: Frontend & UI (v0.4.0)

### Commit 4.1: feat(ui): React foundation with role-based dashboards
- Set up React 18 with TypeScript
- Implement routing with React Router
- Create role-specific dashboard layouts
- Add authentication context and guards
- Implement global state management
- Add responsive design with Tailwind

Files: frontend/src/main.tsx, frontend/src/layouts/*
Impact: Establishes frontend architecture

### Commit 4.2: feat(ui): data operator upload interface
- Implement drag-and-drop file upload
- Add progress indicators and queue status
- Create anonymization preview component
- Add download functionality
- Implement bulk operations

Files: frontend/src/pages/upload.tsx, frontend/src/components/upload/
Impact: Enables file ingestion workflow

### Commit 4.3: feat(ui): prosecutor validation interface
- Create split-screen review layout
- Display anonymized text on left panel
- Show AI predictions with confidence on right
- Implement approval/override controls
- Add reason text input for overrides
- Display alternative suggestions

Files: frontend/src/pages/review.tsx, frontend/src/components/review/
Impact: Main HITL workflow interface

### Commit 4.4: feat(ui): analytics and reporting dashboard
- Create statistics visualization components
- Add trend charts for crime types and urgency
- Implement filtered data exports
- Add correlation analysis views
- Create customizable dashboards

Files: frontend/src/pages/analytics.tsx, frontend/src/components/charts/
Impact: Enables research and pattern analysis

## Phase 5: Testing & Hardening (v0.5.0)

### Commit 5.1: test: comprehensive PII detection test suite
- Create honeypot test framework
- Add unit tests for each anonymization layer
- Implement false positive/negative rate measurement
- Add performance benchmarks
- Create regression tests
- Add test data with known PII patterns

Files: backend/tests/test_anonymization.py, backend/tests/conftest.py
Impact: Ensures anonymization quality

### Commit 5.2: test: integration tests for end-to-end workflow
- Add API integration tests
- Test complete upload → anonymize → classify → validate flow
- Add authentication integration tests
- Test error handling and edge cases
- Add load testing scripts

Files: backend/tests/test_api.py, backend/tests/test_workflow.py
Impact: Validates complete system behavior

### Commit 5.3: test: security and penetration testing
- Add authorization bypass tests
- Test vault encryption/decryption
- Verify audit log integrity
- Add secrets detection in codebase
- Test rate limiting effectiveness

Files: backend/tests/test_security.py
Impact: Ensures security controls work

## Phase 6: Production Deployment (v1.0.0)

### Commit 6.1: ci: GitHub Actions for automated testing
- Add pre-commit hooks for code quality
- Implement secret scanning in CI
- Add automated security scanning (Bandit, Safety)
- Add test coverage reporting
- Implement build caching
- Add multi-environment deployment

Files: .github/workflows/ci.yml, .pre-commit-config.yaml
Impact: Ensures code quality and security

### Commit 6.2: docs: API documentation with Swagger
- Add OpenAPI/Swagger documentation
- Document all API endpoints with examples
- Include authentication flows
- Add response schemas and error codes
- Generate client SDKs

Files: backend/app/main.py (OpenAPI tags), docs/api.md
Impact: Enables API consumers and testing

### Commit 6.3: chore: production configuration and monitoring
- Add production docker-compose configuration
- Implement Prometheus metrics
- Add Grafana dashboards
- Configure log aggregation
- Add backup and recovery procedures
- Document DR procedures

Files: docker-compose.prod.yml, monitoring/
Impact: Production-ready deployment

### Commit 6.4: chore: version 1.0.0 release
- Tag v1.0.0 release
- Update CHANGELOG.md
- Create deployment checklist
- Generate final security audit report
- Add production configuration templates
- Document known limitations

Files: CHANGELOG.md, VERSION, deployment/
Impact: Official production release