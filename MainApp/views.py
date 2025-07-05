import logging
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django_ratelimit.decorators import ratelimit
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Q
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings

from .forms import StudentRegistrationForm, TeacherRegistrationForm, StudentProfileForm, TeacherProfileForm
from .models import User, StudentProfile, TeacherProfile, Course, Enrollment


# Logger for rate-limited events
logger = logging.getLogger('ratelimit')


# ----------------------------
# Home Page
# ----------------------------
def home(request):
    return render(request, 'home.html')


# ----------------------------
# Student Registration
# ----------------------------
@ratelimit(key='ip', rate='3/m', block=True)
def register_student(request):
    if getattr(request, 'limited', False):
        ip = request.META.get('REMOTE_ADDR')
        logger.warning(f"Rate limit exceeded on student registration by IP: {ip}")
        return HttpResponse("Too many registration attempts. Try again later.", status=429)

    if request.method == 'POST':
        form = StudentRegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Student registration successful.")
            return redirect('dashboard')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = StudentRegistrationForm()
    return render(request, 'register.html', {'form': form})


# ----------------------------
# Teacher Registration
# ----------------------------
@ratelimit(key='ip', rate='3/m', block=True)
def register_teacher(request):
    if getattr(request, 'limited', False):
        ip = request.META.get('REMOTE_ADDR')
        logger.warning(f"Rate limit exceeded on teacher registration by IP: {ip}")
        return HttpResponse("Too many registration attempts. Try again later.", status=429)

    if request.method == 'POST':
        form = TeacherRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Teacher registration successful.")
            return redirect('dashboard')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = TeacherRegistrationForm()
    return render(request, 'register.html', {'form': form})


# ----------------------------
# Login View
# ----------------------------
@ratelimit(key='ip', rate='5/m', block=True)
def login_view(request):
    if getattr(request, 'limited', False):
        ip = request.META.get('REMOTE_ADDR')
        logger.warning(f"Rate limit exceeded on login by IP: {ip}")
        return HttpResponse("Too many login attempts. Try again later.", status=429)

    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            messages.success(request, f"Welcome back, {user.username}!")
            return redirect('dashboard')
        else:
            messages.error(request, "Invalid username or password.")
    return render(request, 'login.html')


# ----------------------------
# Logout View
# ----------------------------
@login_required
def logout_view(request):
    logout(request)
    messages.info(request, "You have been logged out.")
    return redirect('login')


# ----------------------------
# Role-Based Dashboard
# ----------------------------
@login_required
def dashboard(request):
    role = request.user.role
    logger.info(f"Dashboard accessed by user {request.user.username} with role {role}")
    
    if role == 'student':
        # Check if user has a profile, if not create one or handle gracefully
        try:
            profile = request.user.student_profile
            logger.info(f"Student profile found for {request.user.username}")
        except Exception as e:
            logger.warning(f"No student profile found for {request.user.username}, creating one. Error: {e}")
            # If no profile exists, create a basic one
            profile = StudentProfile.objects.create(
                user=request.user,
                full_name=request.user.get_full_name() or request.user.username,
                age=18,  # Default age
                contact_number="",
                address_encrypted="",
                guardian_email=request.user.email or "",
            )
        return render(request, 'dashboard/student_dashboard.html', {'profile': profile})
    elif role == 'teacher':
        try:
            profile = request.user.teacher_profile
            logger.info(f"Teacher profile found for {request.user.username}")
        except Exception as e:
            logger.warning(f"No teacher profile found for {request.user.username}, creating one. Error: {e}")
            # If no profile exists, create a basic one
            profile = TeacherProfile.objects.create(
                user=request.user,
                full_name=request.user.get_full_name() or request.user.username,
                department="",
                contact_email=request.user.email or "",
                office_location="",
                bio="",
            )
        return render(request, 'dashboard/teacher_dashboard.html', {'profile': profile})
    elif role == 'admin':
        return render(request, 'dashboard/admin_dashboard.html')
    else:
        messages.error(request, "Unauthorized role.")
        return redirect('login')
    
