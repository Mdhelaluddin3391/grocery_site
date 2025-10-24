from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='home'),
    path('search/', views.search_results, name='search_results'),
    path('category/<slug:slug>/', views.category_detail, name='category_detail'),
    path('product/<slug:slug>/', views.product_detail, name='product_detail'),
    path('ajax/load-more-categories/', views.load_more_categories, name='load_more_categories'),
    path('ajax/get-delivery-info/', views.get_delivery_info, name='get_delivery_info'),
]