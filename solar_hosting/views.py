from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib.auth import login, logout, authenticate, update_session_auth_hash
from .forms import CustomUserCreationForm, EmailChangeForm, PhoneChangeForm, NameChangeForm, HostingPurchaseForm, \
    DomainPurchaseForm, ContactForm
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib import messages
import logging
from .models import HostingPlan, HostingPurchase, DomainPurchase, ContactMessage
from django.http import JsonResponse

logger = logging.getLogger(__name__)


# Create your views here.
def index(request):
    return render(request, 'solar_hosting/index.html')


def features(request):
    return render(request, 'solar_hosting/features.html')


def domain(request):
    return render(request, 'solar_hosting/domain.html')


def hosting(request):
    return render(request, 'solar_hosting/hosting.html')


def pricing(request):
    return render(request, 'solar_hosting/pricing.html')


def testimonials(request):
    return render(request, 'solar_hosting/testimonials.html')


def contact(request):
    return render(request, 'solar_hosting/contact.html')


def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('solar_hosting:dashboard')
        else:
            messages.error(request, 'Неправильное имя пользователя или пароль. Попробуйте ещё раз.')
            # Вы можете добавить другую обработку ошибки, если необходимо
    return redirect('solar_hosting:main')  # Перенаправляем на главную страницу после неудачного входа


def registration_view(request):
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            user.first_name = form.cleaned_data['first_name']
            user.last_name = form.cleaned_data['last_name']
            if not user.first_name:
                user.first_name = ""
            if not user.last_name:
                user.last_name = ""
            user.save()
            login(request, user)
            return redirect('solar_hosting:dashboard')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
    else:
        form = CustomUserCreationForm()
    return render(request, 'solar_hosting/index.html', {'form': form})


@login_required
def dashboard(request):
    if request.user.is_authenticated:
        return render(request, 'solar_hosting/dashboard.html')
    else:
        return redirect('solar_hosting:main')


@login_required
def profile(request):
    user = request.user
    return render(request, 'solar_hosting/profile.html', {'user': user})


@login_required
def settings(request):
    return render(request, 'solar_hosting/settings.html')


def logout_view(request):
    if request.method == 'POST':
        logout(request)
    return redirect('solar_hosting:main')


@login_required
def change_settings(request):
    profile_form = CustomUserCreationForm(instance=request.user)
    name_form = NameChangeForm(instance=request.user)
    email_form = EmailChangeForm(initial={'email': request.user.email})
    phone_form = PhoneChangeForm(initial={'phone': request.user.phone})
    password_form = PasswordChangeForm(request.user)

    if request.method == 'POST':
        action = request.GET.get('action')
        try:
            if action == 'profile':
                name_form = NameChangeForm(request.POST, instance=request.user)
                if name_form.is_valid():
                    name_form.save()  # Сохранить данные имени и фамилии
                    request.user.refresh_from_db()  # Обновить данные пользователя из базы данных
                    logger.info('Личные данные обновлены успешно.')
                    messages.success(request, 'Личные данные обновлены успешно.')

            elif action == 'email':
                email_form = EmailChangeForm(request.POST)
                if email_form.is_valid():
                    new_email = email_form.cleaned_data['email']
                    request.user.email = new_email
                    request.user.save()
                    logger.info('Email успешно изменен.')
                    messages.success(request, 'Email успешно изменен.')

            elif action == 'phone':
                phone_form = PhoneChangeForm(request.POST)
                if phone_form.is_valid():
                    new_phone = phone_form.cleaned_data['phone']
                    request.user.phone = new_phone
                    request.user.save()
                    logger.info('Телефон успешно изменен.')
                    messages.success(request, 'Телефон успешно изменен.')

            elif action == 'password':
                password_form = PasswordChangeForm(request.user, request.POST)
                if password_form.is_valid():
                    user = password_form.save()
                    update_session_auth_hash(request, user)
                    logger.info('Пароль успешно изменен.')
                    messages.success(request, 'Пароль успешно изменен.')
        except Exception as e:
            logger.error(f'Произошла ошибка: {e}')
            messages.error(request, 'Произошла ошибка. Пожалуйста, попробуйте снова.')

    return render(request, 'solar_hosting/settings.html', {
        'profile_form': profile_form,
        'name_form': name_form,
        'email_form': email_form,
        'phone_form': phone_form,
        'password_form': password_form,
    })