from .forms import StudentProfileForm, TeacherProfileForm

@login_required
def edit_profile(request):
    role = request.user.role

    if role == 'student':
        profile = request.user.student_profile
        form_class = StudentProfileForm
        template = 'profiles/edit_student_profile.html'

    elif role == 'teacher':
        profile = request.user.teacher_profile
        form_class = TeacherProfileForm
        template = 'profiles/edit_teacher_profile.html'

    else:
        messages.error(request, "Only students and teachers can edit profiles.")
        return redirect('dashboard')

    if request.method == 'POST':
        form = form_class(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated successfully.")
            return redirect('dashboard')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = form_class(instance=profile)

    return render(request, template, {'form': form})

@login_required
def view_transcript(request):
    profile = getattr(request.user, 'student_profile', None)
    if not profile or not profile.transcript:
        messages.error(request, "No transcript available.")
        return redirect('dashboard')
    return render(request, 'profiles/view_transcript.html', {'profile': profile})

@login_required
def course_list(request):
    courses = Course.objects.all()
    return render(request, 'courses/course_list.html', {'courses': courses})

@login_required
def course_detail(request, course_id):
    course = Course.objects.get(id=course_id)
    already_enrolled = Enrollment.objects.filter(student=request.user, course=course).exists()
    can_enroll = not already_enrolled and course.capacity > course.enrollments.filter(status='approved').count()
    error = None
    if request.method == 'POST' and can_enroll:
        # Check prerequisites
        missing = [pr for pr in course.prerequisites.all() if not Enrollment.objects.filter(student=request.user, course=pr, status='approved').exists()]
        if missing:
            error = 'Missing prerequisites: ' + ', '.join([pr.name for pr in missing])
        else:
            Enrollment.objects.create(student=request.user, course=course)
            return redirect('course_detail', course_id=course.id)
    return render(request, 'courses/course_detail.html', {
        'course': course,
        'already_enrolled': already_enrolled,
        'can_enroll': can_enroll,
        'error': error,
        'enrollment': Enrollment.objects.filter(student=request.user, course=course).first(),
    })

@login_required
def admin_enrollment_requests(request):
    if not request.user.is_authenticated or request.user.role != 'admin':
        return redirect('dashboard')
    # Filtering logic
    student_query = request.GET.get('student', '').strip()
    course_query = request.GET.get('course', '').strip()
    pending = Enrollment.objects.filter(status='pending').select_related('student', 'course')
    if student_query:
        pending = pending.filter(student__username__icontains=student_query)
    if course_query:
        pending = pending.filter(course__name__icontains=course_query)
    if request.method == 'POST':
        enrollment_id = request.POST.get('enrollment_id')
        action = request.POST.get('action')
        note = request.POST.get('note', '')
        try:
            enrollment = Enrollment.objects.get(id=enrollment_id, status='pending')
            if action == 'approve':
                enrollment.status = 'approved'
                decision = 'approved'
            elif action == 'deny':
                enrollment.status = 'denied'
                decision = 'denied'
            else:
                decision = None
            enrollment.reviewed_by = request.user
            enrollment.reviewed_at = timezone.now()
            enrollment.note = note
            enrollment.save()
            # Send email notification to student
            if decision:
                subject = f"Enrollment {decision.title()} for {enrollment.course.name}"
                message = f"Dear {enrollment.student.username},\n\nYour enrollment request for {enrollment.course.name} has been {decision}."
                if note:
                    message += f"\n\nNote from admin: {note}"
                message += "\n\nThank you."
                send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [enrollment.student.email], fail_silently=True)
        except Enrollment.DoesNotExist:
            pass
        return redirect('admin_enrollment_requests')
    return render(request, 'admin/enrollment_requests.html', {
        'pending': pending,
        'student_query': student_query,
        'course_query': course_query,
    })

