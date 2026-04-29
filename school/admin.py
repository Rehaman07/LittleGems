from django.contrib import admin
from django.conf import settings
from .models import (
    Notice, Notification, GalleryCategory, GalleryImage,
    AdmissionApplication, Event, Enquiry,
    ActivityUpdate, VideoEmbed, Student, Teacher,
    SchoolClass, Homework, UserProfile,
)

# ─────────────────────────────────────────────────────────────
#  Admin Site Branding
# ─────────────────────────────────────────────────────────────
admin.site.site_header = "Little Steps International Pre School"
admin.site.site_title = "Little Steps Admin"
admin.site.index_title = "School Management Panel"


# ─────────────────────────────────────────────────────────────
#  Custom Admin Actions
# ─────────────────────────────────────────────────────────────



# ─────────────────────────────────────────────────────────────
#  Homework Admin
# ─────────────────────────────────────────────────────────────

class HomeworkInline(admin.TabularInline):
    model = Homework
    extra = 1
    fields = ('title', 'description', 'date_assigned', 'due_date')
    show_change_link = True


@admin.register(SchoolClass)
class SchoolClassAdmin(admin.ModelAdmin):
    list_display = ('name', 'homework_count', 'description')
    search_fields = ('name',)
    inlines = [HomeworkInline]

    @admin.display(description='Homework Count')
    def homework_count(self, obj):
        return obj.homework_list.count()


@admin.register(Homework)
class HomeworkAdmin(admin.ModelAdmin):
    list_display = ('title', 'school_class', 'date_assigned', 'due_date', 'is_overdue_display')
    list_filter = ('school_class', 'date_assigned', 'due_date')
    search_fields = ('title', 'description')
    date_hierarchy = 'date_assigned'
    ordering = ['-date_assigned']

    @admin.display(description='Overdue?', boolean=True)
    def is_overdue_display(self, obj):
        return obj.is_overdue


class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'Class Assignment'
    fields = ('school_class',)


from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User

admin.site.unregister(User)


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    inlines = [UserProfileInline]


# ─────────────────────────────────────────────────────────────
#  Model Admin Registrations
# ─────────────────────────────────────────────────────────────

@admin.register(Notice)
class NoticeAdmin(admin.ModelAdmin):
    list_display = ('title', 'created_at', 'is_important', 'is_popup')
    list_filter = ('is_important', 'is_popup', 'created_at')
    search_fields = ('title', 'message')
    list_editable = ('is_important', 'is_popup')


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'is_read', 'created_at')
    list_filter = ('is_read', 'created_at')
    search_fields = ('title', 'message', 'user__username')


class GalleryImageInline(admin.TabularInline):
    model = GalleryImage
    extra = 2


@admin.register(GalleryCategory)
class GalleryCategoryAdmin(admin.ModelAdmin):
    inlines = [GalleryImageInline]
    search_fields = ('name',)


@admin.register(GalleryImage)
class GalleryImageAdmin(admin.ModelAdmin):
    list_display = ('caption', 'category', 'created_at')
    list_filter = ('category',)


@admin.register(AdmissionApplication)
class AdmissionApplicationAdmin(admin.ModelAdmin):
    list_display = ('child_name', 'get_program_display_label', 'parent_name', 'phone', 'email', 'submitted_at')
    list_filter = ('program', 'submitted_at')
    search_fields = ('child_name', 'parent_name', 'email', 'phone')
    readonly_fields = ('submitted_at',)

    @admin.display(description='Program')
    def get_program_display_label(self, obj):
        return obj.get_program_display()


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('title', 'date', 'time')
    list_filter = ('date',)
    search_fields = ('title', 'description')


@admin.register(Enquiry)
class EnquiryAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'phone', 'submitted_at')
    list_filter = ('submitted_at',)
    search_fields = ('name', 'email', 'message')
    readonly_fields = ('submitted_at',)


@admin.register(ActivityUpdate)
class ActivityUpdateAdmin(admin.ModelAdmin):
    list_display = ('title', 'date')
    list_filter = ('date',)
    search_fields = ('title', 'content')


@admin.register(VideoEmbed)
class VideoEmbedAdmin(admin.ModelAdmin):
    list_display = ('title', 'is_active')
    list_filter = ('is_active',)
    list_editable = ('is_active',)


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ('name', 'age', 'program_enrolled', 'parent_name', 'parent_phone', 'enrolled_date')
    list_filter = ('program_enrolled', 'enrolled_date')
    search_fields = ('name', 'parent_name', 'parent_email')


@admin.register(Teacher)
class TeacherAdmin(admin.ModelAdmin):
    list_display = ('name', 'designation')
    search_fields = ('name', 'designation')
