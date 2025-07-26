from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator
from django.db.models import Q
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.messages.views import SuccessMessageMixin  # Add this import
from django.urls import reverse_lazy
from django.utils.text import slugify
from .models import Article, Category
from .forms import ArticleForm
from ticker.models import Cryptocurrency


class HomeView(ListView):
    model = Article
    template_name = 'news/home.html'
    context_object_name = 'articles'
    paginate_by = 10

    def get_queryset(self):
        return Article.objects.filter(is_published=True).order_by('-published_date')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Get featured articles (most recent 3)
        context['featured_articles'] = Article.objects.filter(
            is_published=True
        ).order_by('-published_date')[:3]
        # Get cryptocurrencies for the ticker
        context['cryptocurrencies'] = Cryptocurrency.objects.all().order_by(
            '-market_cap')[:8]
        # Get all categories for navigation
        context['categories'] = Category.objects.all()
        return context


class ArticleDetailView(DetailView):
    model = Article
    template_name = 'news/article_detail.html'
    context_object_name = 'article'

    def get_object(self):
        article = super().get_object()
        article.increase_views()
        return article

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Get related articles from the same category
        context['related_articles'] = Article.objects.filter(
            category=self.object.category,
            is_published=True
        ).exclude(id=self.object.id)[:5]
        # Get categories for navigation
        context['categories'] = Category.objects.all()
        return context


class CategoryView(ListView):
    model = Article
    template_name = 'news/category.html'
    context_object_name = 'articles'
    paginate_by = 15

    def get_queryset(self):
        self.category = get_object_or_404(Category, slug=self.kwargs['slug'])
        return Article.objects.filter(category=self.category, is_published=True).order_by('-published_date')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category'] = self.category
        context['categories'] = Category.objects.all()
        return context


class SearchView(ListView):
    model = Article
    template_name = 'news/search.html'
    context_object_name = 'articles'
    paginate_by = 15

    def get_queryset(self):
        query = self.request.GET.get('q')
        if query:
            return Article.objects.filter(
                Q(title__icontains=query) | Q(content__icontains=query),
                is_published=True
            ).order_by('-published_date')
        return Article.objects.none()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['query'] = self.request.GET.get('q', '')
        context['categories'] = Category.objects.all()
        return context


class CreateArticleView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = Article
    form_class = ArticleForm
    template_name = 'news/create_article.html'
    success_message = "Article created successfully!"
    login_url = '/admin/login/'

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('news:article_detail', kwargs={'slug': self.object.slug})


class UpdateArticleView(LoginRequiredMixin, UserPassesTestMixin, SuccessMessageMixin, UpdateView):
    model = Article
    form_class = ArticleForm
    template_name = 'news/update_article.html'
    success_message = "Article updated successfully!"

    def test_func(self):
        article = self.get_object()
        return self.request.user == article.author or self.request.user.is_superuser

    def get_success_url(self):
        return reverse_lazy('news:article_detail', kwargs={'slug': self.object.slug})


class DeleteArticleView(LoginRequiredMixin, UserPassesTestMixin, SuccessMessageMixin, DeleteView):
    model = Article
    template_name = 'news/delete_article.html'
    success_url = reverse_lazy('news:home')
    success_message = "Article deleted successfully!"

    def test_func(self):
        article = self.get_object()
        return self.request.user == article.author or self.request.user.is_superuser


class MyArticlesView(LoginRequiredMixin, ListView):
    model = Article
    template_name = 'news/my_articles.html'
    context_object_name = 'articles'
    paginate_by = 10

    def get_queryset(self):
        return Article.objects.filter(author=self.request.user).order_by('-created_at')
