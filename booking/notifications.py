from django.core.mail import send_mail, EmailMultiAlternatives
from django.conf import settings
from django.template.loader import render_to_string


# -----------------------------------------------------
# Helpers (now REAL data from Booking)
# -----------------------------------------------------
def get_user_email(booking):
    return booking.guest_email


def get_user_phone(booking):
    return booking.guest_phone


# -----------------------------------------------------
# EMAIL / WHATSAPP / SMS NOTIFICATIONS
# -----------------------------------------------------
def send_booking_confirmation(booking):
    subject = "GoExplorer - Booking Confirmed 🎉"

    text_message = f"""
Booking Confirmed

Booking ID: {booking.id}
Hotel: {booking.room_type.hotel.name}
Room: {booking.room_type.name}
Check-in: {booking.check_in}
Check-out: {booking.check_out}
"""

    html_message = render_to_string(
        "booking/emails/booking_confirmed.html",
        {"booking": booking}
    )

    email = EmailMultiAlternatives(
        subject=subject,
        body=text_message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[get_user_email(booking)]
    )
    email.attach_alternative(html_message, "text/html")
    email.send(fail_silently=True)

    print("📧 Booking confirmation email sent")
    send_whatsapp(text_message, booking)
    send_sms(text_message, booking)


def send_booking_cancellation(booking):
    subject = "GoExplorer - Booking Cancelled ❌"

    message = f"""
Booking Cancelled

Booking ID: {booking.id}
Refund (if applicable) will be processed.
"""

    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [get_user_email(booking)],
        fail_silently=True,
    )

    print("📧 Booking cancellation email sent")
    send_whatsapp(message, booking)
    send_sms(message, booking)


def send_payment_failed(booking):
    subject = "GoExplorer - Payment Failed ⚠️"

    message = f"""
Payment Failed

Booking ID: {booking.id}
Please retry payment.
"""

    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [get_user_email(booking)],
        fail_silently=True,
    )

    print("📧 Payment failed email sent")
    send_whatsapp(message, booking)
    send_sms(message, booking)


def send_refund_confirmation(booking):
    subject = "GoExplorer - Refund Initiated 💸"

    message = f"""
Refund Initiated

Booking ID: {booking.id}
Amount will be credited in 5–7 working days.
"""

    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [get_user_email(booking)],
        fail_silently=True,
    )

    print("📧 Refund confirmation email sent")
    send_whatsapp(message, booking)
    send_sms(message, booking)


# -----------------------------------------------------
# SAFE STUBS (NO HARD DEPENDENCY)
# -----------------------------------------------------
def send_whatsapp(message, booking):
    try:
        print(f"📱 WhatsApp queued → {get_user_phone(booking)}")
    except Exception as e:
        print("⚠️ WhatsApp failed:", e)


def send_sms(message, booking):
    try:
        print(f"📩 SMS queued → {get_user_phone(booking)}")
    except Exception as e:
        print("⚠️ SMS failed:", e)
