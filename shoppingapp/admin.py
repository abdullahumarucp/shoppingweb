from django.contrib import admin
from .models import Product, Order, CustomerMessage, ProductImage, Review
from .models import OrderImage

class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1

class ProductAdmin(admin.ModelAdmin):
    inlines = [ProductImageInline]

admin.site.register(Product, ProductAdmin)
admin.site.register(Order)
admin.site.register(CustomerMessage)
admin.site.register(ProductImage)

class ReviewAdmin(admin.ModelAdmin):
    list_display = ('product', 'name', 'rating', 'created_at')
    search_fields = ('product__name', 'name', 'comment')
    list_filter = ('rating', 'created_at')

admin.site.register(Review, ReviewAdmin)
admin.site.register(OrderImage)