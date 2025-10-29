# store/views.py

from django.shortcuts import render, get_object_or_404
from .models import Category, Product
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.template.loader import render_to_string
from django.db.models import Q
from django.conf import settings
from math import radians, sin, cos, sqrt, atan2

def get_main_categories():
    """Helper function to get main categories for the header."""
    return Category.objects.filter(parent=None)

def index(request):
    all_categories = Category.objects.filter(show_on_homepage=True, parent=None).prefetch_related('products')
    paginator = Paginator(all_categories, 4) 
    page_number = request.GET.get('page')
    categories_page = paginator.get_page(page_number)
    
    for category in categories_page:
        category.limited_products = category.products.filter(stock__gt=0)[:10]

    specials = Product.objects.filter(is_special=True, stock__gt=0)

    return render(request, 'store/index.html', {
        'categories': categories_page,
        'specials': specials,
        'main_categories': get_main_categories(),
        'has_more_pages': categories_page.has_next(),
    })

def load_more_categories(request):
    all_categories = Category.objects.filter(show_on_homepage=True, parent=None).prefetch_related('products')
    paginator = Paginator(all_categories, 4)
    page_number = int(request.GET.get('page', 1))
    
    if page_number > paginator.num_pages:
        return JsonResponse({'html': '', 'has_more': False})

    categories_page = paginator.get_page(page_number)
    
    for category in categories_page:
        category.limited_products = category.products.all()[:10]
        
    html = render_to_string(
        'store/partials/_category_section.html', 
        {'categories': categories_page}
    )
    
    return JsonResponse({'html': html, 'has_more': categories_page.has_next()})

def category_detail(request, slug):
    category = get_object_or_404(Category, slug=slug)

    if category.parent is None:
        child_categories = category.subcategories.all()
        categories_to_fetch = [category] + list(child_categories)
        products = Product.objects.filter(category__in=categories_to_fetch)
        subcategories = child_categories
    else:
        products = Product.objects.filter(category=category)
        subcategories = category.parent.subcategories.all()

    context = {
        'category': category,
        'products': products,
        'subcategories': subcategories,
        'main_categories': get_main_categories(),
    }
    return render(request, 'store/category_detail.html', context)

def product_detail(request, slug):
    product = get_object_or_404(Product, slug=slug)
    related_products = Product.objects.filter(category=product.category).exclude(id=product.id)[:10]

    context = {
        'product': product,
        'related_products': related_products,
        'main_categories': get_main_categories(),
    }
    return render(request, 'store/product_detail.html', context)

def search_results(request):
    query = request.GET.get('q')
    products = Product.objects.none()

    if query:
        products = Product.objects.filter(
            Q(name__icontains=query) | Q(description__icontains=query)
        )

    context = {
        'query': query,
        'products': products,
        'main_categories': get_main_categories(),
    }
    return render(request, 'store/search_results.html', context)

def calculate_distance(lat1, lon1, lat2, lon2):
    """Haversine formula se do points ke beech distance (km mein) calculate karein."""
    R = 6371
    dLat = radians(lat2 - lat1)
    dLon = radians(lon2 - lon1)
    lat1 = radians(lat1)
    lat2 = radians(lat2)
    a = sin(dLat / 2)**2 + cos(lat1) * cos(lat2) * sin(dLon / 2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    return R * c

def get_delivery_info(request):
    """User ki location ke basis par delivery time return karein."""
    try:
        user_lat = float(request.GET.get('lat'))
        user_lng = float(request.GET.get('lng'))
    except (TypeError, ValueError):
        return JsonResponse({'error': 'Invalid coordinates'}, status=400)

    store_coords = settings.STORE_COORDINATES
    store_lat = store_coords['lat']
    store_lng = store_coords['lng']
    
    distance = calculate_distance(user_lat, user_lng, store_lat, store_lng)
    
    if distance <= 2:
        delivery_time = "10 minutes"
    elif 2 < distance <= 3:
        delivery_time = "15 minutes"
    elif 3 < distance <= 5:
        delivery_time = "20 minutes"
    else:
        delivery_time = "30+ minutes"
        
    message = f"Delivery in {delivery_time} • {settings.STORE_LOCATION_NAME}"
    return JsonResponse({'delivery_message': message})

def get_product_by_barcode(request, barcode):
    """
    Barcode ke aadhar par product details JSON format mein return karein.
    """
    try:
        product = Product.objects.get(barcode=barcode)
        data = {
            'status': 'success',
            'product': {
                'id': product.id,
                'name': product.name,
                'price': str(product.price),
                'image': product.image or 'https://via.placeholder.com/150',
                'stock': product.stock,
            }
        }
    except Product.DoesNotExist:
        data = {'status': 'error', 'message': 'Product not found'}
    
    return JsonResponse(data)