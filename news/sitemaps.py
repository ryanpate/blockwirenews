from django.contrib.sitemaps import Sitemap
from .models import Article

class ArticleSitemap(Sitemap):
    changefreq = "daily"
    priority = 0.9

    def items(self):
        return Article.objects.filter(is_published=True)

    def lastmod(self, obj):
        return obj.updated_at