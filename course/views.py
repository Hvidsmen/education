from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render, redirect
from .models import *
from django.http import Http404
from datetime import datetime, timedelta
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, authenticate
from .forms import SignUpForm, LoginForm
import smtplib
from django.core.mail import send_mail
from django.conf import settings

def index(request):
    return HttpResponse("Hello, world. You're at the polls index.")


def login_view(request):
    form = LoginForm(data=request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(username=username, password=password)  # Проверяем учетные данные
            if user is not None:
                login(request, user)  # Выполняем вход
                return list_course(request)  # Перенаправляем на главную страницу
    return render(request, 'course\login.html', {'form': form, 'is_admin': 0})


def get_user(req):
    user_obj = User.objects.get(email=req.user.email)
    return user_obj


def is_admin(user_obj):
    if user_obj.rules.name == 'Администратор':
        return 1
    else:
        return 0


def list_course(request):
    if request.user.is_authenticated == False:
        return login_view(request)
    user_obj = get_user(request)

    course_user_id = [u.course.id for u in UsersCourseSubscribe.objects.filter(user=user_obj)]
    course = Course.objects.filter(id__in=course_user_id)

    return render(request, "course/course_list.html", {"courses": course, 'is_admin': is_admin(user_obj)})


def course(request, course_id):
    if request.user.is_authenticated == False:
        return login_view(request)
    try:
        course = Course.objects.get(pk=course_id)
        course_files_id = CourseFile.objects.filter(course=course_id).values_list('sub_title', flat=True).distinct()
        sub_titles = CourseSubTitle.objects.filter(id__in=course_files_id).order_by('ordered')
        content = {}
        for cid in sub_titles:
            sub_title = CourseSubTitle.objects.get(pk=cid.id)
            course_files = CourseFile.objects.filter(sub_title=cid.id).order_by('ordered')

            content[sub_title] = course_files
        user_obj = get_user(request)
        return render(request, "course/course.html",
                      {"course_files": content, 'course': course, 'is_admin': is_admin(user_obj)})

    except Course.DoesNotExist:
        raise Http404("Question does not exist")


def get_course_test(course_id):
    course = Course.objects.get(pk=course_id)
    test_obj = Test.objects.get(course=course_id)
    test = {}

    test_sub = TestSub.objects.filter(course=course_id).order_by('ordered')
    for ts in test_sub:
        test[ts] = []
        test_q = TestQuestion.objects.filter(test=test_obj.id, test_sub=ts.id).order_by('ordered')
        tq_dict = {}
        for tq in test_q:
            test_a = TesstQuestionAnswer.objects.filter(test_aswer=tq.id).order_by('ordered')

            tq_dict[tq] = test_a
        test[ts].append(tq_dict)
    return course, test


def course_test_from(request, course_id):
    if request.user.is_authenticated == False:
        return login_view(request)

    course, test = get_course_test(course_id)
    user_obj = get_user(request)
    return render(
        request
        , "course/test_course.html"
        , {'course': course, 'test': test, 'is_admin': is_admin(user_obj)}
    )


def course_result_test(request):
    if request.user.is_authenticated == False:
        return login_view(request)
    course_id = request.POST.get("course_id", "Undefined")

    course, test = get_course_test(course_id)

    is_all_true = 1

    test_obj = Test.objects.get(course=course_id)
    questions = TestQuestion.objects.filter(test=test_obj.id)

    for questuion in questions:
        answer_users = request.POST.getlist(f'{questuion.id}', [])
        if len(answer_users) == 0:
            is_all_true = 0
            break
        answer_true = {f'{q.id}' for q in TesstQuestionAnswer.objects.filter(test_aswer=questuion.id, is_true=1)}

        if set(answer_users) == set(answer_true):
            is_all_true = 1
        else:
            is_all_true = 0
            break

    res_messeger = 'Сдан' if is_all_true == 1 else 'Не сдан'
    user_obj = get_user(request)
    if res_messeger == 'Сдан':
        st = StatusUserCourse.objects.get(name='Завершил успешно')
        uc = UsersCourseSubscribe.objects.get(user=user_obj, course=course)
        uc.status = st
        uc.save()

    return render(
        request
        , "course/test_course.html"
        , {'course': course, 'test': test, 'res_messeger': res_messeger, 'flag_msg': is_all_true,
           'is_admin': is_admin(user_obj)}
    )


from django.contrib.auth.models import User as UserDj


def create_user(email):
    password_ = email.split('@')[0][:5] + 'qazwsx!su'
    login = email.split('@')[0]
    rule = Rule.objects.get(name='Студент')
    user_obj = User.objects.create(email=email, password=password_, rules=rule)

    user_obj_d = UserDj.objects.create(login=login, email=email, password=password_)
    return user_obj


def send_mail_subscribe(email_to, message):
    try:
        server = smtplib.SMTP_SSL('smtp.yandex.ru', 465)
        server.login('request-profpromeco@yandex.ru', 'ijyrxjliicwfkjio')
        server.sendmail('request-profpromeco@yandex.ru', email_to, message)
        server.quit()
    except:
        return 0

def subscribe(request):
    if request.user.is_authenticated == False:
        return login_view(request)
    user_course = UsersCourseSubscribe.objects.all().order_by('course', 'date_end')
    status_user = StatusUserCourse.objects.filter(is_for_action_amdin=1)
    courses_list = Course.objects.all()
    new_status = request.POST.get('new_status', 'NA')

    if new_status != 'NA':
        sub_id = request.POST.get('subscribe_id', 'NA')
        sub_obj = UsersCourseSubscribe.objects.get(pk=sub_id)
        sub_obj.status = StatusUserCourse.objects.get(pk=new_status)
        sub_obj.save()

    course_new = request.POST.get('course_new', 'NA')
    if course_new != 'NA':
        course_new = Course.objects.get(pk=course_new)
        email = request.POST.get('email', '')
        try:
            user_obj = User.objects.get(email=email)
        except:
            user_obj = create_user(email)

        status_obj = StatusUserCourse.objects.get(name='Подписан')
        datestart = datetime.today()
        dateend = datestart + timedelta(days=30)


        msg = f"""Вы записаны на курс
        {course_new.name}
        Почта
        {user_obj.email}
        Логин для входа
        {user_obj.email.split('@')[0]}
        Пароль для входа
        {user_obj.password} 
        """
        print(user_obj.email)
        send_mail(
            "Логин и пароль от системы СДО",
            msg,
            f"{settings.EMAIL_HOST_USER}",
            [f"{user_obj.email}"],
            fail_silently=False,
        )

        if len(UsersCourseSubscribe.objects.filter(user=user_obj
                , course=course_new)) == 0:
            su_obj = UsersCourseSubscribe.objects.create(
                user=user_obj
                , course=course_new
                , status=status_obj
                , date_start=datestart
                , date_end=dateend
            )
    user_obj = get_user(request)
    return render(request, "course/subscribe.html",
                  {'user_course': user_course, 'status_user': status_user, 'courses_list': courses_list,
                   'is_admin': is_admin(user_obj)})
