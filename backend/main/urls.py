from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'stories', views.StoryViewSet)
router.register(r'generations', views.StoryGenerationViewSet)

app_name = 'main'

urlpatterns = [
    path('api/', include(router.urls)),
    path('api/generate-story/', views.GenerateStoryView.as_view(), name='generate-story'),
]
