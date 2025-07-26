from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.urls import reverse
from taggit.managers import TaggableManager
from ckeditor_uploader.fields import RichTextUploadingField

class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)

    class Meta:
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.name

class Source(models.Model):
    name = models.CharField(max_length=100)
    url = models.URLField()
    logo = models.ImageField(upload_to='source_logos/', blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name

class Article(models.Model):
    ARTICLE_TYPES = (
        ('aggregated', 'Aggregated'),
        ('original', 'Original'),
    )
    
    title = models.CharField(max_length=300)
    slug = models.SlugField(max_length=300, unique=True)
    author = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    content = RichTextUploadingField()
    excerpt = models.TextField(max_length=500)
    featured_image = models.ImageField(upload_to='articles/', blank=True)
    
    article_type = models.CharField(max_length=20, choices=ARTICLE_TYPES, default='aggregated')
    source = models.ForeignKey(Source, on_delete=models.SET_NULL, null=True, blank=True)
    source_url = models.URLField(blank=True)
    
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True)
    tags = TaggableManager()
    
    published_date = models.DateTimeField(default=timezone.now)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    is_published = models.BooleanField(default=True)
    views = models.IntegerField(default=0)
    
    class Meta:
        ordering = ['-published_date']
        
    def __str__(self):
        return self.title
    
    def get_absolute_url(self):
        return reverse('news:article_detail', kwargs={'slug': self.slug})
    
    def increase_views(self):
        self.views += 1
        self.save(update_fields=['views'])