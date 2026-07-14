import logging
from uuid import UUID
from fastapi import Request
from sqlalchemy.ext.asyncio import AsyncSession

from models.audit_log import AuditLog

logger = logging.getLogger("audit")

async def log_audit_event(
    db: AsyncSession,
    event: str,
    request: Request,
    actor_id: UUID | None = None,
    target_id: UUID | None = None,
    target_type: str | None = None,
    metadata: dict | None = None,
) -> None:
    """Log an audit event to the database. Does not commit the transaction automatically."""
    ip_address = request.client.host if request.client else None
    user_agent = request.headers.get("user-agent", "")[:500]
    
    try:
        audit_log = AuditLog(
            event=event,
            actor_id=actor_id,
            target_id=target_id,
            target_type=target_type,
            ip_address=ip_address,
            user_agent=user_agent,
            event_metadata=metadata or {}
        )
        db.add(audit_log)
        await db.flush()  # Flush to populate default database fields without committing
    except Exception as e:
        logger.error(f"Failed to log audit event {event}: {e}")
