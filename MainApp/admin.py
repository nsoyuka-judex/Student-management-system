from django.contrib import admin
from django.utils.html import format_html
from .models import User, StudentProfile, TeacherProfile, Course, Enrollment


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'role', 'is_active', 'date_joined')
    list_filter = ('role', 'is_active')
    search_fields = ('username', 'email')


@admin.register(StudentProfile)
class StudentProfileAdmin(admin.ModelAdmin):
    list_display = (
        'full_name', 'user', 'age', 'contact_number',
        'guardian_email', 'decrypted_address',
        'transcript_preview', 'id_proof_preview',
        'created_at'
    )
    readonly_fields = ('decrypted_address', 'transcript_preview', 'id_proof_preview')

    def decrypted_address(self, obj):
        return obj.get_decrypted_address()
    decrypted_address.short_description = "Address"

    def transcript_preview(self, obj):
        if obj.transcript and obj.transcript.url.endswith('.pdf'):
            return format_html('<a href="{}" target="_blank">View PDF</a>', obj.transcript.url)
        elif obj.transcript:
            return format_html('<img src="{}" width="100" />', obj.transcript.url)
        return "No file"

    def id_proof_preview(self, obj):
        if obj.id_proof and obj.id_proof.url.endswith('.pdf'):
            return format_html('<a href="{}" target="_blank">View PDF</a>', obj.id_proof.url)
        elif obj.id_proof:
            return format_html('<img src="{}" width="100" />', obj.id_proof.url)
        return "No file"


@admin.register(TeacherProfile)
class TeacherProfileAdmin(admin.ModelAdmin):
    list_display = (
        'full_name', 'user', 'department',
        'contact_email', 'office_location', 'created_at'
    )
    search_fields = ('full_name', 'user__username', 'department')
    list_filter = ('department',)


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'teacher', 'capacity')
    search_fields = ('code', 'name')
    list_filter = ('teacher',)
    filter_horizontal = ('prerequisites',)


@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ('student', 'course', 'status', 'requested_at', 'reviewed_by')
    search_fields = ('student__username', 'course__code')
    list_filter = ('status', 'course')