"""Initial schema: security incident anonymization system

Revision ID: 001
Revises:
Create Date: 2024-01-01 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Enable pgcrypto extension for encryption functions
    op.execute("CREATE EXTENSION IF NOT EXISTS pgcrypto")

    # Create roles table
    op.create_table(
        'roles',
        sa.Column('id', postgresql.UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), primary_key=True),
        sa.Column('name', sa.String(50), nullable=False, unique=True),
        sa.Column('description', sa.Text, nullable=True),
        sa.Column('permissions', postgresql.JSONB, nullable=False),
        sa.Column('is_active', sa.Boolean, server_default='true', nullable=False),
        sa.Column('created_at', sa.DateTime, server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('updated_at', sa.DateTime, server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Index('idx_roles_name_active', 'name', 'is_active'),
    )

    # Create users table
    op.create_table(
        'users',
        sa.Column('id', postgresql.UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), primary_key=True),
        sa.Column('email', sa.String(255), nullable=False, unique=True),
        sa.Column('full_name', sa.String(255), nullable=True),
        sa.Column('hashed_password', sa.String(255), nullable=False),
        sa.Column('role', sa.String(50), nullable=False, index=True),
        sa.Column('is_active', sa.Boolean, server_default='true', nullable=False),
        sa.Column('created_at', sa.DateTime, server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('updated_at', sa.DateTime, server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('last_login', sa.DateTime, nullable=True),
        sa.Index('idx_users_email_active', 'email', 'is_active'),
        sa.Index('idx_users_role_active', 'role', 'is_active'),
    )

    # Create raw_incidents table - encrypted vault
    op.create_table(
        'raw_incidents',
        sa.Column('id', postgresql.UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), primary_key=True),
        sa.Column('encrypted_payload', sa.Text, nullable=False),  # AES-256-GCM encrypted
        sa.Column('file_name', sa.String(500), nullable=False),
        sa.Column('file_size', sa.Integer, nullable=False),
        sa.Column('mime_type', sa.String(100), nullable=False),
        sa.Column('upload_metadata', postgresql.JSONB, nullable=False),
        sa.Column('uploaded_by', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('uploaded_at', sa.DateTime, server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('retention_until', sa.DateTime, nullable=False),
        sa.Column('retention_reason', sa.String(200), nullable=False),
        sa.Column('access_count', sa.Integer, server_default='0', nullable=False),
        sa.Column('last_accessed_at', sa.DateTime, nullable=True),
        sa.Column('last_accessed_by', postgresql.UUID(as_uuid=True), nullable=True),
        sa.ForeignKeyConstraint(['uploaded_by'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['last_accessed_by'], ['users.id'], ondelete='SET NULL'),
        sa.Index('idx_raw_incidents_uploaded_by', 'uploaded_by', 'uploaded_at'),
        sa.Index('idx_raw_incidents_retention', 'retention_until'),
    )

    # Create anonymized_incidents table
    op.create_table(
        'anonymized_incidents',
        sa.Column('id', postgresql.UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), primary_key=True),
        sa.Column('raw_incident_id', postgresql.UUID(as_uuid=True), nullable=False, unique=True),
        sa.Column('anonymized_text', sa.Text, nullable=False),
        sa.Column('hash_salt', sa.String(255), nullable=False),
        sa.Column('processing_log', postgresql.JSONB, nullable=False),
        sa.Column('processing_time_ms', sa.Integer, nullable=False),
        sa.Column('status', sa.String(50), nullable=False, index=True),
        sa.Column('pii_detected', postgresql.JSONB, nullable=False),
        sa.Column('flagged_reason', sa.Text, nullable=True),
        sa.Column('created_at', sa.DateTime, server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('updated_at', sa.DateTime, server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.ForeignKeyConstraint(['raw_incident_id'], ['raw_incidents.id'], ondelete='CASCADE'),
        sa.Index('idx_anonymized_incidents_status', 'status'),
        sa.Index('idx_anonymized_incidents_created', 'created_at'),
    )

    # Create crime_categories table
    op.create_table(
        'crime_categories',
        sa.Column('id', postgresql.UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), primary_key=True),
        sa.Column('name', sa.String(100), nullable=False, unique=True),
        sa.Column('description', sa.Text, nullable=False),
        sa.Column('examples', postgresql.JSONB, nullable=False),
        sa.Column('urgency_indicators', postgresql.JSONB, nullable=True),
        sa.Column('is_active', sa.Boolean, server_default='true', nullable=False),
        sa.Column('created_by', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('created_at', sa.DateTime, server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('updated_at', sa.DateTime, server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.ForeignKeyConstraint(['created_by'], ['users.id'], ondelete='RESTRICT'),
        sa.Index('idx_crime_categories_active', 'is_active'),
        sa.Index('idx_crime_categories_name', 'name'),
    )

    # Create ai_classifications table
    op.create_table(
        'ai_classifications',
        sa.Column('id', postgresql.UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), primary_key=True),
        sa.Column('anonymized_incident_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('model_version', sa.String(100), nullable=False, index=True),
        sa.Column('suggested_crime_type', sa.String(100), nullable=False, index=True),
        sa.Column('suggested_urgency', sa.Integer, nullable=False),
        sa.Column('confidence_scores', postgresql.JSONB, nullable=False),
        sa.Column('explanation_data', postgresql.JSONB, nullable=True),
        sa.Column('inference_time_ms', sa.Integer, nullable=False),
        sa.Column('status', sa.String(50), nullable=False, index=True),
        sa.Column('created_at', sa.DateTime, server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('updated_at', sa.DateTime, server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.ForeignKeyConstraint(['anonymized_incident_id'], ['anonymized_incidents.id'], ondelete='CASCADE'),
        sa.Index('idx_ai_classifications_status', 'status'),
        sa.Index('idx_ai_classifications_crime', 'suggested_crime_type'),
        sa.Index('idx_ai_classifications_urgency', 'suggested_urgency'),
    )

    # Create human_validations table - gold standard for training
    op.create_table(
        'human_validations',
        sa.Column('id', postgresql.UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), primary_key=True),
        sa.Column('ai_classification_id', postgresql.UUID(as_uuid=True), nullable=False, unique=True),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('validated_crime_type', sa.String(100), nullable=False),
        sa.Column('validated_urgency', sa.Integer, nullable=False),
        sa.Column('confidence_level', sa.String(20), nullable=False),
        sa.Column('override_reason', sa.Text, nullable=True),
        sa.Column('review_time_seconds', sa.Integer, nullable=False),
        sa.Column('is_gold_standard', sa.Boolean, server_default='false', nullable=False),
        sa.Column('difficult_case', sa.Boolean, server_default='false', nullable=False),
        sa.Column('created_at', sa.DateTime, server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('updated_at', sa.DateTime, server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.ForeignKeyConstraint(['ai_classification_id'], ['ai_classifications.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='RESTRICT'),
        sa.Index('idx_human_validations_user', 'user_id'),
        sa.Index('idx_human_validations_confidence', 'confidence_level'),
    )

    # Create audit_logs table - immutable with hash chaining
    op.create_table(
        'audit_logs',
        sa.Column('id', postgresql.UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), primary_key=True),
        sa.Column('timestamp', sa.DateTime, server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False, index=True),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('action', sa.String(50), nullable=False, index=True),
        sa.Column('target_entity', sa.String(100), nullable=False),
        sa.Column('target_id', sa.String(100), nullable=False, index=True),
        sa.Column('ip_address', sa.String(45), nullable=False),
        sa.Column('session_id', sa.String(255), nullable=True),
        sa.Column('user_agent', sa.Text, nullable=True),
        sa.Column('metadata', postgresql.JSONB, nullable=False),
        sa.Column('prev_hash', sa.Text, nullable=False),
        sa.Column('signature', sa.Text, nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='RESTRICT'),
        sa.Index('idx_audit_logs_user_action', 'user_id', 'action'),
        sa.Index('idx_audit_logs_timestamp', 'timestamp'),
        sa.Index('idx_audit_logs_target', 'target_entity', 'target_id'),
    )

    # Insert default roles
    op.execute("""
        INSERT INTO roles (name, description, permissions) VALUES
        ('system_admin', 'System Administrator - Full system access', '["manage_users", "manage_categories", "view_audit_logs", "configure_system"]'),
        ('data_operator', 'Data Operator - Upload and anonymize incidents', '["upload_incidents", "view_anonymized", "download_anonymized"]'),
        ('prosecutor', 'Prosecutor - Review and validate AI classifications', '["view_anonymized", "validate_classifications", "view_audit_logs"]'),
        ('researcher', 'Researcher - View anonymized data for analytics', '["view_anonymized", "export_anonymized", "view_analytics"]')
    """)

    # Insert default crime categories
    op.execute("""
        INSERT INTO crime_categories (name, description, examples, created_by) VALUES
        ('Robo', 'Sustracción de bienes mediante violencia o intimidación', '["El acusado amenazó con un cuchillo y le quitó el celular", "Entraron por la fuerza al local y se llevaron mercadería"]', (SELECT id FROM roles WHERE name = 'system_admin')),
        ('Violencia de Género', 'Violencia ejercida contra mujeres por razón de su género', '["El denunciado le pegó porque ella no quería volver", "Le envía mensajes amenazantes si no responde"]', (SELECT id FROM roles WHERE name = 'system_admin')),
        ('Abuso de Autoridad', 'Uso indebido del poder por parte de agentes del estado', '["El policía le exigió dinero para no multarlo", "Amenazó con detenerlo sin causa"]', (SELECT id FROM roles WHERE name = 'system_admin')),
        ('Amenazas', 'Intimidación o amenaza de causar daño', '["Los acusados lo siguieron por varias cuadras amenazándolo", "Le dijo que si hablaba lo mataban"]', (SELECT id FROM roles WHERE name = 'system_admin')),
        ('Lesiones', 'Causar lesiones físicas a otra persona', '["Le pegó y le fracturó el brazo", "Le ocasionó una herida que requirió sutura"]', (SELECT id FROM roles WHERE name = 'system_admin'))
    """)


def downgrade() -> None:
    # Drop tables in reverse order (respect foreign keys)
    op.drop_table('audit_logs')
    op.drop_table('human_validations')
    op.drop_table('ai_classifications')
    op.drop_table('crime_categories')
    op.drop_table('anonymized_incidents')
    op.drop_table('raw_incidents')
    op.drop_table('users')
    op.drop_table('roles')

    # Drop pgcrypto extension
    op.execute("DROP EXTENSION IF EXISTS pgcrypto")
