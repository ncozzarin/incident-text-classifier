from sqlalchemy import create_engine, Column, Integer, String, Text, Boolean, DateTime, ForeignKey, JSON, Numeric, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy.dialects.postgresql import UUID, JSONB
import uuid
from datetime import datetime

Base = declarative_base()


class TimestampMixin:
    """Mixin to add timestamp columns to models"""
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)


class User(Base, TimestampMixin):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False, index=True)
    full_name = Column(String(255), nullable=True)
    hashed_password = Column(String(255), nullable=False)
    role = Column(String(50), nullable=False, index=True)
    is_active = Column(Boolean, default=True, nullable=False)
    last_login = Column(DateTime, nullable=True)

    # Relationships
    uploaded_incidents = relationship("RawIncident", back_populates="uploaded_by_user", foreign_keys="[RawIncident.uploaded_by]")
    accessed_incidents = relationship("RawIncident", back_populates="last_accessed_by_user", foreign_keys="[RawIncident.last_accessed_by]")
    validations = relationship("HumanValidation", back_populates="validated_by_user")
    audit_logs = relationship("AuditLog", back_populates="user")

    __table_args__ = (
        Index('idx_users_email_active', 'email', 'is_active'),
        Index('idx_users_role_active', 'role', 'is_active'),
    )


class Role(Base, TimestampMixin):
    __tablename__ = "roles"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(50), unique=True, nullable=False)
    description = Column(Text, nullable=True)
    permissions = Column(JSONB, nullable=False)  # List of permission strings
    is_active = Column(Boolean, default=True, nullable=False)

    __table_args__ = (Index('idx_roles_name_active', 'name', 'is_active'),)


class RawIncident(Base):
    __tablename__ = "raw_incidents"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    encrypted_payload = Column(Text, nullable=False)  # AES-256-GCM encrypted
    file_name = Column(String(500), nullable=False)
    file_size = Column(Integer, nullable=False)
    mime_type = Column(String(100), nullable=False)
    upload_metadata = Column(JSONB, nullable=False)  # Original headers, structure validation
    uploaded_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    uploaded_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    retention_until = Column(DateTime, nullable=False)  # 7 years from upload
    retention_reason = Column(String(200), nullable=False)  # Legal basis
    access_count = Column(Integer, default=0, nullable=False)  # Audit trail
    last_accessed_at = Column(DateTime, nullable=True)
    last_accessed_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)

    # Relationships
    uploaded_by_user = relationship("User", foreign_keys=[uploaded_by], back_populates="uploaded_incidents")
    last_accessed_by_user = relationship("User", foreign_keys=[last_accessed_by], back_populates="accessed_incidents")
    anonymized_incident = relationship("AnonymizedIncident", back_populates="raw_incident", uselist=False)

    __table_args__ = (
        Index('idx_raw_incidents_uploaded_by', 'uploaded_by', 'uploaded_at'),
        Index('idx_raw_incidents_retention', 'retention_until'),
    )


class AnonymizedIncident(Base, TimestampMixin):
    __tablename__ = "anonymized_incidents"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    raw_incident_id = Column(UUID(as_uuid=True), ForeignKey("raw_incidents.id"), nullable=False, unique=True)
    anonymized_text = Column(Text, nullable=False)
    hash_salt = Column(String(255), nullable=False)  # For reproducible hashing
    processing_log = Column(JSONB, nullable=False)  # Step-by-step anonymization log
    processing_time_ms = Column(Integer, nullable=False)
    status = Column(String(50), nullable=False, index=True)  # processing, completed, failed, flagged
    pii_detected = Column(JSONB, nullable=False)  # Array of PII types found
    flagged_reason = Column(Text, nullable=True)  # If leakage or error detected

    # Relationships
    raw_incident = relationship("RawIncident", back_populates="anonymized_incident")
    ai_classifications = relationship("AIClassification", back_populates="anonymized_incident")

    __table_args__ = (
        Index('idx_anonymized_incidents_status', 'status'),
        Index('idx_anonymized_incidents_created', 'created_at'),
    )


