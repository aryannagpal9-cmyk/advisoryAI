import hashlib
import hmac
import os
from datetime import datetime, timedelta
from uuid import UUID

SECRET_KEY = os.getenv("APP_SECRET", "dev-secret-key-123")

class SecurityService:
    """
    Handles robust, time-limited secure link generation.
    """
    
    @staticmethod
    def generate_upload_token(request_id: UUID, expires_in_hours: int = 48) -> str:
        """
        Generates a signed token for a specific request.
        """
        expires_at = datetime.utcnow() + timedelta(hours=expires_in_hours)
        payload = f"{request_id}:{expires_at.timestamp()}"
        
        signature = hmac.new(
            SECRET_KEY.encode(),
            payload.encode(),
            hashlib.sha256
        ).hexdigest()
        
        return f"{payload}:{signature}"

    @staticmethod
    def validate_token(token: str, request_id: UUID) -> bool:
        try:
            payload, signature = token.rsplit(":", 1)
            req_id_str, timestamp_str = payload.split(":")
            
            # 1. Verify Request ID matches
            if req_id_str != str(request_id):
                return False
                
            # 2. Verify Signature
            expected_signature = hmac.new(
                SECRET_KEY.encode(),
                payload.encode(),
                hashlib.sha256
            ).hexdigest()
            
            if not hmac.compare_digest(signature, expected_signature):
                return False
                
            # 3. Verify Expiry
            expires_at = datetime.fromtimestamp(float(timestamp_str))
            if datetime.utcnow() > expires_at:
                return False
                
            return True
            
        except Exception:
            return False
