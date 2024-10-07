from django.contrib import admin
from .models import Gifter, Taker, User, Question, Answer


admin.site.register(Gifter)

admin.site.register(Taker)
admin.site.register(User)
admin.site.register(Question)
admin.site.register(Answer)