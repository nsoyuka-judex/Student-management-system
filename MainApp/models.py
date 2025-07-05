from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone
from MainApp.utils.encryption import encrypt_text, decrypt_text
import bleach
from django.core.files.uploadedfile import UploadedFile

ALLOWED_FILE_TYPES = ['application/pdf', 'image/jpeg', 'image/png']
MAX_FILE_SIZE_MB = 5

class User(AbstractUser):
    ROLE_CHOICES = (
        ('student', 'Student'),
        ('teacher', 'Teacher'),
        ('admin', 'Admin'),
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)

    @property
    def is_student(self):
        return self.role == 'student'

    @property
    def is_teacher(self):
        return self.role == 'teacher'

    def __str__(self):
        return f"{self.username} ({self.role})"

    class Meta:
        permissions = [
            ("can_approve_enrollment", "Can approve enrollment requests"),
        ]


class StudentProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, unique=True, related_name='student_profile')
    full_name = models.CharField(max_length=100)
    age = models.PositiveIntegerField()
    contact_number = models.CharField(max_length=20)
    address_encrypted = models.TextField()
    guardian_email = models.EmailField(db_index=True)
    transcript = models.FileField(upload_to='documents/transcripts/', null=True, blank=True)
    id_proof = models.FileField(upload_to='documents/id_proofs/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    profile_picture = models.ImageField(upload_to='profile_pics/', null=True, blank=True)

    class Meta:
        verbose_name = "Student Profile"
        verbose_name_plural = "Student Profiles"

    def __str__(self):
        return self.full_name

    def __repr__(self):
        return f"<StudentProfile {self.full_name} - {self.user.username}>"

    def get_decrypted_address(self):
        try:
            return decrypt_text(self.address_encrypted)
        except Exception:
            return "[Decryption Error]"

    def clean(self):
        # Sanitize and encrypt address
        clean_address = bleach.clean(self.get_decrypted_address())
        self.address_encrypted = encrypt_text(clean_address)

        # Validate file types and sizes
        for file_field in [self.transcript, self.id_proof]:
            # Skip validation if the file is cleared (None or False)
            if not file_field:
                continue
            # Only check content_type if it's an uploaded file
            if hasattr(file_field, 'file') and isinstance(file_field.file, UploadedFile):
                if file_field.file.content_type not in ALLOWED_FILE_TYPES:
                    raise ValidationError("Invalid file type.")
                if file_field.size > MAX_FILE_SIZE_MB * 1024 * 1024:
                    raise ValidationError("File size exceeds limit.")

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)


class TeacherProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, unique=True, related_name='teacher_profile')
    full_name = models.CharField(max_length=100)
    department = models.CharField(max_length=100)
    contact_email = models.EmailField()
    office_location = models.CharField(max_length=100, blank=True)
    bio = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    profile_picture = models.ImageField(upload_to='profile_pics/', null=True, blank=True)

    class Meta:
        verbose_name = "Teacher Profile"
        verbose_name_plural = "Teacher Profiles"

    def __str__(self):
        return self.full_name


class Course(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=20, unique=True)
    description = models.TextField(blank=True)
    prerequisites = models.ManyToManyField('self', blank=True, symmetrical=False)
    teacher = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, limit_choices_to={'role': 'teacher'}, related_name='courses')
    schedule = models.CharField(max_length=100, blank=True)  # e.g., 'Mon 10-12, Wed 10-12'
    capacity = models.PositiveIntegerField(default=30)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.code} - {self.name}"


class Enrollment(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('denied', 'Denied'),
    ]
    student = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={'role': 'student'}, related_name='enrollments')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='enrollments')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    requested_at = models.DateTimeField(auto_now_add=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)
    reviewed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, limit_choices_to={'role': 'admin'}, related_name='reviewed_enrollments')
    note = models.TextField(blank=True)

    class Meta:
        unique_together = ('student', 'course')

    def __str__(self):
        return f"{self.student.username} - {self.course.code} ({self.status})"