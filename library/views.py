from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Avg, Q
from django.utils import timezone
from datetime import timedelta

from .models import Book, Author, Category, BorrowRecord, Review, UserProfile
from .forms import RegistrationForm, LoginForm, ContactForm, ReviewForm, ProfileEditForm


def home(request):
    recent_books = Book.objects.all()[:6]

    # grab the top 3 books that actually have reviews
    top_books = Book.objects.annotate(
        avg_rating=Avg('reviews__rating')
    ).filter(avg_rating__isnull=False).order_by('-avg_rating')[:3]

    stats = {
        'book_count': Book.objects.count(),
        'author_count': Author.objects.count(),
        'student_count': User.objects.filter(is_staff=False).count(),
    }

    return render(request, 'home.html', {
        'recent_books': recent_books,
        'top_books': top_books,
        'stats': stats,
    })


def book_list(request):
    books = Book.objects.all()

    # search by title or author name
    query = request.GET.get('q', '')
    if query:
        books = books.filter(
            Q(title__icontains=query) | Q(author__name__icontains=query)
        )

    # filter by category from dropdown
    category_id = request.GET.get('category', '')
    selected_category = None
    if category_id:
        books = books.filter(category_id=category_id)
        try:
            selected_category = int(category_id)
        except (ValueError, TypeError):
            selected_category = None

    # sort options from the sort dropdown
    sort = request.GET.get('sort', 'newest')
    if sort == 'oldest':
        books = books.order_by('created_at')
    elif sort == 'rating':
        books = books.annotate(avg_rating=Avg('reviews__rating')).order_by('-avg_rating')
    else:
        books = books.order_by('-created_at')

    paginator = Paginator(books, 9)
    page_num = request.GET.get('page', 1)
    page = paginator.get_page(page_num)

    categories = Category.objects.all()

    return render(request, 'book_list.html', {
        'page': page,
        'categories': categories,
        'query': query,
        'selected_category': selected_category,
        'selected_sort': sort,
    })


def book_detail(request, id):
    book = get_object_or_404(Book, id=id)
    reviews = book.reviews.all()

    # figure out what this user has done with this book so we can
    # show the right buttons on the page
    user_has_borrowed = False
    user_currently_borrowing = False
    user_has_reviewed = False

    if request.user.is_authenticated:
        user_has_borrowed = BorrowRecord.objects.filter(
            user=request.user, book=book
        ).exists()
        user_currently_borrowing = BorrowRecord.objects.filter(
            user=request.user, book=book, is_returned=False
        ).exists()
        user_has_reviewed = Review.objects.filter(
            user=request.user, book=book
        ).exists()

    return render(request, 'book_detail.html', {
        'book': book,
        'reviews': reviews,
        'user_has_borrowed': user_has_borrowed,
        'user_currently_borrowing': user_currently_borrowing,
        'user_has_reviewed': user_has_reviewed,
    })


def category_list(request):
    categories = Category.objects.all()
    return render(request, 'category_list.html', {'categories': categories})


def category_books(request, id):
    category = get_object_or_404(Category, id=id)
    books = Book.objects.filter(category=category)
    return render(request, 'category_books.html', {
        'category': category,
        'books': books,
    })


def author_list(request):
    authors = Author.objects.all()
    return render(request, 'author_list.html', {'authors': authors})


def author_detail(request, id):
    author = get_object_or_404(Author, id=id)
    books = Book.objects.filter(author=author)
    return render(request, 'author_detail.html', {
        'author': author,
        'books': books,
    })


