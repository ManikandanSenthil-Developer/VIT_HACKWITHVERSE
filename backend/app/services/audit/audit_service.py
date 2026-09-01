import json
import logging
from typing import Any, Dict, Optional
from sqlalchemy.orm import Session
from app.models.audit import AuditLog

logger = logging.getLogger("mats.audit")


class AuditService:
    @staticmethod
    def log_event(
        db: Session,
        action: str,
        user_id: Optional[int] = None,
        resource_type: Optional[str] = None,
        resource_id: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        ip_address: Optional[str] = None,
        status: str = "SUCCESS",
    ) -> AuditLog:
        """
        Record a security or operational event to the audit trail.
        Never store raw passwords, tokens, or credentials in details.
        """
        # Sanitize details to guarantee zero credential leakage
        sanitized_details = {}
        if details:
            for k, v in details.items():
                if any(sensitive in k.lower() for sensitive in ["password", "token", "secret", "authorization"]):
                    sanitized_details[k] = "[REDACTED]"
                else:
                    sanitized_details[k] = v

        details_json = json.dumps(sanitized_details) if sanitized_details else None

        audit_entry = AuditLog(
            user_id=user_id,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            details_json=details_json,
            ip_address=ip_address,
            status=status,
        )
        db.add(audit_entry)
        try:
            db.commit()
            db.refresh(audit_entry)
        except Exception as e:
            db.rollback()
            logger.error(f"Failed to record audit log: {e}")

        logger.info(
            f"[AUDIT] action={action} user_id={user_id} status={status} "
            f"resource={resource_type}:{resource_id} ip={ip_address}"
        )
        return audit_entry


audit_service = AuditService()
