from django.db import models


class Cryptocurrency(models.Model):
    symbol = models.CharField(max_length=10, unique=True)
    name = models.CharField(max_length=100)
    current_price = models.DecimalField(max_digits=20, decimal_places=8)
    market_cap = models.BigIntegerField()
    volume_24h = models.BigIntegerField()
    percent_change_24h = models.DecimalField(max_digits=10, decimal_places=2)
    last_updated = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Cryptocurrencies"

    def __str__(self):
        return f"{self.name} ({self.symbol})"


class PriceHistory(models.Model):
    cryptocurrency = models.ForeignKey(
        Cryptocurrency, on_delete=models.CASCADE, related_name='price_history')
    price = models.DecimalField(max_digits=20, decimal_places=8)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']