@login_required
def student_schedule(request):
    if not request.user.is_authenticated or request.user.role != 'student':
        return redirect('dashboard')
    enrollments = Enrollment.objects.filter(student=request.user, status='approved').select_related('course')
    return render(request, 'dashboard/student_schedule.html', {'enrollments': enrollments})

@login_required
def teacher_dashboard(request):
    if not request.user.is_authenticated or request.user.role != 'teacher':
        return redirect('dashboard')
    courses = Course.objects.filter(teacher=request.user)
    selected_course = None
    students = None
    message = None
    if request.method == 'POST':
        course_id = request.POST.get('course_id')
        student_username = request.POST.get('student_username')
        try:
            selected_course = Course.objects.get(id=course_id, teacher=request.user)
            student = User.objects.get(username=student_username, role='student')
            # Check if already enrolled
            if Enrollment.objects.filter(student=student, course=selected_course).exists():
                message = f"{student.username} is already enrolled or has a pending request."
            elif selected_course.capacity <= Enrollment.objects.filter(course=selected_course, status='approved').count():
                message = "No seats available in this course."
            else:
                Enrollment.objects.create(student=student, course=selected_course, status='approved', reviewed_by=request.user, reviewed_at=timezone.now())
                message = f"{student.username} has been enrolled in {selected_course.name}."
        except (Course.DoesNotExist, User.DoesNotExist):
            message = "Invalid course or student."
    if selected_course:
        students = Enrollment.objects.filter(course=selected_course, status='approved').select_related('student')
    return render(request, 'dashboard/teacher_dashboard.html', {
        'courses': courses,
        'selected_course': selected_course,
        'students': students,
        'message': message,
    })

@login_required
def teacher_courses(request):
    if not request.user.is_authenticated or request.user.role != 'teacher':
        return redirect('dashboard')
    courses = Course.objects.filter(teacher=request.user)
    return render(request, 'courses/teacher_courses.html', {'courses': courses})

@login_required
def teacher_course_students(request, course_id):
    if not request.user.is_authenticated or request.user.role != 'teacher':
        return redirect('dashboard')
    try:
        course = Course.objects.get(id=course_id, teacher=request.user)
    except Course.DoesNotExist:
        return redirect('teacher_courses')
    enrollments = Enrollment.objects.filter(course=course, status='approved').select_related('student')
    return render(request, 'courses/teacher_course_students.html', {'course': course, 'enrollments': enrollments})

@login_required
def teacher_pending_enrollments(request):
    if not request.user.is_authenticated or request.user.role != 'teacher':
        return redirect('dashboard')
    courses = Course.objects.filter(teacher=request.user)
    pending = Enrollment.objects.filter(course__in=courses, status='pending').select_related('student', 'course')
    if request.method == 'POST':
        enrollment_id = request.POST.get('enrollment_id')
        action = request.POST.get('action')
        note = request.POST.get('note', '')
        try:
            enrollment = Enrollment.objects.get(id=enrollment_id, status='pending', course__teacher=request.user)
            if action == 'approve':
                enrollment.status = 'approved'
                decision = 'approved'
            elif action == 'deny':
                enrollment.status = 'denied'
                decision = 'denied'
            else:
                decision = None
            enrollment.reviewed_by = request.user
            enrollment.reviewed_at = timezone.now()
            enrollment.note = note
            enrollment.save()
            # Optionally, send email notification to student
            if decision:
                subject = f"Enrollment {decision.title()} for {enrollment.course.name}"
                message = f"Dear {enrollment.student.username},\n\nYour enrollment request for {enrollment.course.name} has been {decision}."
                if note:
                    message += f"\n\nNote from teacher: {note}"
                message += "\n\nThank you."
                send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [enrollment.student.email], fail_silently=True)
        except Enrollment.DoesNotExist:
            pass
        return redirect('teacher_pending_enrollments')
    return render(request, 'courses/teacher_pending_enrollments.html', {'pending': pending})