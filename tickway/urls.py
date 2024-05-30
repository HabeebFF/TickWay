"""
URL configuration for tickway project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from ticket.views import *

urlpatterns = [
    path("admin/", admin.site.urls),
    path("user/", include('django.contrib.auth.urls')),
    path("", landing, name='landing'),
    path('signup/', signup, name='signup'),
    path('login/', login, name='login'),
    path('history/', history, name='history'),
    path('book_ticket/', book_ticket, name='book_ticket'),
    path('get_ticket_price/', get_ticket_price, name='get_ticket_price'),
    path('get_all_users/', get_all_users, name='get_all_users'),
    path('top_up_wallet/', top_up_wallet, name='top_up_wallet'),
    path('verify_payment/', verify_payment, name='verify_payment'),
    path('change_username/', change_username, name='change_username'),
    path('change_email/', change_email, name='change_email'),
    path('change_phone_number/', change_phone_number, name='change_phone_number'),
    path('credit_user/', credit_user, name='credit_user'),
    path('debit_user/', debit_user, name='debit_user'),
    path('get_user_info/', get_user_info, name='get_user_info'),
    path('get_all_tickets/', get_all_tickets, name='get_all_tickets'),
    path('dashboard/', index, name='index'),
    path('verify_email/', verify_email, name='verify_email'),
    path('verified/', verified, name='verified' ),
    path('not_verified/', not_verified, name='not_verified'),
    path('get_all_transactions/', get_all_transactions, name='get_all_transactions')
]
