"""
"""
from django.contrib import admin
from django.urls import path
from Cgame import views
from . import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('',views.home, name='home'),
    path('increment/', views.increment_counter, name='increment_counter'),
    path('task',views.taskList, name='task'),
    path('boost/', views.boost, name='boost'),
    path('signup/', views.signup, name='signup'),
    path('login/', views.login_view, name='login'),
    path('leaderboard',views.leaderboard, name='leaderboard'),
    path('get-button-state/', views.get_button_state, name='get_button_state'),
    path('update-button-state/', views.update_button_state, name='update_button_state'),
    path('api/balance/', views.get_balance, name='get_balance'),
    path('activate/<uidb64>/<token>/', views.activate, name='activate'),
]
if settings.DEBUG is False:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

