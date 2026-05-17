from django.urls import path
from . import views

urlpatterns = [
    path('diagnose', views.diagnose, name='diagnose'),
    path('chat', views.chat, name='chat'),
    path('health', views.health, name='health'),
    path('diseases', views.get_diseases, name='get_diseases'),
    path('symptoms', views.get_symptoms, name='get_symptoms'),
]
