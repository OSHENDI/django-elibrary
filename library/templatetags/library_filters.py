from django import template
from django.utils.safestring import mark_safe

register = template.Library()


# badge showing if the book has copies left
@register.filter(name='book_status')
def book_status(book):
    if book.available_copies > 0:
        return mark_safe('<span class="badge bg-available">Available</span>')
    return mark_safe('<span class="badge bg-borrowed">Fully Borrowed</span>')


# turns a number like 3.5 into filled and empty star icons
@register.filter(name='star_rating')
def star_rating(value):
    try:
        val = float(value)
    except (ValueError, TypeError):
        val = 0

    full = int(val)
    half = 1 if val - full >= 0.5 else 0
    empty = 5 - full - half

    stars = ''
    for i in range(full):
        stars += '<i class="fas fa-star star-filled"></i>'
    if half:
        stars += '<i class="fas fa-star-half-alt star-filled"></i>'
    for i in range(empty):
        stars += '<i class="far fa-star star-empty"></i>'

    return mark_safe(stars)
