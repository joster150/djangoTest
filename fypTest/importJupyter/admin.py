from django.contrib import admin
from .models import ModelDefinition,Data,step_tracker,Pipelines,Pipeline,NotebookModel,DocumentationPosts,DocumentationImage

admin.site.register(ModelDefinition)
admin.site.register(Data)
admin.site.register(step_tracker)
admin.site.register(Pipelines)
admin.site.register(Pipeline)
admin.site.register(NotebookModel)
admin.site.register(DocumentationPosts)
admin.site.register(DocumentationImage)
