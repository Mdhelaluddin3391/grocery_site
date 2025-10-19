# store/context_processors.py

from .models import Category

def footer_categories(request):
    """
    Makes all categories available to every template for the footer.
    """
    # Yahan hum sabhi categories ko fetch kar rahe hain
    all_categories = Category.objects.all() 
    
    # Ek dictionary return karein
    return {
        'footer_all_categories': all_categories
    }