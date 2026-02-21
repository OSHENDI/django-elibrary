from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator


class Category(models.Model):
    name = models.CharField(max_length=100, verbose_name='اسم التصنيف')
    icon = models.CharField(max_length=50, default='fa-book', verbose_name='الأيقونة')
    description = models.TextField(blank=True, verbose_name='الوصف')

    class Meta:
        verbose_name = 'تصنيف'
        verbose_name_plural = 'التصنيفات'
        ordering = ['name']

    def __str__(self):
        return self.name

    def book_count(self):
        return self.books.count()


class Author(models.Model):
    name = models.CharField(max_length=200, verbose_name='اسم المؤلف')
    photo = models.FileField(upload_to='authors/', blank=True, null=True, verbose_name='الصورة')
    bio = models.TextField(blank=True, verbose_name='السيرة الذاتية')

    class Meta:
        verbose_name = 'مؤلف'
        verbose_name_plural = 'المؤلفون'
        ordering = ['name']

    def __str__(self):
        return self.name

    def book_count(self):
        return self.books.count()


class Book(models.Model):
    title = models.CharField(max_length=300, verbose_name='عنوان الكتاب')
    author = models.ForeignKey(Author, on_delete=models.CASCADE, related_name='books', verbose_name='المؤلف')
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name='books', verbose_name='التصنيف')
    cover = models.FileField(upload_to='books/', blank=True, null=True, verbose_name='صورة الغلاف')
    description = models.TextField(blank=True, verbose_name='الوصف')
    publication_year = models.PositiveIntegerField(blank=True, null=True, verbose_name='سنة النشر')
    pages = models.PositiveIntegerField(blank=True, null=True, verbose_name='عدد الصفحات')
    language = models.CharField(max_length=50, default='English', verbose_name='اللغة')
    total_copies = models.PositiveIntegerField(default=1, verbose_name='إجمالي النسخ')
    available_copies = models.PositiveIntegerField(default=1, verbose_name='النسخ المتاحة')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاريخ الإضافة')

    class Meta:
        verbose_name = 'كتاب'
        verbose_name_plural = 'الكتب'
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    def is_available(self):
        return self.available_copies > 0

    # calculates the average star rating from all reviews on this book
    def average_rating(self):
        reviews = self.reviews.all()
        if not reviews:
            return 0
        total = sum(r.rating for r in reviews)
        return round(total / reviews.count(), 1)

    def rating_count(self):
        return self.reviews.count()


class UserProfile(models.Model):
    # extends the built in user model with extra fields
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile', verbose_name='المستخدم')
    phone = models.CharField(max_length=20, blank=True, verbose_name='رقم الهاتف')
    profile_picture = models.FileField(upload_to='profiles/', blank=True, null=True, verbose_name='صورة الملف الشخصي')

    class Meta:
        verbose_name = 'ملف شخصي'
        verbose_name_plural = 'الملفات الشخصية'

    def __str__(self):
        return self.user.username

    def currently_borrowed_count(self):
        return BorrowRecord.objects.filter(user=self.user, is_returned=False).count()

    def total_borrowed_count(self):
        return BorrowRecord.objects.filter(user=self.user).count()


class BorrowRecord(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='borrows', verbose_name='المستخدم')
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='borrows', verbose_name='الكتاب')
    borrow_date = models.DateField(auto_now_add=True, verbose_name='تاريخ الاستعارة')
    due_date = models.DateField(verbose_name='تاريخ الإرجاع المتوقع')
    return_date = models.DateField(blank=True, null=True, verbose_name='تاريخ الإرجاع الفعلي')
    is_returned = models.BooleanField(default=False, verbose_name='تم الإرجاع')

    class Meta:
        verbose_name = 'سجل استعارة'
        verbose_name_plural = 'سجلات الاستعارة'
        ordering = ['-borrow_date']

    def __str__(self):
        return f'{self.user.username} - {self.book.title}'

    # checks if the book is past its due date
    def is_overdue(self):
        from django.utils import timezone
        if not self.is_returned and self.due_date < timezone.now().date():
            return True
        return False

    # returns how many days until due date (negative means overdue)
    def days_remaining(self):
        from django.utils import timezone
        if self.is_returned:
            return 0
        delta = self.due_date - timezone.now().date()
        return delta.days


class Review(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews', verbose_name='المستخدم')
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='reviews', verbose_name='الكتاب')
    rating = models.PositiveIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)], verbose_name='التقييم')
    comment = models.TextField(blank=True, verbose_name='التعليق')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاريخ المراجعة')

    class Meta:
        # each user can only review a book once
        unique_together = ('user', 'book')
        verbose_name = 'مراجعة'
        verbose_name_plural = 'المراجعات'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.user.username} - {self.book.title} ({self.rating})'


class ContactMessage(models.Model):
    name = models.CharField(max_length=100, verbose_name='الاسم')
    email = models.EmailField(verbose_name='البريد الإلكتروني')
    subject = models.CharField(max_length=200, verbose_name='الموضوع')
    message = models.TextField(verbose_name='الرسالة')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاريخ الإرسال')

    class Meta:
        verbose_name = 'رسالة تواصل'
        verbose_name_plural = 'رسائل التواصل'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.name} - {self.subject}'


# keeps a record of every page visit for analytics
class VisitLog(models.Model):
    path = models.CharField(max_length=500, verbose_name='المسار')
    method = models.CharField(max_length=10, verbose_name='نوع الطلب')
    ip_address = models.GenericIPAddressField(blank=True, null=True, verbose_name='عنوان IP')
    timestamp = models.DateTimeField(auto_now_add=True, verbose_name='الوقت')

    class Meta:
        verbose_name = 'سجل زيارة'
        verbose_name_plural = 'سجلات الزيارات'
        ordering = ['-timestamp']

    def __str__(self):
        return f'{self.method} {self.path} at {self.timestamp}'


# singleton model so only one settings row exists in the database
class SiteSettings(models.Model):
    maintenance_mode = models.BooleanField(default=False, verbose_name='وضع الصيانة')

    class Meta:
        verbose_name = 'إعدادات الموقع'
        verbose_name_plural = 'إعدادات الموقع'

    def __str__(self):
        status = 'ON' if self.maintenance_mode else 'OFF'
        return f'Maintenance Mode: {status}'

    def save(self, *args, **kwargs):
        # force pk=1 so we never create more than one row
        self.pk = 1
        super().save(*args, **kwargs)

    @classmethod
    def load(cls):
        obj, created = cls.objects.get_or_create(pk=1)
        return obj
