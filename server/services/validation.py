import os

ALLOWED_EXTENSIONS = {'.pdf', '.jpg', '.jpeg', '.png'}
MAX_SIZE_MB = 10

class ValidationService:
    """
    Conservative, deterministic document validation.
    No "AI" guessing. Just strict physics checks.
    """
    
    @staticmethod
    def validate_file(filename: str, size_bytes: int, content_type: str) -> dict:
        """
        Returns {'valid': bool, 'reason': str}
        """
        # 1. Size Check
        if size_bytes > MAX_SIZE_MB * 1024 * 1024:
            return {"valid": False, "reason": f"File too large (> {MAX_SIZE_MB}MB)"}
        
        if size_bytes < 1024: # < 1KB
            return {"valid": False, "reason": "File suspiciously small (< 1KB)"}

        # 2. Extension Check
        ext = os.path.splitext(filename)[1].lower()
        if ext not in ALLOWED_EXTENSIONS:
            return {"valid": False, "reason": f"Unsupported file type: {ext}"}
            
        return {"valid": True, "reason": "OK"}
