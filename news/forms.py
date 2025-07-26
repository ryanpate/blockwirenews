from django import forms
from django.utils.text import slugify
from .models import Article, Category
from ckeditor_uploader.widgets import CKEditorUploadingWidget

class ArticleForm(forms.ModelForm):
    content = forms.CharField(widget=CKEditorUploadingWidget())
    
    class Meta:
        model = Article
        fields = ['title', 'excerpt', 'content', 'featured_image', 'category', 'tags']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter article title'}),
            'excerpt': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Brief description of your article'}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'tags': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'bitcoin, ethereum, defi (comma separated)'}),
        }
        labels = {
            'excerpt': 'Article Summary',
            'featured_image': 'Featured Image (optional)',
        }

    def save(self, commit=True):
        article = super().save(commit=False)
        article.slug = slugify(article.title)
        article.article_type = 'original'
        article.is_published = True
        
        if commit:
            article.save()
            self.save_m2m()  # Save tags
        
        return article