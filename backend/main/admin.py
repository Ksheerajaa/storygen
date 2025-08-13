from django.contrib import admin
from .models import Story, StoryGeneration


@admin.register(Story)
class StoryAdmin(admin.ModelAdmin):
    list_display = ['title', 'author', 'created_at', 'updated_at']
    list_filter = ['created_at', 'author']
    search_fields = ['title', 'content']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(StoryGeneration)
class StoryGenerationAdmin(admin.ModelAdmin):
    list_display = ['id', 'prompt', 'status', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['prompt']
    readonly_fields = ['created_at']
