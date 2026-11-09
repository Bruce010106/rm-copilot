from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session, selectinload

from app.db import get_session
from app.models import Customer, Holding
from app.schemas import CustomerDetail, CustomerPage, CustomerSummary, HoldingOut, InteractionOut

router = APIRouter(prefix="/customers", tags=["customers"])


@router.get("", response_model=CustomerPage)
def list_customers(
    q: str | None = Query(None, description="按姓名或客户 ID 搜索"),
    tier: str | None = None,
    rm_id: str | None = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    session: Session = Depends(get_session),
) -> CustomerPage:
    stmt = select(Customer)
    if q:
        stmt = stmt.where(or_(Customer.name.contains(q), Customer.id == q))
    if tier:
        stmt = stmt.where(Customer.tier == tier)
    if rm_id:
        stmt = stmt.where(Customer.rm_id == rm_id)

    total = session.scalar(select(func.count()).select_from(stmt.subquery())) or 0
    rows = session.scalars(
        stmt.order_by(Customer.aum.desc()).offset((page - 1) * page_size).limit(page_size)
    ).all()
    return CustomerPage(
        items=[CustomerSummary.model_validate(c) for c in rows],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get("/{customer_id}", response_model=CustomerDetail)
def get_customer(customer_id: str, session: Session = Depends(get_session)) -> CustomerDetail:
    customer = session.scalar(
        select(Customer)
        .where(Customer.id == customer_id)
        .options(
            selectinload(Customer.rm),
            selectinload(Customer.holdings).selectinload(Holding.product),
            selectinload(Customer.interactions),
        )
    )
    if customer is None:
        raise HTTPException(status_code=404, detail="customer not found")

    return CustomerDetail(
        **CustomerSummary.model_validate(customer).model_dump(),
        gender=customer.gender,
        birth_date=customer.birth_date,
        occupation=customer.occupation,
        onboarded_at=customer.onboarded_at,
        rm_name=customer.rm.name,
        holdings=[
            HoldingOut(
                id=h.id,
                product_id=h.product_id,
                product_name=h.product.name,
                category=h.product.category,
                amount=h.amount,
                start_date=h.start_date,
                maturity_date=h.maturity_date,
            )
            for h in sorted(customer.holdings, key=lambda h: h.amount, reverse=True)
        ],
        interactions=[InteractionOut.model_validate(i) for i in customer.interactions],
    )
