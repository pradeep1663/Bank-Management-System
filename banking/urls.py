from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('signup/', views.signup, name='signup'),
    path('login/', views.login, name='login'),
    path('logout/', views.logout, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    
    # Customer
    path('withdraw/', views.withdraw, name='withdraw'),
    path('deposit/', views.deposit, name='deposit'),
    path('balance/', views.balance, name='balance'),
    path('request/', views.submit_request, name='request'),
    path('view_responses/', views.view_responses, name='view_responses'),
    
    # Admin
    path('users/', views.all_users, name='all_users'),
    path('delete/<int:user_id>/', views.delete_user, name='delete_user'),
    path('requests/', views.view_requests, name='view_requests'),
    path('response/<int:req_id>/', views.respond_request, name='respond_request'),
    path('approve/<int:req_id>/', views.approve_request, name='approve_request'),
    path('reject/<int:req_id>/', views.reject_request, name='reject_request'),
    path('search_user/',views.search_user,name='search_user'),
]
