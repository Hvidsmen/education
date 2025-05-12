from django.contrib import admin
from .models import *

# Register your models here.
admin.site.register(Course)
admin.site.register(CourseFile)
admin.site.register(Test)
admin.site.register(TestSub)
admin.site.register(TestQuestion)
admin.site.register(TesstQuestionAnswer)
admin.site.register(User)
admin.site.register(StatusUserCourse)
admin.site.register(UsersCourseSubscribe)
admin.site.register(AdminUser)
admin.site.register(Rule)

admin.site.register(CourseSubTitle)
admin.site.register(Company)

