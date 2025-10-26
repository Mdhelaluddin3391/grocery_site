# store/context_processors.py

from .models import Category

def get_main_categories():
    """Helper function to get main categories for the header."""
    return Category.objects.filter(parent=None)

def main_categories_processor(request):
    """
    Header mein dikhane ke liye main categories.
    """
    return {'main_categories': get_main_categories()}

def footer_categories(request):
    """
    Makes all categories available to every template for the footer.
    """
    all_categories = Category.objects.all() 
    return {
        'footer_all_categories': all_categories
    }