def purchase(request):
    if request.method == 'POST':
        form = HostingPurchaseForm(request.POST)
        if form.is_valid():
            selected_plan = form.cleaned_data['plan']

            # В этой части кода вы проверяете, какой именно план выбрал пользователь
            if selected_plan.plan_id == 'basic':
                # Выполняете действия для Basic Plan
                # Например, создаете экземпляр HostingPurchase и сохраняете его в базе данных
                purchase = HostingPurchase(user=request.user, plan=selected_plan)
                purchase.save()
            elif selected_plan.plan_id == 'premium':
                # Выполняете действия для Premium Plan
                # Аналогично создаете и сохраняете информацию о покупке
                purchase = HostingPurchase(user=request.user, plan=selected_plan)
                purchase.save()
            elif selected_plan.plan_id == 'ultimate':
                # Выполняете действия для Ultimate Plan
                # Создаете и сохраняете информацию о покупке
                purchase = HostingPurchase(user=request.user, plan=selected_plan)
                purchase.save()

            return render(request, 'solar_hosting/purchase_confirmation.html', {'purchase': purchase})
    else:
        form = HostingPurchaseForm()
    return render(request, 'solar_hosting/purchase.html', {'form': form})


@login_required
def purchase_history(request):
    hosting_purchases = HostingPurchase.objects.filter(user=request.user)
    domain_purchases = DomainPurchase.objects.filter(user=request.user)
    return render(request, 'solar_hosting/purchase_history.html', {
        'hosting_purchases': hosting_purchases,
        'domain_purchases': domain_purchases,
    })


@login_required
def purchase_domain(request):
    if request.method == 'POST':
        form = DomainPurchaseForm(request.POST)
        if form.is_valid():
            domain_name = form.cleaned_data['domain_name']

            # Проверка, существует ли уже такой домен в базе данных
            if DomainPurchase.objects.filter(user=request.user, domain_name=domain_name).exists():
                # Если домен уже существует, добавьте сообщение об ошибке
                messages.error(request, 'This domain is already purchased by you.')
            else:
                # Здесь вы можете выполнить действия для покупки домена, например, создать экземпляр DomainPurchase
                # и сохранить его в базе данных
                domain_purchase = DomainPurchase(user=request.user, domain_name=domain_name)
                domain_purchase.save()

                # Перенаправьте пользователя на страницу подтверждения после покупки
                return render(request, 'solar_hosting/purchase_domain_confirmation.html',
                              {'domain_purchase': domain_purchase})

    else:
        form = DomainPurchaseForm()

    return render(request, 'solar_hosting/purchase_domain.html', {'form': form})


@login_required
def purchase_domain_confirmation(request):
    # Здесь вы можете выполнить действия для страницы подтверждения покупки домена
    # Например, получить информацию о покупке, если это необходимо

    return render(request, 'solar_hosting/purchase_domain_confirmation.html')


# def contact_view(request):
#     if request.method == 'POST':
#         form = ContactForm(request.POST)
#         if form.is_valid():
#             form.save()
#             return redirect('contact_success')
#     else:
#         form = ContactForm()
#     return render(request, 'solar_hosting/contact.html', {'form': form})

def contact_view(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            message = ContactMessage(
                first_name=data['first_name'],
                last_name=data['last_name'],
                email=data['email'],
                phone=data['phone'],
                comments=data['comments'],
                read=False
            )
            message.save()
            # form.save()  # Сохранить данные из формы
            return redirect('solar_hosting:contact_success')
    else:
        form = ContactForm()
    return render(request, 'solar_hosting/contact.html', {'form': form})


def contact_success(request):
    return render(request, 'solar_hosting/contact_success.html')


def contactmessage_unread_count(request):
    # Ваша логика подсчета непрочитанных сообщений
    unread_count = 50  # Замените на реальное значение

    return JsonResponse({'unread_count': unread_count})
