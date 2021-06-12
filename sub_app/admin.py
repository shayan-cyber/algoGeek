from django.contrib import admin
from . models import Question,DsAlgoTopics,Contest,Profile,ScoreCard

# Register your models here.
admin.site.register(Question)
admin.site.register(DsAlgoTopics)
admin.site.register(Contest)
admin.site.register(Profile)
admin.site.register(ScoreCard)
