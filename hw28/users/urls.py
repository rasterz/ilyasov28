from django.urls import path

from users import views

urlpatterns = [
    path('loc/', views.LocationListView.as_view()),
    path('loc/<int:pk>', views.LocationDetailView.as_view()),
    path('loc/create/', views.LocationCreateView.as_view()),
    path('loc/<int:pk>/update/', views.LocationUpdateView.as_view()),
    path('loc/<int:pk>/delete/', views.LocationDeleteView.as_view()),
    path('', views.UserListView.as_view()),
    path('<int:pk>/', views.UserDetailView.as_view()),
    path('create/', views.UserCreateView.as_view()),
    path('<int:pk>/update/', views.UserUpdateView.as_view()),
    path('<int:pk>/delete/', views.UserDeleteView.as_view()),
]
