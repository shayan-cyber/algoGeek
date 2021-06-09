from django.contrib import admin
from . models import Question,DsAlgoTopics,Contest

# Register your models here.
admin.site.register(Question)
admin.site.register(DsAlgoTopics)
admin.site.register(Contest)

