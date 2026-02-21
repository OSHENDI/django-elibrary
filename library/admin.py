from django.contrib import admin
from .models import (
    Category, Author, Book, UserProfile,
    BorrowRecord, Review, ContactMessage,
    VisitLog, SiteSettings,
)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'icon', 'book_count']
    search_fields = ['name']
    list_per_page = 20


@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    list_display = ['name', 'book_count']
    search_fields = ['name']
    list_per_page = 20


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ['title', 'author', 'category', 'total_copies', 'available_copies', 'average_rating', 'created_at']
    list_filter = ['category', 'language', 'author']
    search_fields = ['title', 'author__name', 'description']
    list_per_page = 20


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'phone', 'currently_borrowed_count', 'total_borrowed_count']
    search_fields = ['user__username', 'user__email', 'phone']
    list_per_page = 20


@admin.register(BorrowRecord)
class BorrowRecordAdmin(admin.ModelAdmin):
    list_display = ['user', 'book', 'borrow_date', 'due_date', 'return_date', 'is_returned']
    list_filter = ['is_returned', 'borrow_date']
    search_fields = ['user__username', 'book__title']
    list_per_page = 20


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['user', 'book', 'rating', 'created_at']
    list_filter = ['rating']
    search_fields = ['user__username', 'book__title', 'comment']
    list_per_page = 20


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'subject', 'created_at']
    search_fields = ['name', 'email', 'subject', 'message']
    list_per_page = 20


@admin.register(VisitLog)
class VisitLogAdmin(admin.ModelAdmin):
    list_display = ['path', 'method', 'ip_address', 'timestamp']
    list_filter = ['method']
    search_fields = ['path', 'ip_address']
    list_per_page = 50


@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'maintenance_mode']

    # only one settings row should exist
    def has_add_permission(self, request):
        if SiteSettings.objects.exists():
            return False
        return True

    def has_delete_permission(self, request, obj=None):
        return False


admin.site.site_header = 'لوحة تحكم المكتبة'
admin.site.site_title = 'إدارة المكتبة'
admin.site.index_title = 'لوحة التحكم'
