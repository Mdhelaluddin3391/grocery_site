# store/views.py

from django.shortcuts import render, get_object_or_404
from .models import Category, Product
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.template.loader import render_to_string
from django.db.models import Q

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
        category.limited_products = category.products.all()[:10]

    specials = Product.objects.filter(is_special=True)

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


# Baaki ke views waise hi rahenge
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