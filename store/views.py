# store/views.py

from django.shortcuts import render, get_object_or_404
from .models import Category, Product

def get_main_categories():
    """Helper function to get main categories for the header."""
    return Category.objects.filter(parent=None)

def index(request):
    # 'prefetch_related' se performance behtar hoti hai
    categories = Category.objects.filter(show_on_homepage=True, parent=None).prefetch_related('products')
    specials = Product.objects.filter(is_special=True)

    # Har category ke products ko view mein hi limit kar dein
    for category in categories:
        # Har category object ke saath ek naya attribute 'limited_products' jod do
        # Jismein sirf pehle 10 products honge
        category.limited_products = category.products.all()[:10]

    return render(request, 'store/index.html', {
        'categories': categories,
        'specials': specials,
        'main_categories': get_main_categories(), # Header ke liye
    })


def category_detail(request, slug):
    category = get_object_or_404(Category, slug=slug)

    if category.parent is None:
        child_categories = category.subcategories.all()
        products = Product.objects.filter(category__in=child_categories)
    else:
        products = Product.objects.filter(category=category)

    if category.parent is None:
        subcategories = category.subcategories.all()
    else:
        subcategories = category.parent.subcategories.all()

    context = {
        'category': category,
        'products': products,
        'subcategories': subcategories,
        'main_categories': get_main_categories(), # Header ke liye
    }
    return render(request, 'store/category_detail.html', context)


def product_detail(request, slug):
    product = get_object_or_404(Product, slug=slug)
    related_products = Product.objects.filter(category=product.category).exclude(id=product.id)[:10]

    context = {
        'product': product,
        'related_products': related_products,
        'main_categories': get_main_categories(), # Header ke liye
    }
    return render(request, 'store/product_detail.html', context)