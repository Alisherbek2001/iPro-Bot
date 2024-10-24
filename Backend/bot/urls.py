from django.urls import path
from .views import UserDetailCreateView

urlpatterns = [
    path('user/<int:telegram_id>/', UserDetailCreateView.as_view(), name='user-detail-create'),
    path('user/', UserDetailCreateView.as_view(), name='user-create'),
]