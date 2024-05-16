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
from ticket.views import signup, login, history, book_ticket, get_ticket_price, get_all_users, top_up_wallet

urlpatterns = [
    path("admin/", admin.site.urls),
    path("user/", include('django.contrib.auth.urls')),
    path('signup/', signup, name='signup'),
    path('login/', login, name='login'),
    path('history/', history, name='history'),
    path('book_ticket/', book_ticket, name='book_ticket'),
    path('get_ticket_price/', get_ticket_price, name='get_ticket_price'),
    path('get_all_users/', get_all_users, name='get_all_users'),
    path('top_up_wallet/', top_up_wallet, name='top_up_wallet')
]
