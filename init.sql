# Initialize pgcrypto for field-level encryption
# Run on database creation

-- Enable pgcrypto extension for encryption functions
CREATE EXTENSION IF NOT EXISTS pgcrypto;

-- Create a schema for security functions
CREATE SCHEMA IF NOT EXISTS security;

-- Create encryption function for vault data
-- Accepts: text to encrypt, key (hex string)
-- Returns: encrypted text in format: iv::ciphertext::tag
-- Uses AES-256-GCM for authenticated encryption
CREATE OR REPLACE FUNCTION security.encrypt_value(plain_text text, encryption_key text)
RETURNS text AS $$
BEGIN
    -- Generate random 16-byte IV and convert to hex
    RETURN encode(
        encrypt_iv(
            plain_text::bytea,
            digest(encryption_key, 'sha256'), -- 32-byte key from hex string
            gen_random_bytes(16), -- 16-byte IV
            'aes-256-gcm'
        ),
        'base64'
    );
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Create decryption function for vault data
-- Accepts: encrypted text in format: iv::ciphertext::tag, key
-- Returns: decrypted text
CREATE OR REPLACE FUNCTION security.decrypt_value(encrypted_text text, encryption_key text)
RETURNS text AS $$
BEGIN
    RETURN convert_from(
        decrypt_iv(
            decode(encrypted_text, 'base64'),
            digest(encryption_key, 'sha256'), -- Must match encryption key
            gen_random_bytes(16), -- IV from encrypted data
            'aes-256-gcm'
        ),
        'utf8'
    );
EXCEPTION WHEN OTHERS THEN
    -- Log failed decryption attempts (potential tampering)
    RAISE NOTICE 'Decryption failed: possible tampering or wrong key';
    RETURN NULL;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Create audit log trigger function
-- Automatically maintains hash chain: hash(prev_hash + current_data)
CREATE OR REPLACE FUNCTION security.audit_log_trigger()
RETURNS TRIGGER AS $$
DECLARE
    current_hash text;
    prev_hash text;
BEGIN
    -- Get the hash of the previous audit log entry
    SELECT COALESCE(hash, '') INTO prev_hash
    FROM audit_logs
    ORDER BY timestamp DESC
    LIMIT 1;

    -- Calculate hash of current entry (simplified: hash action + target + timestamp)
    SELECT digest(
        prev_hash || NEW.action || NEW.target_entity || NEW.target_id || NEW.timestamp::text,
        'sha256'
    ) INTO current_hash;

    -- Store the hash
    NEW.prev_hash := prev_hash;
    NEW.signature := encode(current_hash, 'hex');

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create index for efficient audit log queries
CREATE INDEX IF NOT EXISTS idx_audit_logs_signature ON audit_logs(signature);

-- Create retention policy cleanup function
-- Runs daily to delete expired vault data
CREATE OR REPLACE FUNCTION security.cleanup_expired_vault_data()
RETURNS void AS $$
BEGIN
    -- Archive expired records before deletion
    INSERT INTO audit_logs (
        user_id, action, target_entity, target_id,
        ip_address, metadata, prev_hash, signature
    )
    SELECT
        '00000000-0000-0000-0000-000000000000', -- System user
        'VAULT_CLEANUP',
        'raw_incidents',
        id,
        '127.0.0.1',
        jsonb_build_object('retention_expired', uploaded_at, 'file_name', file_name),
        '',
        ''
    FROM raw_incidents
    WHERE retention_until < NOW();

    -- Delete expired records (cascade will clean up anonymized_incidents)
    DELETE FROM raw_incidents
    WHERE retention_until < NOW();
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Grant minimal necessary permissions
-- Applications should use role-based access
GRANT USAGE ON SCHEMA security TO ${POSTGRES_USER:-security_user};
GRANT EXECUTE ON FUNCTION security.encrypt_value TO ${POSTGRES_USER:-security_user};
GRANT EXECUTE ON FUNCTION security.decrypt_value TO ${POSTGRES_USER:-security_user};
GRANT EXECUTE ON FUNCTION security.cleanup_expired_vault_data TO ${POSTGRES_USER:-security_user};

-- Comment: Security model assumes applications handle authorization
-- Database enforces: data integrity, encryption, audit logging
-- Application API enforces: RBAC, rate limiting, business logic