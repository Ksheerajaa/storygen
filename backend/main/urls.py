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
    path('api/stream-generate-story/', views.StreamingStoryGenerationView.as_view(), name='stream-generate-story'),
    
    # Debug endpoints for testing
    path('api/test-story/', views.TestStoryView.as_view(), name='test-story'),
    path('api/test-images/', views.TestImagesView.as_view(), name='test-images'),
    path('api/test-orchestrator/', views.TestOrchestratorView.as_view(), name='test-orchestrator'),
    path('api/health/', views.HealthCheckView.as_view(), name='health-check'),
]