class CrimeCategory(Base, TimestampMixin):
    __tablename__ = "crime_categories"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(100), unique=True, nullable=False)
    description = Column(Text, nullable=False)
    examples = Column(JSONB, nullable=False)  # Text examples for ML training
    urgency_indicators = Column(JSONB, nullable=True)  # Keywords that suggest urgency
    is_active = Column(Boolean, default=True, nullable=False)
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)

    # Relationships
    created_by_user = relationship("User", foreign_keys=[created_by])
    classifications = relationship("AIClassification", back_populates="crime_category")

    __table_args__ = (
        Index('idx_crime_categories_active', 'is_active'),
        Index('idx_crime_categories_name', 'name'),
    )


class AIClassification(Base, TimestampMixin):
    __tablename__ = "ai_classifications"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    anonymized_incident_id = Column(UUID(as_uuid=True), ForeignKey("anonymized_incidents.id"), nullable=False)
    model_version = Column(String(100), nullable=False, index=True)
    suggested_crime_type = Column(String(100), nullable=False, index=True)
    suggested_urgency = Column(Integer, nullable=False)  # 1-5 mapping to P1-P5
    confidence_scores = Column(JSONB, nullable=False)  # { "crime_type": {...}, "urgency": {...} }
    explanation_data = Column(JSONB, nullable=True)  # Attention weights, SHAP values
    inference_time_ms = Column(Integer, nullable=False)
    status = Column(String(50), nullable=False, index=True)  # pending_validation, validated, overridden

    # Relationships
    anonymized_incident = relationship("AnonymizedIncident", back_populates="ai_classifications")
    crime_category = relationship("CrimeCategory", foreign_keys=[suggested_crime_type], back_populates="classifications")
    human_validation = relationship("HumanValidation", back_populates="ai_classification", uselist=False)

    __table_args__ = (
        Index('idx_ai_classifications_status', 'status'),
        Index('idx_ai_classifications_crime', 'suggested_crime_type'),
        Index('idx_ai_classifications_urgency', 'suggested_urgency'),
    )


class HumanValidation(Base, TimestampMixin):
    __tablename__ = "human_validations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    ai_classification_id = Column(UUID(as_uuid=True), ForeignKey("ai_classifications.id"), nullable=False, unique=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    validated_crime_type = Column(String(100), nullable=False)
    validated_urgency = Column(Integer, nullable=False)
    confidence_level = Column(String(20), nullable=False)  # high, medium, low
    override_reason = Column(Text, nullable=True)
    review_time_seconds = Column(Integer, nullable=False)

    # For training - gold standard used for model improvement
    is_gold_standard = Column(Boolean, default=False, nullable=False)
    difficult_case = Column(Boolean, default=False, nullable=False)  # For active learning

    # Relationships
    ai_classification = relationship("AIClassification", back_populates="human_validation")
    validated_by_user = relationship("User", foreign_keys=[user_id], back_populates="validations")

    __table_args__ = (
        Index('idx_human_validations_user', 'user_id'),
        Index('idx_human_validations_confidence', 'confidence_level'),
    )


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    action = Column(String(50), nullable=False, index=True)  # UPLOAD, ANONYMIZE, CLASSIFY, VALIDATE, ACCESS_VAULT
    target_entity = Column(String(100), nullable=False)
    target_id = Column(String(100), nullable=False, index=True)
    ip_address = Column(String(45), nullable=False)  # IPv6 compatible
    session_id = Column(String(255), nullable=True)
    user_agent = Column(Text, nullable=True)
    metadata = Column(JSONB, nullable=False)
    prev_hash = Column(Text, nullable=False)  # Hash of previous entry
    signature = Column(Text, nullable=False)  # HMAC of this entry

    # Relationships
    user = relationship("User", foreign_keys=[user_id], back_populates="audit_logs")

    __table_args__ = (
        Index('idx_audit_logs_user_action', 'user_id', 'action'),
        Index('idx_audit_logs_timestamp', 'timestamp'),
        Index('idx_audit_logs_target', 'target_entity', 'target_id'),
    )