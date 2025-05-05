from typing import List

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from starlette import status

from app.core.security import get_current_active_user
from app.crud.alert import alert_crud
from app.db.session import get_db
from app.schemas.alert import Alert, AlertCreate, AlertUpdate
from app.models.user import User
from app.services.notification.email import EmailNotifier

router = APIRouter()

@router.get("/", response_model=List[Alert])
def read_alerts(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_active_user),
):
    """Retrieve alerts for current user"""
    alerts = alert_crud.get_multi_by_owner(
        db, user_id=current_user.id, skip=skip, limit=limit
    )
    return alerts

@router.post("/", response_model=Alert)
def create_alert(
    *,
    db: Session = Depends(get_db),
    alert_in: AlertCreate,
    current_user: User = Depends(get_current_active_user),
    background_tasks: BackgroundTasks,
):
    """Create new alert for current user"""
    alert = alert_crud.create_with_owner(
        db=db, obj_in=alert_in, user_id=current_user.id
    )
    
    # Immediately check if condition is met
    background_tasks.add_task(
        check_alert_condition,
        alert_id=alert.id,
        db=db
    )
    
    return alert

@router.put("/{alert_id}", response_model=Alert)
def update_alert(
    *,
    db: Session = Depends(get_db),
    alert_id: int,
    alert_in: AlertUpdate,
    current_user: User = Depends(get_current_active_user),
):
    """Update existing alert"""
    alert = alert_crud.get(db, id=alert_id)
    if not alert:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Alert not found"
        )
    if alert.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    alert = alert_crud.update(db, db_obj=alert, obj_in=alert_in)
    return alert

@router.delete("/{alert_id}", response_model=Alert)
def delete_alert(
    *,
    db: Session = Depends(get_db),
    alert_id: int,
    current_user: User = Depends(get_current_active_user),
):
    """Delete existing alert"""
    alert = alert_crud.get(db, id=alert_id)
    if not alert:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Alert not found"
        )
    if alert.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    alert = alert_crud.remove(db, id=alert_id)
    return alert

def check_alert_condition(alert_id: int, db: Session):
    """Background task to check if alert condition is met"""
    from app.tasks.price_checks import check_alert
    check_alert.delay(alert_id)
    