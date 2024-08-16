from django.urls import path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from . import views

urlpatterns = [
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('user/login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('user/register/', views.UserRegister.as_view(), name=''),
    path('image/', views.RecognizeImage.as_view(), name=''),
    path('room/create/', views.CreateRoom.as_view(), name=''),
    path('room/validate/<str:code>/', views.ValidateRoomCode.as_view(), name=''),
    path('', views.chat),

]
