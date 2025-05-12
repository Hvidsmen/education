from django.db import models


class Course(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=2000)

    def __str__(self):
        return self.name


class CourseSubTitle(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=2000)
    ordered = models.IntegerField(null=True)

    def __str__(self):
        return self.name


class CourseFile(models.Model):
    id = models.AutoField(primary_key=True)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    file = models.FileField(upload_to='documents/')
    ordered = models.IntegerField(null=True)
    sub_title = models.ForeignKey(CourseSubTitle, on_delete=models.CASCADE, null=True)

    def __str__(self):
        return self.name


class Test(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=2000)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)

    def __str__(self):
        return self.name


class TestSub(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    test = models.ForeignKey(Test, on_delete=models.CASCADE)

    ordered = models.IntegerField(null=True)

    def __str__(self):
        return self.name


class TestQuestion(models.Model):
    id = models.AutoField(primary_key=True)
    label = models.CharField(max_length=1000)
    test_sub = models.ForeignKey(TestSub, on_delete=models.CASCADE)
    test = models.ForeignKey(Test, on_delete=models.CASCADE)

    ordered = models.IntegerField(null=True)

    def __str__(self):
        return self.label


class TesstQuestionAnswer(models.Model):
    id = models.AutoField(primary_key=True)
    text = models.CharField(max_length=255)
    test_aswer = models.ForeignKey(TestQuestion, on_delete=models.CASCADE)
    ordered = models.IntegerField()
    is_true = models.IntegerField()

    def __str__(self):
        return f"""{self.test_aswer.label}
{self.text}"""


class Rule(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class Company(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


from django.contrib.auth.models import User as UserSyst


class User(models.Model):
    email = models.CharField(max_length=255, primary_key=True)
    password = models.CharField(max_length=255)
    fio = models.CharField(max_length=500, null=True)
    login = models.CharField(max_length=500, null=True)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, null=True)
    rules = models.ForeignKey(Rule, null=True, on_delete=models.CASCADE)

    user_syst = models.ForeignKey(UserSyst, on_delete=models.CASCADE, null=True)

    def __str__(self):
        return self.email


class StatusUserCourse(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    is_for_action_amdin = models.IntegerField(null=True)

    def __str__(self):
        return self.name


class UsersCourseSubscribe(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    status = models.ForeignKey(StatusUserCourse, on_delete=models.CASCADE)
    date_start = models.DateField()
    date_end = models.DateField()

    def __str__(self):
        return f'{self.user} == {self.course}'


class AdminUser(models.Model):
    login = models.CharField(max_length=255)
    password = models.CharField(max_length=255)

# Create your models here.
