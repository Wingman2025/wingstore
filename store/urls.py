from django.urls import path
from . import views

urlpatterns = [
    path('', views.product_list, name='product_list'),
    path('producto/<int:pk>/', views.product_detail, name='product_detail'),
    path('chat/', views.chat, name='chat'),
    path('chat_api/', views.chat_api, name='chat_api'),
]
