from django.shortcuts import render, get_object_or_404, redirect
from .models import Product, Order, CustomerMessage, Review , OrderImage
from django.urls import reverse
from django.db import models
from django.core.mail import EmailMessage
from django.conf import settings
from django.core.mail import send_mail
from django.contrib import messages
from .models import Cart
from django.core.mail import EmailMultiAlternatives

# Create your views here.

def home(request):
    products = Product.objects.all()
    return render(request, 'myapp/home.html', {'products': products})

def about(request):
    return render(request, 'myapp/about.html')

def product_list(request):
    products = Product.objects.all()
    return render(request, 'myapp/product_list.html', {'products': products})

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Product, Order, OrderImage

def bulk_order(request, pk=None):
    if request.method == 'POST':
        print('POST DATA:', request.POST)  # Debug print
        # Get product
        product_id = request.POST.get('product_id') or pk
        product = get_object_or_404(Product, id=product_id)

        # Extract form data safely
        customer_name = request.POST.get('customer_name')
        email_address = request.POST.get('email')
        phone = request.POST.get('phone')
        size = request.POST.get('size')
        color = request.POST.get('color')
        quantity = int(request.POST.get('quantity', 1))
        message = request.POST.get('message', '')
        images = request.FILES.getlist('images')

        # Check for required fields
        if not all([customer_name, email_address, phone, size, color, quantity]):
            messages.error(request, 'Please fill in all required fields.')
            return render(request, 'myapp/bulk_order.html', {'product': product, 'size': size, 'color': color, 'quantity': quantity})

        # Save order (store size_color in size, leave color blank)
        order = Order.objects.create(
            customer_name=customer_name,
            email=email_address,
            phone=phone,
            product=product,
            size=size,
            color=color,
            quantity=quantity,
            message=message
        )
        print('ORDER SIZE:', order.size, 'ORDER COLOR:', order.color, 'ORDER QUANTITY:', order.quantity)  # Debug print
        for img in images:
            OrderImage.objects.create(order=order, image=img)
        messages.success(request, "✅ Your order has been submitted successfully!")
        return redirect('thank_you')

    # GET request
    product = get_object_or_404(Product, pk=pk) if pk else None
    products = Product.objects.all()
    size = request.GET.get('size')
    color = request.GET.get('color')
    quantity = request.GET.get('quantity', 1)
    return render(request, 'myapp/bulk_order.html', {
        'product': product,
        'products': products,
        'size': size,
        'color': color,
        'quantity': quantity,
    })


def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)
    reviews = product.reviews.all().order_by('-created_at')
    avg_rating = reviews.aggregate(models.Avg('rating'))['rating__avg']
    if request.method == 'POST':
        name = request.POST['name']
        rating = int(request.POST['rating'])
        comment = request.POST.get('comment', '')
        Review.objects.create(product=product, name=name, rating=rating, comment=comment)
        return redirect('product_detail', pk=pk)
    return render(request, 'myapp/product_detail.html', {
        'product': product,
        'reviews': reviews,
        'avg_rating': avg_rating,
    })




def customer_service(request):
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        email = request.POST.get('email', '').strip()
        phone = request.POST.get('phone', '').strip()
        message = request.POST.get('message', '').strip()

        if not name or not email or not phone or not message:
            return render(request, 'myapp/customer_service.html', {
                'error': 'All fields are required.',
                'name': name,
                'email': email,
                'phone': phone,
                'message': message,
            })

        CustomerMessage.objects.create(
            name=name,
            email=email,
            phone=phone,
            message=message,
        )
        return redirect('thank_you')

    return render(request, 'myapp/customer_service.html')


def thank_you(request):
    return render(request, 'myapp/thank_you.html')


def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    size = request.POST.get('size')
    color = request.POST.get('color')
    quantity = int(request.POST.get('quantity', 1))
    if request.user.is_authenticated:
        cart_item, created = Cart.objects.get_or_create(user=request.user, product=product, size=size,
            color=color, defaults={'quantity': quantity})
    else:
        session_key = request.session.session_key
        if not session_key:
            request.session.create()
            session_key = request.session.session_key
        cart_item, created = Cart.objects.get_or_create(session_key=session_key, product=product, size=size,
            color=color, defaults={'quantity': quantity})
    if not created:
        cart_item.quantity += quantity
    else:
        cart_item.quantity = quantity
    # Save size and color if fields exist
    if hasattr(cart_item, 'size'):
        cart_item.size = size
    if hasattr(cart_item, 'color'):
        cart_item.color = color
    cart_item.save()

    messages.success(request, f"{product.name} added to cart.")
    return redirect("cart")   # redirects to cart page


def cart_view(request):
    if request.user.is_authenticated:
        cart_items = Cart.objects.filter(user=request.user)
    else:
        session_key = request.session.session_key
        cart_items = Cart.objects.filter(session_key=session_key)

    total = sum(item.total_price() for item in cart_items)

    return render(request, "myapp/cart.html", {"cart_items": cart_items, "total": total})


def remove_from_cart(request, cart_id):
    cart_item = get_object_or_404(Cart, id=cart_id)
    cart_item.delete()
    messages.success(request, "Item removed from cart.")
    return redirect("cart")


def checkout(request):

    if not request.session.session_key:
        request.session.create()

    if request.user.is_authenticated:
        cart_items = Cart.objects.filter(user=request.user)
    else:
        cart_items = Cart.objects.filter(session_key=request.session.session_key)

    if not cart_items.exists():
        messages.error(request, "Your cart is empty!")
        return redirect("cart")

    if request.method == "POST":
        customer_name = request.POST["customer_name"]
        email = request.POST["email"]
        phone = request.POST["phone"]
        message_text = request.POST.get("message", "Checkout order")

        # ✅ Save order
        for item in cart_items:
            Order.objects.create(
                customer_name=customer_name,
                email=email,
                phone=phone,
                product=item.product,  # product stays intact
                quantity=item.quantity,
                size=getattr(item, 'size', ''),
                color=getattr(item, 'color', ''),
                message=message_text
            )

        # ✅ Build email content
        order_summary = "\n".join(
            [f"{item.product.name} (Size: {getattr(item, 'size', 'N/A')}, Color: {getattr(item, 'color', 'N/A')}) x {item.quantity} = Rs {item.total_price()}" for item in cart_items]
        )
        subject = "🛒 New Order Received"
        message = f"""
New Order Received:

Name: {customer_name}
Email: {email}
Phone: {phone}
Message: {message_text}

Order Summary:
{order_summary}

# 
Total = Rs {sum(item.total_price() for item in cart_items)}
# """

        # ✅ Send email to Gmail
        # send_mail(
        #     subject,
        #     message,
        #     settings.DEFAULT_FROM_EMAIL,   # from email
        #     ["Abdullahumarch000@gmail.com"],       # your Gmail (receiver)
        #     fail_silently=False,
        # )

         # ✅ Clear cart only
        cart_items.delete()
        messages.success(request, "Order placed successfully! Check your email for confirmation.")
        return redirect("thank_you")

    total = sum(item.total_price() for item in cart_items)
    return render(request, "myapp/checkout.html", {"cart_items": cart_items, "total": total})
