from django.http import JsonResponse
from django.shortcuts import get_object_or_404  # Add this import
from django.views.generic import View
from .models import Cryptocurrency, PriceHistory
import json


class CryptoPricesAPIView(View):
    def get(self, request):
        cryptos = Cryptocurrency.objects.all()
        data = []

        for crypto in cryptos:
            data.append({
                'symbol': crypto.symbol,
                'name': crypto.name,
                'price': float(crypto.current_price),
                'market_cap': crypto.market_cap,
                'volume_24h': crypto.volume_24h,
                'change_24h': float(crypto.percent_change_24h)
            })

        return JsonResponse({'cryptocurrencies': data})


class PriceHistoryAPIView(View):
    def get(self, request, symbol):
        crypto = get_object_or_404(Cryptocurrency, symbol=symbol.upper())
        history = crypto.price_history.all()[:100]  # Last 100 data points

        data = {
            'symbol': crypto.symbol,
            'name': crypto.name,
            'history': [
                {
                    'price': float(h.price),
                    'timestamp': h.timestamp.isoformat()
                }
                for h in history
            ]
        }

        return JsonResponse(data)
