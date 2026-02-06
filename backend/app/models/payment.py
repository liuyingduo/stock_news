from datetime import datetime
from typing import Literal, Optional, List
from pydantic import BaseModel, Field


class Plan(BaseModel):
    id: str
    name: str
    monthly_price: int
    annual_discount_rate: float
    features: List[str] = Field(default_factory=list)


class CreateOrderRequest(BaseModel):
    plan_id: str
    billing_cycle: Literal["monthly", "annual"]
    channel: Literal["wechat", "alipay"]


class PaymentOrderResponse(BaseModel):
    order_id: str
    out_trade_no: str
    plan_id: str
    billing_cycle: Literal["monthly", "annual"]
    channel: Literal["wechat", "alipay"]
    amount: int
    currency: str = "CNY"
    qr_code_url: str
    status: str
    created_at: datetime


class PaymentOrderStatus(BaseModel):
    order_id: str
    status: str
    paid_at: Optional[datetime] = None
    plan_id: Optional[str] = None
    billing_cycle: Optional[str] = None
    channel: Optional[str] = None
