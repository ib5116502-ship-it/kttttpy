import time

from src.core.celery_app import celery_app


@celery_app.task(name="notifications.send_booking_confirmation")
def send_booking_confirmation(booking_id: int, user_email: str, room_name: str) -> dict:
    # Имитация отправки уведомления (например, email или webhook)
    time.sleep(2)
    msg = f"Booking #{booking_id} confirmed for {user_email} on room '{room_name}'"
    print(f"[CELERY TASK] {msg}")
    return {"status": "sent", "message": msg}   