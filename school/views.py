from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.conf import settings
from .models import (
    Notice, Notification, GalleryCategory, GalleryImage,
    AdmissionApplication, Event, Enquiry,
    ActivityUpdate, VideoEmbed, Student, Teacher,
    SchoolClass, Homework, UserProfile,
)
from .forms import AdmissionForm, EnquiryForm, UserRegistrationForm
from datetime import date


def home(request):
    notices = Notice.objects.all()[:5]
    updates = ActivityUpdate.objects.all()[:3]
    events = Event.objects.filter(date__gte=date.today())[:3]
    videos = VideoEmbed.objects.filter(is_active=True)[:2]
    popup_notice = Notice.objects.filter(is_popup=True).order_by('-created_at').first()
    context = {
        'notices': notices,
        'updates': updates,
        'events': events,
        'videos': videos,
        'popup_notice': popup_notice,
    }
    return render(request, 'home.html', context)


def about(request):
    teachers = Teacher.objects.all()
    return render(request, 'about.html', {'teachers': teachers})


def gallery(request):
    categories = GalleryCategory.objects.all()
    images = GalleryImage.objects.all()
    return render(request, 'gallery.html', {'categories': categories, 'images': images})


def events(request):
    upcoming_events = Event.objects.filter(date__gte=date.today())
    past_events = Event.objects.filter(date__lt=date.today()).order_by('-date')[:5]
    return render(request, 'events.html', {
        'upcoming_events': upcoming_events,
        'past_events': past_events,
    })


def updates(request):
    all_updates = ActivityUpdate.objects.all()
    return render(request, 'updates.html', {'updates': all_updates})


def admissions(request):
    if request.method == 'POST':
        form = AdmissionForm(request.POST)
        if form.is_valid():
            app = form.save()

            messages.success(request, 'Admission application submitted successfully. We will contact you soon.')
            return redirect('admissions')
        # Form is invalid — fall through and re-render with errors
    else:
        form = AdmissionForm()

    return render(request, 'admissions.html', {
        'form': form,
        'programs': AdmissionApplication.PROGRAM_CHOICES,  # keep backward-compat with template
    })


def contact(request):
    if request.method == 'POST':
        form = EnquiryForm(request.POST)
        if form.is_valid():
            enquiry = form.save()

            messages.success(request, 'Your enquiry has been submitted successfully. We will get back to you shortly.')
            return redirect('contact')
        # Invalid form — re-render with errors
    else:
        form = EnquiryForm()

    return render(request, 'contact.html', {'form': form})
def admin(request):
    return redirect('admin')


def notice_list(request):
    notices = Notice.objects.all()
    popup_notice = Notice.objects.filter(is_popup=True).order_by('-created_at').first()
    return render(request, 'notices.html', {
        'notices': notices,
        'popup_notice': popup_notice
    })


@login_required
def notification_list(request):
    notifications = Notification.objects.filter(user=request.user)
    return render(request, 'notifications.html', {'notifications': notifications})


@login_required
@require_POST
def mark_notification_read(request, pk):
    notification = get_object_or_404(Notification, pk=pk, user=request.user)
    notification.is_read = True
    notification.save()
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({'status': 'success'})
    return redirect('notification_list')


@login_required
@require_POST
def mark_all_notifications_read(request):
    Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({'status': 'success'})
    return redirect('notification_list')


# Authentication Views
def register(request):
    if request.user.is_authenticated:
        return redirect('home')
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f'Account created successfully! Welcome, {user.first_name}!')
            return redirect('home')
    else:
        form = UserRegistrationForm()
    return render(request, 'register.html', {'form': form})


def login_user(request):
    if request.user.is_authenticated:
        return redirect('home')
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f'Welcome back, {user.first_name or user.username}!')
            return redirect('home')
    else:
        form = AuthenticationForm()
    return render(request, 'login.html', {'form': form})


@login_required
def logout_user(request):
    logout(request)
    messages.success(request, 'You have been logged out.')
    return redirect('home')


# ─────────────────────────────────────────────────────────────
#  Homework API
# ─────────────────────────────────────────────────────────────

@login_required
def homework_api(request):
    """
    AJAX endpoint: returns JSON list of homework for the logged-in user's class.
    Returns 401 for unauthenticated, 200 with homework list otherwise.
    """
    try:
        profile = request.user.profile
        school_class = profile.school_class
    except UserProfile.DoesNotExist:
        school_class = None

    if school_class is None:
        return JsonResponse({
            'class_name': None,
            'homework': [],
            'message': 'No class assigned to your account. Please contact the school admin.'
        })

    homework_qs = Homework.objects.filter(school_class=school_class).order_by('-date_assigned')
    data = []
    for hw in homework_qs:
        data.append({
            'id': hw.id,
            'title': hw.title,
            'description': hw.description,
            'date_assigned': hw.date_assigned.strftime('%d %b %Y'),
            'due_date': hw.due_date.strftime('%d %b %Y') if hw.due_date else None,
            'is_overdue': hw.is_overdue,
        })

    return JsonResponse({
        'class_name': school_class.name,
        'homework': data,
        'message': None
    })
