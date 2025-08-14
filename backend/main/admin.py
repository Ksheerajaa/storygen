from django.contrib import admin
from .models import Story, StoryGeneration, StorySession, GeneratedContent


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


@admin.register(StorySession)
class StorySessionAdmin(admin.ModelAdmin):
    list_display = ['session_id', 'prompt_text', 'status', 'user', 'created_at']
    list_filter = ['status', 'created_at', 'user']
    search_fields = ['session_id', 'prompt_text']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(GeneratedContent)
class GeneratedContentAdmin(admin.ModelAdmin):
    list_display = ['id', 'session', 'processing_status', 'created_at']
    list_filter = ['processing_status', 'created_at']
    search_fields = ['session__session_id']
    readonly_fields = ['created_at']
