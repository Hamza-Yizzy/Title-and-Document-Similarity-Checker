from django.urls import path
from . import views
from .views import ImportUsersView

urlpatterns = [
    path('', views.login_view, name='login'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('logout/', views.logout_view, name='logout'),
    path('compare/', views.compare_uploaded_books, name='compare_uploaded_books'),
    path('handle_uploaded_file/', views.handle_uploaded_file, name='handle_uploaded_file'),
    path('books/', views.books_list, name='books_list'),
    path('book/view-file/<int:book_id>/', views.view_book_file, name='view_book_file'),
    path('book/add/', views.add_or_edit_book, name='add_book'),
    path('book/edit/<int:book_id>/', views.add_or_edit_book, name='edit_book'),
    path('book/delete/<int:book_id>/', views.delete_book, name='delete_book'),
    path('index/', views.index, name='index'),
    path('check-title/', views.check_title, name='check_title'),
    path('admin-dashboard/', views.dashboard, name='admin_dashboard'),
    path('register-user/', views.register_user, name='register_user'),
    path('users/', views.users_list, name='users_list'),
    path('users/edit/<int:user_id>/', views.edit_user, name='edit_user'),
    path('users/delete/<int:user_id>/', views.delete_user, name='delete_user'),
    path('api/import/preview/', views.preview_user_import, name='preview_user_import'),
    path('api/import/upload/', views.upload_user_import, name='upload_user_import'),
    path('api/import-users/', ImportUsersView.as_view(), name='import_users_api'),
]