from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from cloudinary.models import CloudinaryField


# ─────────────────────────────────────────────────────────────
#  Homework / Assignment Models
# ─────────────────────────────────────────────────────────────

class SchoolClass(models.Model):
    """Represents a school class/grade (e.g. Nursery, Kindergarten, Class 1)."""
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)

    class Meta:
        ordering = ['name']
        verbose_name = 'School Class'
        verbose_name_plural = 'School Classes'

    def __str__(self):
        return self.name


class Homework(models.Model):
    """A homework / assignment assigned to a specific class."""
    title = models.CharField(max_length=255)
    description = models.TextField()
    school_class = models.ForeignKey(
        SchoolClass,
        on_delete=models.CASCADE,
        related_name='homework_list',
        verbose_name='Class'
    )
    date_assigned = models.DateField(default=timezone.now)
    due_date = models.DateField(null=True, blank=True, help_text='Leave blank if no specific due date')

    class Meta:
        ordering = ['-date_assigned']
        verbose_name = 'Homework'
        verbose_name_plural = 'Homework Assignments'

    def __str__(self):
        return f"{self.title} ({self.school_class})"

    @property
    def is_overdue(self):
        from datetime import date
        return self.due_date and self.due_date < date.today()


class UserProfile(models.Model):
    """Extends the default User model to store the student's class."""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    school_class = models.ForeignKey(
        SchoolClass,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='students',
        verbose_name='Class'
    )

    def __str__(self):
        return f"{self.user.username}'s Profile"

class Notice(models.Model):
    title = models.CharField(max_length=255)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_important = models.BooleanField(default=False)
    is_popup = models.BooleanField(default=False)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title


class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} - {self.user.username}"


class GalleryCategory(models.Model):
    name = models.CharField(max_length=100)
    
    class Meta:
        verbose_name_plural = "Gallery Categories"

    def __str__(self):
        return self.name


class GalleryImage(models.Model):
    category = models.ForeignKey(GalleryCategory, on_delete=models.CASCADE, related_name='images')
    image = CloudinaryField('image')  # ✅ changed
    caption = models.CharField(max_length=200, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.category.name} - {self.caption or 'Image'}"


class AdmissionApplication(models.Model):
    PROGRAM_CHOICES = [
        ('1', 'Early Years (Age 2-3)'),
        ('2', 'Nursery (Age 3-4)'),
        ('3', 'Kindergarten (Age 4-6)'),
        ('4', 'Day Care (Age 2-6)'),
    ]
    child_name = models.CharField(max_length=150)
    date_of_birth = models.DateField()
    parent_name = models.CharField(max_length=150)
    email = models.EmailField()
    phone = models.CharField(max_length=15)
    program = models.CharField(max_length=1, choices=PROGRAM_CHOICES)
    message = models.TextField(blank=True)
    submitted_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.child_name} - {self.get_program_display()}"


class Event(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    date = models.DateField()
    time = models.TimeField(null=True, blank=True)
    image = CloudinaryField('image', null=True, blank=True)

    class Meta:
        ordering = ['date']

    def __str__(self):
        return self.title
        
    @property
    def is_past(self):
        from datetime import date
        return self.date < date.today()


class Enquiry(models.Model):
    name = models.CharField(max_length=150)
    email = models.EmailField()
    phone = models.CharField(max_length=15)
    message = models.TextField()
    submitted_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Enquiries"

    def __str__(self):
        return f"Enquiry from {self.name}"


class ActivityUpdate(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    image = CloudinaryField('images')
    date = models.DateField(default=timezone.now)

    class Meta:
        verbose_name = "Daily Activity Update"
        verbose_name_plural = "Daily Activity Updates"
        ordering = ['-date']

    def __str__(self):
        return self.title


class VideoEmbed(models.Model):
    title = models.CharField(max_length=200)
    youtube_url = models.URLField(help_text="Full YouTube URL")
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.title
        
    def get_embed_url(self):
        import re
        match = re.search(r'(?:v=|youtu\.be/|embed/|shorts/)([^&?]+)', self.youtube_url)
        if match:
            video_id = match.group(1).replace('/', '')
            return f"https://www.youtube.com/embed/{video_id}"
        return self.youtube_url


class Student(models.Model):
    name = models.CharField(max_length=150)
    age = models.IntegerField()
    program_enrolled = models.CharField(max_length=200)
    parent_name = models.CharField(max_length=150)
    parent_email = models.EmailField(blank=True)
    parent_phone = models.CharField(max_length=20)
    enrolled_date = models.DateField(default=timezone.now)
    photo = CloudinaryField('image', blank=True, null=True)

    def __str__(self):
        return self.name


class Teacher(models.Model):
    name = models.CharField(max_length=150)
    designation = models.CharField(max_length=150)
    bio = models.TextField(blank=True)
    image = CloudinaryField('image')

    def __str__(self):
        return self.name


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """Auto-create a UserProfile when a new User is registered."""
    if created:
        UserProfile.objects.get_or_create(user=instance)


@receiver(post_save, sender=Notice)
def create_notice_notifications(sender, instance, created, **kwargs):
    if created:
        users = User.objects.all()
        notifications = []
        for user in users:
            notifications.append(Notification(
                user=user,
                title=f"New Notice: {instance.title}",
                message=instance.message[:100] + ("..." if len(instance.message) > 100 else ""),
            ))
        Notification.objects.bulk_create(notifications)


@receiver(post_save, sender=AdmissionApplication)
def alert_staff_new_admission(sender, instance, created, **kwargs):
    if created:
        staff_users = User.objects.filter(models.Q(is_staff=True) | models.Q(is_superuser=True))
        notifications = []
        for user in staff_users:
            notifications.append(Notification(
                user=user,
                title="New Admission Application",
                message=f"A new application has been submitted for {instance.child_name}.",
            ))
        Notification.objects.bulk_create(notifications)


@receiver(post_save, sender=Enquiry)
def alert_staff_new_enquiry(sender, instance, created, **kwargs):
    if created:
        staff_users = User.objects.filter(models.Q(is_staff=True) | models.Q(is_superuser=True))
        notifications = []
        for user in staff_users:
            notifications.append(Notification(
                user=user,
                title="New Enquiry Received",
                message=f"Received a new enquiry from {instance.name}.",
            ))
        Notification.objects.bulk_create(notifications)
