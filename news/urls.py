from django.urls import path
from . import views

app_name = 'news'

urlpatterns = [
    path('', views.HomeView.as_view(), name='home'),
    path('article/<slug:slug>/', views.ArticleDetailView.as_view(), name='article_detail'),
    path('category/<slug:slug>/', views.CategoryView.as_view(), name='category'),
    path('search/', views.SearchView.as_view(), name='search'),
    path('write/', views.CreateArticleView.as_view(), name='create_article'),
        path('article/<slug:slug>/edit/',
         views.UpdateArticleView.as_view(), name='update_article'),
    path('article/<slug:slug>/delete/',
         views.DeleteArticleView.as_view(), name='delete_article'),
    path('my-articles/', views.MyArticlesView.as_view(), name='my_articles'),
]