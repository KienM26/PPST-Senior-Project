from django.contrib import admin
from .models import Doctor, Test, Stimulus, Response, Results, Latency

admin.site.register(Doctor)
admin.site.register(Test)
admin.site.register(Stimulus)
admin.site.register(Response)
admin.site.register(Results)
admin.site.register(Latency)