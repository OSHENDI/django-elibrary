from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),

    # books
    path('books/', views.book_list, name='book_list'),
    path('book/<int:id>/', views.book_detail, name='book_detail'),

    # categories
    path('categories/', views.category_list, name='category_list'),
    path('categories/<int:id>/', views.category_books, name='category_books'),

    # authors
    path('authors/', views.author_list, name='author_list'),
    path('authors/<int:id>/', views.author_detail, name='author_detail'),

    # contact
    path('contact/', views.contact_us, name='contact'),

    # auth
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    # profile
    path('profile/', views.profile_view, name='profile'),
    path('profile/edit/', views.edit_profile, name='edit_profile'),

    # borrowing
    path('borrow/<int:book_id>/', views.borrow_book, name='borrow_book'),
    path('return/<int:record_id>/', views.return_book, name='return_book'),
    path('my-books/', views.my_books, name='my_books'),

    # reviews
    path('book/<int:id>/review/', views.add_review, name='add_review'),
]
