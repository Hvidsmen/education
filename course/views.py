from django.http import HttpResponse
from django.shortcuts import render
from .models import *
from django.http import Http404
from datetime import datetime, timedelta

from django.contrib.auth import login, authenticate
from .forms import LoginForm
import smtplib
from django.core.mail import send_mail
from django.conf import settings


def index(request):
    from django.conf import settings
    return HttpResponse("Hello, world. You're at the polls index. " + str(settings.BASE_DIR))


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
    return render(request, "course/login.html", {'form': form, 'is_admin': 0})


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

    if user_obj.rules.name == 'Администратор':
        course = Course.objects.all()
        return render(request, "course/admin_course_list.html",
                      {"courses": course, 'is_admin': is_admin(user_obj), 'user_sdo': user_obj})

    elif user_obj.rules.name == 'Наблюдатель':

        course_user_id = [u.course.id for u in UsersCourseSubscribe.objects.filter(user=user_obj)]

        course = Course.objects.filter(id__in=course_user_id)

        return render(request, "course/course_list.html",
                      {"courses": course, 'is_admin': is_admin(user_obj), 'user_sdo': user_obj})

    elif user_obj.rules.name == 'Студент':
        statuses = StatusUserCourse.objects.filter(name__in=['Завершил успешно', 'Проходит', 'Подписан'])
        course = UsersCourseSubscribe.objects.filter(user=user_obj, status__in=statuses)

        return render(request, "course/course_list_student.html",
                      {"courses": course, 'is_admin': is_admin(user_obj), 'user_sdo': user_obj})


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
            course_files = CourseFile.objects.filter(sub_title=cid.id, course= course_id).order_by('ordered')

            content[sub_title] = course_files
        user_obj = get_user(request)

        return render(request, "course/course.html",
                      {"course_files": content, 'course': course, 'is_admin': is_admin(user_obj), 'user_sdo': user_obj})

    except Course.DoesNotExist:
        raise Http404("Question does not exist")


import random


def get_course_test(course_id):
    course = Course.objects.get(pk=course_id)
    test_obj = Test.objects.get(course=course_id)
    test = {}

    test_q_ = list(TestQuestion.objects.filter(test=test_obj.id).order_by('ordered'))

    test_q = []
    for _ in range(min(10, len(test_q_))):
        q_c = random.choice(test_q_)
        test_q.append(q_c)
        test_q_.remove(q_c)

    for tq in test_q:
        test_a = TesstQuestionAnswer.objects.filter(test_aswer=tq.id).order_by('ordered')
        test[tq] = test_a
    return course, test


def course_test_from(request, course_id):
    if request.user.is_authenticated == False:
        return login_view(request)

    course, test = get_course_test(course_id)
    user_obj = get_user(request)
    return render(
        request
        , "course/test_course.html"
        , {'course': course, 'test': test, 'is_admin': is_admin(user_obj), 'user_sdo': user_obj}
    )


def course_result_test(request):
    if request.user.is_authenticated == False:
        return login_view(request)
    print(request.POST)
    print("result test")
    course_id = request.POST.get("course_id", "Undefined")

    course, _ = get_course_test(course_id)

    test_obj = Test.objects.get(course=course_id)
    questions = TestQuestion.objects.filter(test=test_obj.id)

    is_all_true = 1
    cnt_answer = 0
    for questuion in questions:
        answer_users = request.POST.getlist(f'{questuion.id}', [])

        if len(answer_users) != 0:
            cnt_answer += 1
            answer_true = {f'{q.id}' for q in TesstQuestionAnswer.objects.filter(test_aswer=questuion.id, is_true=1)}

            if set(answer_users) == set(answer_true):
                pass
            else:
                is_all_true = 0

                continue

    is_all_true = 1 if cnt_answer == 10 else 0

    res_messeger = 'Сдан' if is_all_true == 1 else 'Не сдан'
    user_obj = get_user(request)
    if res_messeger == 'Сдан':
        st = StatusUserCourse.objects.get(name='Завершил успешно')
        uc = UsersCourseSubscribe.objects.get(user=user_obj, course=course)
        uc.status = st
        uc.save()

    return render(
        request
        , "course/test_course_res.html"
        , {'course': course, 'res_messeger': res_messeger, 'flag_msg': is_all_true,
           'is_admin': is_admin(user_obj), 'user_sdo': user_obj}
    )


