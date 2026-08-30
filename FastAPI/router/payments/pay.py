from fastapi import APIRouter, Depends, HTTPException, status
from urllib.parse import quote
import uuid
from router.auth.deps import get_current_user
from router.auth.schemas import UserResponse
from database.user_data import get_user_by_id
from database.exp_data import record_settlement
from .schemas import SettleUpRequest, SettleUpResponse, UPILinkRequest, UPILinkResponse

payments = APIRouter(prefix="/payments", tags=["payments"])

#need record_settlement
#need get_friends
#need exp of a friend

@payments.post("/settle", response_model=SettleUpResponse)
def settle_up(body: SettleUpRequest, current_user: UserResponse = Depends(get_current_user)):
    paid_by = get_user_by_id(str(current_user.id))
    received_to = get_user_by_id(str(body.receiver_id))

    if not paid_by or not received_to:
        raise HTTPException(status_code=404, detail="Payer or Receiver user not found")

    if paid_by["id"] == received_to["id"]:
        raise HTTPException(status_code=400, detail="You cannot settle up with yourself")
    try:
        record_settlement(paid_by["id"], received_to["id"], body.amount, body.notes)
        new_balance = (paid_by["exp_frnd"] or {}).get(received_to["id"], 0)

        upi_link_response = None
        if body.payment_method == "UPI":
            payee_upi = received_to.get("email") or f"{received_to.get('name', 'payee').replace(' ', '').lower()}@upi"
            encoded_name = quote(received_to.get("name", "Payee"))
            encoded_note = quote(body.notes or "UdharrDe Settlement")
            upi_url = f"upi://pay?pa={payee_upi}&pn={encoded_name}&am={body.amount:.2f}&cu=INR&tn={encoded_note}"
            encoded_upi_url = quote(upi_url)
            qr_code_url = f"https://quickchart.io/qr?text={encoded_upi_url}&size=300"
            upi_link_response = UPILinkResponse(
                upi_url=upi_url,
                qr_code_url=qr_code_url,
                payee_upi=payee_upi,
                amount=body.amount,
                payer_name=paid_by.get("name", "Payer"),
                payee_name=received_to.get("name", "Payee")
            )

        return SettleUpResponse(
            message="Settlement recorded successfully",
            payer_id=uuid.UUID(paid_by["id"]),
            receiver_id=uuid.UUID(received_to["id"]),
            amount_settled=body.amount,
            net_balance_with_friend=new_balance,
            upi_link=upi_link_response,
            method=body.payment_method
        )
    except Exception as err:
        raise HTTPException(status_code=400, detail=str(err))

@payments.post("/upi-link", response_model=UPILinkResponse)
def generate_upi_link(body: UPILinkRequest, current_user: UserResponse = Depends(get_current_user)):
    encoded_name = quote(body.payee_name)
    encoded_note = quote(body.note or "UdharrDe Settlement")
    
    # 1. Standard Indian UPI URI Scheme (compatible with GPay, PhonePe, Paytm, BHIM)
    upi_url = f"upi://pay?pa={body.payee_upi}&pn={encoded_name}&am={body.amount:.2f}&cu=INR&tn={encoded_note}"
    
    # 2. QR Code image URL via quickchart.io QR generator API
    encoded_upi_url = quote(upi_url)
    qr_code_url = f"https://quickchart.io/qr?text={encoded_upi_url}&size=300"

    return UPILinkResponse(
        upi_url=upi_url,
        qr_code_url=qr_code_url,
        payee_upi=body.payee_upi,
        amount=body.amount,
        payer_name=body.payer_name,
        payee_name=body.payee_name
    )