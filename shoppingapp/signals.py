from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import EmailMessage, EmailMultiAlternatives, send_mail
from django.conf import settings
from .models import Order, CustomerMessage
import pytz


@receiver(post_save, sender=Order)
def send_order_notification(sender, instance, created, **kwargs):
    if created:
        # Convert to Pakistan timezone
        pakistan_tz = pytz.timezone('Asia/Karachi')
        created_at_pkr = instance.created_at.astimezone(pakistan_tz).strftime('%Y-%m-%d %I:%M %p')

        # -----------------
        # 📧 Admin Email
        # -----------------
        subject_admin = f"📦 New Bulk Order from {instance.customer_name}"
        text_admin = (
            f"New order received:\n\n"
            f"Customer: {instance.customer_name}\n"
            f"Email: {instance.email}\n"
            f"Phone: {instance.phone}\n"
            f"Product: {instance.product.name}\n"
            f"Size: {instance.size}\n"
            f"Color: {instance.color}\n"
            f"Quantity: {instance.quantity}\n"
            f"Message: {instance.message}\n"
            f"Status: {instance.status}\n"
            f"Created at: {created_at_pkr}\n"
        )

        html_admin = f"""
        <!DOCTYPE html>
        <html>
        <body style="font-family:Segoe UI,Arial,sans-serif;background:#f7f9fc;padding:20px;">
          <div style="max-width:700px;margin:auto;background:#fff;border-radius:10px;overflow:hidden;
                      box-shadow:0 4px 15px rgba(0,0,0,0.1);">
            <div style="background:#0d6efd;color:#fff;padding:15px;text-align:center;">
              <h2>📦 New Bulk Order</h2>
            </div>
            <div style="padding:20px;">
              <h3>🛍️ Product Details</h3>
              <p><strong>Product:</strong> {instance.product.name}</p>
              <p><strong>Size:</strong> {instance.size or "N/A"}</p>
              <p><strong>Color:</strong> {instance.color or "N/A"}</p>
              <p><strong>Quantity:</strong> {instance.quantity}</p>

              <hr>
              <h3>👤 Customer Details</h3>
              <p><strong>Name:</strong> {instance.customer_name}</p>
              <p><strong>Email:</strong> {instance.email}</p>
              <p><strong>Phone:</strong> {instance.phone}</p>
              <p><strong>Message:</strong> {instance.message or "N/A"}</p>
              <p><strong>Status:</strong> {instance.status}</p>
              <p><strong>Created At:</strong> {created_at_pkr}</p>
            </div>
          </div>
        </body>
        </html>
        """

        email_admin = EmailMultiAlternatives(
            subject_admin, text_admin, settings.DEFAULT_FROM_EMAIL, ["abdullahumarch000@gmail.com"]
        )
        email_admin.attach_alternative(html_admin, "text/html")

        # Attach uploaded images
        try:
            for img in instance.images.all():
                if img.image and hasattr(img.image, 'path'):
                    email_admin.attach_file(img.image.path)
        except Exception as e:
            print("Error attaching image:", e)

        email_admin.send()

        # -----------------
        # 📧 Customer Email
        # -----------------
        subject_customer = "✅ We Received Your Order"
        text_customer = (
            f"Dear {instance.customer_name},\n\n"
            f"Thank you for placing an order with us.\n"
            f"Product: {instance.product.name}\n"
            f"Size: {instance.size}\n"
            f"Color: {instance.color}\n"
            f"Quantity: {instance.quantity}\n"
            f"Message: {instance.message}\n"
            f"Placed at: {created_at_pkr}\n\n"
            f"We will contact you shortly.\n\n"
            f"Best regards,\nYour Team"
        )

        html_customer = f"""
        <!DOCTYPE html>
        <html>
        <body style="font-family:Segoe UI,Arial,sans-serif;background:#f7f9fc;padding:20px;">
          <div style="max-width:650px;margin:auto;background:#fff;border-radius:10px;overflow:hidden;
                      box-shadow:0 4px 15px rgba(0,0,0,0.1);">
            <div style="background:#0d6efd;color:#fff;padding:20px;text-align:center;">
              <h2>✅ Order Confirmation</h2>
            </div>
            <div style="padding:25px;">
              <p>Hello <strong>{instance.customer_name}</strong>,</p>
              <p>Thank you for your <strong>bulk order</strong>. Our team will contact you shortly.</p>

              <div style="background:#f1f3f5;padding:15px;border-radius:8px;margin-top:10px;">
                <h3>📦 Order Summary</h3>
                <p><strong>Product:</strong> {instance.product.name}</p>
                <p><strong>Size:</strong> {instance.size or "N/A"}</p>
                <p><strong>Color:</strong> {instance.color or "N/A"}</p>
                <p><strong>Quantity:</strong> {instance.quantity}</p>
                <p><strong>Message:</strong> {instance.message or "N/A"}</p>
                <p><strong>Placed At:</strong> {created_at_pkr}</p>
              </div>

              <p style="margin-top:20px;">💙 Thank you for shopping with us!</p>
              <a href="https://yourwebsite.com"
                 style="display:inline-block;margin-top:10px;padding:12px 20px;background:#0d6efd;
                        color:#fff;text-decoration:none;border-radius:6px;font-weight:bold;">
                 Visit Our Store
              </a>
            </div>
            <div style="text-align:center;padding:12px;background:#fafafa;color:#777;font-size:13px;">
              © {2025} Rangrez Studio. All rights reserved.<br>
              Need help? Contact us at <a href="mailto:yourcompany@gmail.com">yourcompany@gmail.com</a>
            </div>
          </div>
        </body>
        </html>
        """

        email_customer = EmailMultiAlternatives(
            subject_customer, text_customer, settings.DEFAULT_FROM_EMAIL, [instance.email]
        )
        email_customer.attach_alternative(html_customer, "text/html")
        email_customer.send()


@receiver(post_save, sender=CustomerMessage)
def send_customer_message_notification(sender, instance, created, **kwargs):
    if created:
        pakistan_tz = pytz.timezone('Asia/Karachi')
        created_at_pkr = instance.created_at.astimezone(pakistan_tz).strftime('%Y-%m-%d %I:%M %p')

        subject = f'📩 New Customer Message from {instance.name}'
        message = (
            f"You have received a new customer service message.\n\n"
            f"Name: {instance.name}\n"
            f"Email: {instance.email}\n"
            f"Phone: {instance.phone}\n"
            f"Message: {instance.message}\n"
            f"Status: {instance.status}\n"
            f"Created at: {created_at_pkr}\n"
        )

        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=['abdullahumarch000@gmail.com'],
            fail_silently=False,
        )
