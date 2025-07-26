from django.urls import path
from . import views

urlpatterns = [
    path('crypto-prices/', views.CryptoPricesAPIView.as_view(), name='crypto_prices'),
    path('price-history/<str:symbol>/', views.PriceHistoryAPIView.as_view(), name='price_history'),
]