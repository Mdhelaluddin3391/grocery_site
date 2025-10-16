from django.shortcuts import render

# Create your views here.
from django.shortcuts import render

def home_view(request):
    """
    Renders the store homepage (index.html).
    """
    # Template path: 'store/index.html'
    return render(request, 'store/index.html', {})