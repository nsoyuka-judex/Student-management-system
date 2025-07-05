import bleach
from django import forms
from django.core.exceptions import ValidationError
from django.contrib.auth.forms import UserCreationForm
from .models import User, StudentProfile, TeacherProfile
from .utils.encryption import encrypt_text, decrypt_text

ALLOWED_FILE_TYPES = ['application/pdf', 'image/jpeg', 'image/png']
MAX_FILE_SIZE_MB = 5


# ----------------------------
# Student Registration Form
# ----------------------------
class StudentRegistrationForm(UserCreationForm):
    full_name = forms.CharField(max_length=100)
    age = forms.IntegerField(min_value=1)
    contact_number = forms.CharField(max_length=20)
    address = forms.CharField(widget=forms.Textarea)
    guardian_email = forms.EmailField()
    transcript = forms.FileField(required=False)
    id_proof = forms.FileField(required=False)

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

    def clean_full_name(self):
        return bleach.clean(self.cleaned_data['full_name'])

    def clean_contact_number(self):
        return bleach.clean(self.cleaned_data['contact_number'])

    def clean_address(self):
        return bleach.clean(self.cleaned_data['address'])

    def clean_guardian_email(self):
        return bleach.clean(self.cleaned_data['guardian_email'])

    def validate_file(self, file, label):
        if file:
            if file.content_type not in ALLOWED_FILE_TYPES:
                raise ValidationError(f"Invalid file type for {label}. Only PDF, JPG, and PNG are allowed.")
            if file.size > MAX_FILE_SIZE_MB * 1024 * 1024:
                raise ValidationError(f"{label} exceeds the {MAX_FILE_SIZE_MB}MB size limit.")
        return file

    def clean_transcript(self):
        return self.validate_file(self.cleaned_data.get('transcript'), "Transcript")

    def clean_id_proof(self):
        return self.validate_file(self.cleaned_data.get('id_proof'), "ID Proof")

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = 'student'
        if commit:
            user.save()
            encrypted_address = encrypt_text(self.cleaned_data['address'])
            StudentProfile.objects.create(
                user=user,
                full_name=self.cleaned_data['full_name'],
                age=self.cleaned_data['age'],
                contact_number=self.cleaned_data['contact_number'],
                address_encrypted=encrypted_address,
                guardian_email=self.cleaned_data['guardian_email'],
                transcript=self.cleaned_data.get('transcript'),
                id_proof=self.cleaned_data.get('id_proof'),
            )
        return user


# ----------------------------
# Teacher Registration Form
# ----------------------------
class TeacherRegistrationForm(UserCreationForm):
    full_name = forms.CharField(max_length=100)
    department = forms.CharField(max_length=100)
    contact_email = forms.EmailField()
    office_location = forms.CharField(max_length=100, required=False)
    bio = forms.CharField(widget=forms.Textarea, required=False)

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

    def clean_full_name(self):
        return bleach.clean(self.cleaned_data['full_name'])

    def clean_department(self):
        return bleach.clean(self.cleaned_data['department'])

    def clean_contact_email(self):
        return bleach.clean(self.cleaned_data['contact_email'])

    def clean_office_location(self):
        return bleach.clean(self.cleaned_data['office_location'])

    def clean_bio(self):
        return bleach.clean(self.cleaned_data['bio'])

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = 'teacher'
        if commit:
            user.save()
            TeacherProfile.objects.create(
                user=user,
                full_name=self.cleaned_data['full_name'],
                department=self.cleaned_data['department'],
                contact_email=self.cleaned_data['contact_email'],
                office_location=self.cleaned_data.get('office_location', ''),
                bio=self.cleaned_data.get('bio', ''),
            )
        return user

class StudentProfileForm(forms.ModelForm):
    address = forms.CharField(widget=forms.Textarea)
    profile_picture = forms.ImageField(required=False)
    transcript = forms.FileField(required=False)
    id_proof = forms.FileField(required=False)

    class Meta:
        model = StudentProfile
        fields = ['full_name', 'age', 'contact_number', 'guardian_email', 'address', 'transcript', 'id_proof', 'profile_picture']

    def __init__(self, *args, **kwargs):
        instance = kwargs.get('instance')
        if instance:
            initial = kwargs.setdefault('initial', {})
            initial['address'] = decrypt_text(instance.address_encrypted)
        super().__init__(*args, **kwargs)

    def clean_address(self):
        return bleach.clean(self.cleaned_data['address'])

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.address_encrypted = encrypt_text(self.cleaned_data['address'])
        if commit:
            instance.save()
        return instance


class TeacherProfileForm(forms.ModelForm):
    profile_picture = forms.ImageField(required=False)

    class Meta:
        model = TeacherProfile
        fields = ['full_name', 'department', 'contact_email', 'office_location', 'bio', 'profile_picture']

    def clean(self):
        cleaned = super().clean()
        for field in ['full_name', 'department', 'contact_email', 'office_location', 'bio']:
            if field in cleaned:
                cleaned[field] = bleach.clean(cleaned[field])
        return cleaned