from django.contrib.auth.models import User as UserDj


def create_user(fio, email, company, rule):
    password_ = email.split('@')[0][:5] + 'qazwsx!su'
    login = email.split('@')[0]
    rule = Rule.objects.get(id=rule)
    company = Company.objects.get(id=company)

    user_obj_d = UserDj.objects.create(username=login, email=email, password=password_)
    user_obj_d.set_password(password_)
    user_obj_d.save()
    user_obj = User.objects.create(fio=fio, company=company, email=email, password=password_, rules=rule, login=login,
                                   user_syst=user_obj_d)

    return user_obj


def send_mail_subscribe(email_to, message):
    try:
        server = smtplib.SMTP_SSL('smtp.yandex.ru', 465)
        server.login('request-profpromeco@yandex.ru', 'ijyrxjliicwfkjio')
        server.sendmail('request-profpromeco@yandex.ru', email_to, message)
        server.quit()
    except:
        return 0


def list_course_view(req):
    user = get_user(req)
    user_comp = User.objects.filter(company=user.company)
    company_id_filter = req.POST.get('company_filter', 'NA')

    if company_id_filter == 'NA':
        user_companies = User.objects.all()
    else:
        user_companies = User.objects.filter(company=company_id_filter)

    course_id_filter = req.POST.get('course_filter', 'NA')
    if course_id_filter == 'NA':
        course_filter = Course.objects.all()
    else:
        course_filter = Course.objects.filter(id=course_id_filter)
    user_course_comp = UsersCourseSubscribe.objects.filter(user__in=user_comp, course__in=course_filter).order_by(
        'course', 'date_end')
    courses_list = Course.objects.all()
    company_list = Company.objects.all()
    return render(req, "course/list_course_comp.html",
                  {'user_course_comp': user_course_comp, 'user_sdo': user, 'company_list': company_list,
                   'courses_list': courses_list})


def subscribe(request):
    print(request.POST)

    if request.user.is_authenticated == False:
        return login_view(request)

    company_id_filter = request.POST.get('company_filter', 'NA')

    if company_id_filter == 'NA':
        user_companies = User.objects.all()
    else:
        user_companies = User.objects.filter(company=company_id_filter)

    course_id_filter = request.POST.get('course_filter', 'NA')

    if course_id_filter == 'NA':
        course_filter = Course.objects.all()
    else:
        course_filter = Course.objects.filter(id=course_id_filter)

    rules_adm = Rule.objects.filter(name='Администратор')
    user_admin = User.objects.filter(rules__in = rules_adm)

    user_course = UsersCourseSubscribe.objects.filter(user__in=user_companies, course__in=course_filter).exclude(user__in=user_admin).order_by(
        'course', 'date_end')

    status_user = StatusUserCourse.objects.filter(is_for_action_amdin=1)

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
        fio = request.POST.get('name_new', '')
        company = request.POST.get('company_new', '')
        rule = request.POST.get('rule_new', '')
        try:
            user_obj = User.objects.get(email=email)
        except:
            user_obj = create_user(fio, email, company, rule)

        status_obj = StatusUserCourse.objects.get(name='Подписан')
        datestart = datetime.today()
        dateend = datestart + timedelta(days=30)

        msg = f"""Вы записаны на курс
        {course_new.name}
        Сслыка
        https://iprofpromeducation.pro/list_course/  
        
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
    courses_list = Course.objects.all()
    company_list = Company.objects.all()
    rules_lst = Rule.objects.filter(name__in=['Наблюдатель', 'Студент'])

    return render(request, "course/subscribe.html",
                  {'user_course': user_course, 'rules_lst': rules_lst, 'status_user': status_user,
                   'courses_list': courses_list,
                   'is_admin': is_admin(user_obj), 'company_list': company_list, 'user_sdo': user_obj})
