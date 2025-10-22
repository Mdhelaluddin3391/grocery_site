from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='home'),
    path('category/<slug:slug>/', views.category_detail, name='category_detail'),
    path('product/<slug:slug>/', views.product_detail, name='product_detail'),
    path('ajax/load-more-categories/', views.load_more_categories, name='load_more_categories'),

]