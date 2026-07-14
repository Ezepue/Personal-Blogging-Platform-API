"""Content reporting: readers flag stories or comments; admins review them."""
import logging
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, require_admin
from app.db.session import get_db
from app.models.report import ReportDB
from app.models.user import UserDB
from app.schemas.report import ReportCreate, ReportResponse
from app.services import get_article_by_id, get_comment_by_id, can_view_article

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/", response_model=ReportResponse)
def create_report(
    report: ReportCreate,
    db: Session = Depends(get_db),
    current_user: UserDB = Depends(get_current_user),
):
    """File a report against a story or a comment."""
    if report.article_id is not None:
        article = get_article_by_id(db, report.article_id)
        if not can_view_article(article, current_user):
            raise HTTPException(status_code=404, detail="Article not found")
    if report.comment_id is not None:
        get_comment_by_id(db, report.comment_id)

    new_report = ReportDB(
        reporter_id=current_user.id,
        article_id=report.article_id,
        comment_id=report.comment_id,
        reason=report.reason,
    )
    db.add(new_report)
    db.commit()
    db.refresh(new_report)
    logger.info(f"User {current_user.id} filed report {new_report.id}")
    return new_report


@router.get("/", response_model=List[ReportResponse])
def list_reports(
    db: Session = Depends(get_db),
    current_user: UserDB = Depends(require_admin),
    status: Optional[str] = None,
):
    """Review queue for admins, optionally filtered by status (open/resolved)."""
    query = db.query(ReportDB)
    if status in {"open", "resolved"}:
        query = query.filter(ReportDB.status == status)
    return query.order_by(ReportDB.id.desc()).limit(200).all()


@router.put("/{report_id}/resolve", response_model=ReportResponse)
def resolve_report(
    report_id: int,
    db: Session = Depends(get_db),
    current_user: UserDB = Depends(require_admin),
):
    """Mark a report as resolved."""
    report = db.query(ReportDB).filter(ReportDB.id == report_id).first()
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    report.status = "resolved"
    db.commit()
    db.refresh(report)
    return report
