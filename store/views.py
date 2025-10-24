# store/views.py

from django.shortcuts import render, get_object_or_404
from .models import Category, Product
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.template.loader import render_to_string
from django.db.models import Q
from django.http import JsonResponse
from django.conf import settings
from math import radians, sin, cos, sqrt, atan2

def get_main_categories():
    """Helper function to get main categories for the header."""
    # Yeh "Shop by Category" ke liye hai, yeh poora load hoga
    return Category.objects.filter(parent=None)

def index(request):
    # Yeh neeche waale PRODUCT SECTIONS ke liye hai, is par lazy loading lagegi
    all_categories = Category.objects.filter(show_on_homepage=True, parent=None).prefetch_related('products')
    
    paginator = Paginator(all_categories, 4) 
    page_number = request.GET.get('page')
    categories_page = paginator.get_page(page_number)
    
    for category in categories_page:
        category.limited_products = category.products.filter(stock__gt=0)[:10]

    specials = Product.objects.filter(is_special=True, stock__gt=0)

    return render(request, 'store/index.html', {
        'categories': categories_page, # Yeh lazy loaded hain
        'specials': specials,
        'main_categories': get_main_categories(), # Yeh poore load honge
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

    # Agar yeh ek main category hai (jiska koi parent nahi hai)
    if category.parent is None:
        # Iske sabhi sub-categories ko lein
        child_categories = category.subcategories.all()
        # Main category aur uske sabhi sub-categories ko ek list mein daalein
        categories_to_fetch = [category] + list(child_categories)
        # Un sabhi categories ke products ko fetch karein
        products = Product.objects.filter(category__in=categories_to_fetch)
        # Sidebar ke liye, iske sub-categories ko set karein
        subcategories = child_categories
    # Agar yeh ek sub-category hai
    else:
        # Sirf isi sub-category ke products ko lein
        products = Product.objects.filter(category=category)
        # Sidebar ke liye, iske parent ke sabhi sub-categories (siblings) ko set karein
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
    products = Product.objects.none() # Shuruaat mein koi product nahi

    if query:
        # Hum product ke naam aur description dono mein search karenge
        # 'icontains' case-insensitive search karta hai (e.g., 'Milk' aur 'milk' dono milenge)
        products = Product.objects.filter(
            Q(name__icontains=query) | Q(description__icontains=query)
        )

    context = {
        'query': query,
        'products': products,
        'main_categories': get_main_categories(), # Header ke liye
    }
    return render(request, 'store/search_results.html', context)


def calculate_distance(lat1, lon1, lat2, lon2):
    """Haversine formula se do points ke beech distance (km mein) calculate karein."""
    R = 6371  # Earth ka radius in km

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
    
    delivery_time = ""
    if distance <= 2:
        delivery_time = "10 minutes"
    elif 2 < distance <= 3:
        delivery_time = "15 minutes"
    elif 3 < distance <= 5:
        delivery_time = "20 minutes"
    else:
        # Agar 5km se zyada door hai
        delivery_time = "30+ minutes"
        
    message = f"Delivery in {delivery_time} • {settings.STORE_LOCATION_NAME}"
    
    return JsonResponse({'delivery_message': message})