def contact_us(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your message has been sent. Thank you!')
            return redirect('contact')
    else:
        form = ContactForm()

    return render(request, 'contact.html', {'form': form})


def register_view(request):
    # no need to show register page if already logged in
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = User.objects.create_user(
                username=form.cleaned_data['username'],
                email=form.cleaned_data['email'],
                password=form.cleaned_data['password'],
            )
            # split the full name into first and last
            names = form.cleaned_data['full_name'].split(' ', 1)
            user.first_name = names[0]
            if len(names) > 1:
                user.last_name = names[1]
            user.save()

            UserProfile.objects.create(
                user=user,
                phone=form.cleaned_data.get('phone', ''),
            )

            messages.success(request, 'Account created. You can now log in.')
            return redirect('login')
    else:
        form = RegistrationForm()

    return render(request, 'register.html', {'form': form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            remember = form.cleaned_data.get('remember_me', False)

            user = authenticate(request, username=username, password=password)
            if user is None:
                # maybe they typed their email instead of username
                try:
                    user_obj = User.objects.get(email=username)
                    user = authenticate(request, username=user_obj.username, password=password)
                except User.DoesNotExist:
                    user = None

            if user is not None:
                login(request, user)
                # if they didnt check remember me the session dies when browser closes
                if not remember:
                    request.session.set_expiry(0)
                messages.success(request, f'Welcome back, {user.first_name or user.username}!')
                return redirect('home')
            else:
                messages.error(request, 'Invalid username or password.')
    else:
        form = LoginForm()

    return render(request, 'login.html', {'form': form})


def logout_view(request):
    logout(request)
    messages.success(request, 'You have been logged out.')
    return redirect('home')


@login_required
def profile_view(request):
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    return render(request, 'profile.html', {'profile': profile})


@login_required
def edit_profile(request):
    profile, created = UserProfile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        form = ProfileEditForm(request.POST, request.FILES)
        if form.is_valid():
            user = request.user
            names = form.cleaned_data['full_name'].split(' ', 1)
            user.first_name = names[0]
            user.last_name = names[1] if len(names) > 1 else ''
            user.email = form.cleaned_data['email']
            if form.cleaned_data.get('new_password'):
                user.set_password(form.cleaned_data['new_password'])
            user.save()

            profile.phone = form.cleaned_data.get('phone', '')
            if form.cleaned_data.get('profile_picture'):
                profile.profile_picture = form.cleaned_data['profile_picture']
            profile.save()

            # if password was changed we need to re login so the session stays valid
            if form.cleaned_data.get('new_password'):
                login(request, user)

            messages.success(request, 'Profile updated.')
            return redirect('profile')
    else:
        form = ProfileEditForm(initial={
            'full_name': request.user.get_full_name(),
            'email': request.user.email,
            'phone': profile.phone,
        })

    return render(request, 'edit_profile.html', {'form': form, 'profile': profile})


@login_required
def borrow_book(request, book_id):
    book = get_object_or_404(Book, id=book_id)

    if not book.is_available():
        messages.error(request, 'This book has no available copies right now.')
        return redirect('book_detail', id=book.id)

    # make sure they dont already have this book out
    already_borrowing = BorrowRecord.objects.filter(
        user=request.user, book=book, is_returned=False
    ).exists()
    if already_borrowing:
        messages.error(request, 'You already have this book borrowed.')
        return redirect('book_detail', id=book.id)

    # students can only have 5 books at a time
    active_borrows = BorrowRecord.objects.filter(user=request.user, is_returned=False).count()
    if active_borrows >= 5:
        messages.error(request, 'You have reached the maximum of 5 borrowed books.')
        return redirect('book_detail', id=book.id)

    if request.method == 'POST':
        due = timezone.now().date() + timedelta(days=14)
        BorrowRecord.objects.create(
            user=request.user,
            book=book,
            due_date=due,
        )
        # decrease available copies since the book is now borrowed
        book.available_copies -= 1
        book.save()
        messages.success(request, f'You have borrowed "{book.title}". Due date: {due}.')
        return redirect('my_books')

    return render(request, 'borrow_book.html', {'book': book})


@login_required
def return_book(request, record_id):
    record = get_object_or_404(BorrowRecord, id=record_id, user=request.user)

    if record.is_returned:
        messages.error(request, 'This book has already been returned.')
        return redirect('my_books')

    record.is_returned = True
    record.return_date = timezone.now().date()
    record.save()

    # give the copy back to the available pool
    book = record.book
    book.available_copies += 1
    book.save()

    messages.success(request, f'You have returned "{book.title}".')
    return redirect('my_books')


@login_required
def my_books(request):
    records = BorrowRecord.objects.filter(user=request.user, is_returned=False)
    return render(request, 'my_books.html', {'records': records})


@login_required
def add_review(request, id):
    book = get_object_or_404(Book, id=id)

    # only people who have borrowed this book can review it
    has_borrowed = BorrowRecord.objects.filter(user=request.user, book=book).exists()
    if not has_borrowed:
        messages.error(request, 'You can only review books you have borrowed.')
        return redirect('book_detail', id=book.id)

    # one review per person per book
    already_reviewed = Review.objects.filter(user=request.user, book=book).exists()
    if already_reviewed:
        messages.error(request, 'You have already reviewed this book.')
        return redirect('book_detail', id=book.id)

    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.user = request.user
            review.book = book
            review.save()
            messages.success(request, 'Your review has been added.')
            return redirect('book_detail', id=book.id)
    else:
        form = ReviewForm()

    return render(request, 'add_review.html', {'form': form, 'book': book})
