from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Request
from app.models.payment import CreateOrderRequest, PaymentOrderResponse, PaymentOrderStatus, Plan
from app.models.user import UserResponse
from app.services.auth import get_current_user
from app.services.payment_service import (
    PLAN_CONFIG,
    create_payment_order,
    get_order_by_id,
    handle_alipay_notify,
    handle_wechat_notify,
)

router = APIRouter(prefix="/api/payments", tags=["payments"])


@router.get("/plans", response_model=list[Plan])
async def get_plans():
    return list(PLAN_CONFIG.values())


@router.post("/orders", response_model=PaymentOrderResponse)
async def create_order(
    data: CreateOrderRequest,
    current_user: UserResponse = Depends(get_current_user),
):
    if not current_user:
        raise HTTPException(status_code=401, detail="未登录")

    order = await create_payment_order(
        user_id=current_user.id,
        user_email=current_user.email,
        plan_id=data.plan_id,
        billing_cycle=data.billing_cycle,
        channel=data.channel,
    )

    return PaymentOrderResponse(
        order_id=str(order["_id"]),
        out_trade_no=order["out_trade_no"],
        plan_id=order["plan_id"],
        billing_cycle=order["billing_cycle"],
        channel=order["channel"],
        amount=order["amount"],
        currency=order.get("currency", "CNY"),
        qr_code_url=order["qr_code_url"],
        status=order["status"],
        created_at=order["created_at"],
    )


@router.get("/orders/{order_id}", response_model=PaymentOrderStatus)
async def get_order(order_id: str, current_user: UserResponse = Depends(get_current_user)):
    if not current_user:
        raise HTTPException(status_code=401, detail="未登录")

    try:
        order = await get_order_by_id(order_id)
    except Exception:
        raise HTTPException(status_code=400, detail="无效订单")

    if not order or str(order.get("user_id")) != current_user.id:
        raise HTTPException(status_code=404, detail="订单不存在")

    return PaymentOrderStatus(
        order_id=str(order["_id"]),
        status=order.get("status", "pending"),
        paid_at=order.get("paid_at"),
        plan_id=order.get("plan_id"),
        billing_cycle=order.get("billing_cycle"),
        channel=order.get("channel"),
    )


@router.post("/notify/wechat")
async def wechat_notify(request: Request):
    payload = await request.json()
    await handle_wechat_notify(payload)
    return {"code": "SUCCESS", "message": "成功"}


@router.post("/notify/alipay")
async def alipay_notify(request: Request):
    form = await request.form()
    params = dict(form)
    await handle_alipay_notify(params)
    return "success"
