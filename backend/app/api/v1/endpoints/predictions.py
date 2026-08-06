"""AI Predictions and Risk endpoints."""
from typing import Literal

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_active_user, get_db
from app.models.prediction import Prediction
from app.models.risk_score import RiskScore
from app.models.user import User
from app.services.ai_service import AIService
from app.services.business_service import BusinessService

router = APIRouter(prefix="/predictions", tags=["AI Predictions"])


async def _get_business(business_id: int, user: User, db):
    svc = BusinessService(db)
    biz = await svc.get_by_id(business_id)
    if not biz or (biz.owner_id != user.id and user.role.value != "admin"):
        raise HTTPException(status_code=404, detail="Business not found")
    return biz


@router.post("/{business_id}/forecast")
async def run_forecast(
    business_id: int,
    horizon: Literal[7, 15, 30, 90] = Query(30, description="Forecast horizon in days"),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Run cash flow forecast for the specified horizon."""
    business = await _get_business(business_id, current_user, db)
    ai = AIService(db)
    return await ai.run_cash_flow_forecast(business, horizon_days=horizon)


@router.get("/{business_id}/forecast/history")
async def forecast_history(
    business_id: int,
    limit: int = Query(10, ge=1, le=50),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Get historical forecast records."""
    await _get_business(business_id, current_user, db)
    result = await db.execute(
        select(Prediction)
        .where(Prediction.business_id == business_id)
        .order_by(Prediction.created_at.desc())
        .limit(limit)
    )
    predictions = result.scalars().all()
    return [
        {
            "id": p.id,
            "type": p.prediction_type.value,
            "predicted_value": p.predicted_value,
            "confidence_score": p.confidence_score,
            "prediction_date": p.prediction_date.isoformat(),
            "model_name": p.model_name,
        }
        for p in predictions
    ]


@router.post("/{business_id}/anomalies")
async def run_anomaly_detection(
    business_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Detect anomalous expenses using Isolation Forest."""
    business = await _get_business(business_id, current_user, db)
    ai = AIService(db)
    return await ai.run_anomaly_detection(business_id)


@router.post("/{business_id}/health-score")
async def run_health_score(
    business_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Calculate business health score."""
    business = await _get_business(business_id, current_user, db)
    ai = AIService(db)
    return await ai.run_health_score(business)


@router.get("/{business_id}/health-score/history")
async def health_score_history(
    business_id: int,
    limit: int = Query(30, ge=1, le=90),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Historical health scores for trend chart."""
    await _get_business(business_id, current_user, db)
    result = await db.execute(
        select(RiskScore)
        .where(RiskScore.business_id == business_id)
        .order_by(RiskScore.score_date.asc())
        .limit(limit)
    )
    scores = result.scalars().all()
    return [
        {
            "date": s.score_date.isoformat(),
            "health_score": s.health_score,
            "risk_score": s.risk_score,
            "rating": s.rating,
        }
        for s in scores
    ]


@router.post("/{business_id}/shortage")
async def run_shortage_prediction(
    business_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Predict probability of cash shortage."""
    business = await _get_business(business_id, current_user, db)
    ai = AIService(db)
    return await ai.run_shortage_prediction(business)


@router.post("/{business_id}/recommendations")
async def run_recommendations(
    business_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Generate AI recommendations."""
    business = await _get_business(business_id, current_user, db)
    ai = AIService(db)
    return await ai.run_recommendations(business)


@router.get("/{business_id}/recommendations/saved")
async def get_saved_recommendations(
    business_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Get saved recommendations for a business."""
    from app.models.recommendation import Recommendation
    await _get_business(business_id, current_user, db)
    result = await db.execute(
        select(Recommendation)
        .where(
            Recommendation.business_id == business_id,
            Recommendation.is_dismissed == False,
        )
        .order_by(Recommendation.created_at.desc())
        .limit(20)
    )
    import json
    recs = result.scalars().all()
    return [
        {
            "id": r.id,
            "title": r.title,
            "description": r.description,
            "category": r.category.value,
            "priority": r.priority.value,
            "estimated_impact": r.estimated_impact,
            "confidence": r.confidence,
            "action_items": json.loads(r.action_items) if r.action_items else [],
            "is_read": r.is_read,
            "is_implemented": r.is_implemented,
            "created_at": r.created_at.isoformat(),
        }
        for r in recs
    ]
