import random
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from library.models import Book, UserProfile, BorrowRecord, Review
from django.utils import timezone
from datetime import timedelta


class Command(BaseCommand):
    help = 'Add realistic student accounts with borrow history and reviews'

    def handle(self, *args, **options):
        students_data = [
            ('nora_k', 'Nora', 'Khalid', 'nora.khalid@students.edu'),
            ('omar_sy', 'Omar', 'Syed', 'omar.syed@students.edu'),
            ('lina_m', 'Lina', 'Mansour', 'lina.mansour@students.edu'),
            ('youssef_a', 'Youssef', 'Ali', 'youssef.ali@students.edu'),
            ('reem_h', 'Reem', 'Haddad', 'reem.haddad@students.edu'),
            ('khalid_w', 'Khalid', 'Waleed', 'khalid.waleed@students.edu'),
            ('maya_z', 'Maya', 'Zahra', 'maya.zahra@students.edu'),
            ('tariq_n', 'Tariq', 'Nasser', 'tariq.nasser@students.edu'),
            ('hana_b', 'Hana', 'Basim', 'hana.basim@students.edu'),
            ('faisal_r', 'Faisal', 'Rahman', 'faisal.rahman@students.edu'),
        ]

        phones = [
            '0501234567', '0559876543', '0541112233',
            '0567778899', '0533445566', '0512345678',
            '0549998877', '0556667788', '0521231234', '0534564567',
        ]

        review_comments = [
            'Really enjoyed this one, finished it in two days.',
            'Well written and easy to follow. Highly recommend.',
            'Changed the way I think about the subject entirely.',
            'Solid read. Some chapters were better than others.',
            'Couldn\'t put it down. One of the best I\'ve read this year.',
            'Good content but the pacing felt slow in parts.',
            'Insightful and thought-provoking. Will read again.',
            'A must-read for anyone interested in this topic.',
            'Beautifully written, the author has a great voice.',
            'Interesting concepts but could have been more concise.',
            'Loved the examples and real-world applications.',
            'This book completely exceeded my expectations.',
            'Not what I expected but pleasantly surprised.',
            'The writing style made complex ideas very accessible.',
            'A great addition to the library. Worth borrowing.',
        ]

        all_books = list(Book.objects.all())
        if not all_books:
            self.stdout.write(self.style.ERROR('No books in database. Run seed_data first.'))
            return

        created_count = 0

        for i, (uname, first, last, email) in enumerate(students_data):
            # skip if already exists
            if User.objects.filter(username=uname).exists():
                self.stdout.write(f'  {uname} already exists, skipping')
                continue

            user = User.objects.create_user(
                username=uname,
                email=email,
                password='student123',
                first_name=first,
                last_name=last,
            )

            # stagger join dates so it looks organic
            user.date_joined = timezone.now() - timedelta(days=random.randint(10, 90))
            user.save()

            UserProfile.objects.create(user=user, phone=phones[i])
            created_count += 1

            # each student borrows 2-5 books (returned) and leaves reviews
            num_borrows = random.randint(2, min(5, len(all_books)))
            borrowed_books = random.sample(all_books, num_borrows)

            for book in borrowed_books:
                borrow_days_ago = random.randint(5, 60)
                borrow_date = timezone.now().date() - timedelta(days=borrow_days_ago)
                return_date = borrow_date + timedelta(days=random.randint(3, 13))

                BorrowRecord.objects.create(
                    user=user,
                    book=book,
                    due_date=borrow_date + timedelta(days=14),
                    is_returned=True,
                    return_date=return_date,
                )

                # 70% chance of leaving a review
                if random.random() < 0.7:
                    if not Review.objects.filter(user=user, book=book).exists():
                        Review.objects.create(
                            user=user,
                            book=book,
                            rating=random.randint(3, 5),
                            comment=random.choice(review_comments),
                        )

            # give 1-2 students an active borrow (not returned)
            if i < 3:
                active_book = random.choice([b for b in all_books if b not in borrowed_books])
                if active_book.available_copies > 0:
                    BorrowRecord.objects.create(
                        user=user,
                        book=active_book,
                        due_date=timezone.now().date() + timedelta(days=random.randint(3, 12)),
                        is_returned=False,
                    )
                    active_book.available_copies -= 1
                    active_book.save()

        self.stdout.write(self.style.SUCCESS(
            f'Done. Created {created_count} students with borrow history and reviews.'
        ))
