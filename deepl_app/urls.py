from django.urls import path
from .views import DeepLTranslateView

urlpatterns = [
    path('deepl/', DeepLTranslateView.as_view(), name='deepl-translate'),
]