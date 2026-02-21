import random
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from library.models import (
    Category, Author, Book, UserProfile,
    BorrowRecord, Review, SiteSettings,
)
from django.utils import timezone
from datetime import timedelta


class Command(BaseCommand):
    help = 'Populate database with sample library data'

    def handle(self, *args, **options):
        self.stdout.write('Creating sample data...')

        # site settings
        SiteSettings.load()

        # categories
        categories_data = [
            ('Fiction', 'fa-feather'),
            ('Science', 'fa-flask'),
            ('History', 'fa-landmark'),
            ('Technology', 'fa-microchip'),
            ('Philosophy', 'fa-brain'),
            ('Biography', 'fa-user-tie'),
            ('Poetry', 'fa-pen-fancy'),
        ]
        categories = {}
        for name, icon in categories_data:
            cat, _ = Category.objects.get_or_create(name=name, defaults={'icon': icon})
            categories[name] = cat

        # authors
        authors_data = [
            ('George Orwell', 'English novelist known for his sharp criticism of political oppression. He wrote some of the most influential works of the 20th century.'),
            ('Jane Austen', 'English novelist known for her wit and social commentary. Her works explore the lives and manners of the British landed gentry.'),
            ('Isaac Asimov', 'American writer and professor known for his works of science fiction and popular science. He was one of the most prolific writers of all time.'),
            ('Yuval Noah Harari', 'Israeli historian and professor at the Hebrew University of Jerusalem. He is the author of popular science bestsellers.'),
            ('Marcus Aurelius', 'Roman emperor and Stoic philosopher. His personal writings are a significant source of understanding Stoic philosophy.'),
            ('Walter Isaacson', 'American author and journalist known for his biographies of important historical figures.'),
        ]
        authors = {}
        for name, bio in authors_data:
            auth, _ = Author.objects.get_or_create(name=name, defaults={'bio': bio})
            authors[name] = auth

        # books
        books_data = [
            ('1984', 'George Orwell', 'Fiction', 1949, 328, 'English',
             'A dystopian novel set in a totalitarian society ruled by Big Brother. It explores themes of surveillance, truth, and individual freedom.', 5),
            ('Animal Farm', 'George Orwell', 'Fiction', 1945, 112, 'English',
             'An allegorical novella reflecting events leading up to the Russian Revolution. A group of farm animals rebel against their human farmer.', 4),
            ('Pride and Prejudice', 'Jane Austen', 'Fiction', 1813, 432, 'English',
             'A romantic novel following Elizabeth Bennet as she deals with issues of manners, upbringing, morality and marriage in early 19th-century England.', 4),
            ('Sense and Sensibility', 'Jane Austen', 'Fiction', 1811, 409, 'English',
             'The story follows the Dashwood sisters as they navigate love and heartbreak, contrasting emotional and rational temperaments.', 3),
            ('Emma', 'Jane Austen', 'Fiction', 1815, 474, 'English',
             'A comedy of manners about the perils of misconstrued romance. Emma Woodhouse is a well-meaning but misguided matchmaker.', 3),
            ('Foundation', 'Isaac Asimov', 'Science', 1951, 244, 'English',
             'The first novel in the Foundation series. A mathematician develops a theory to predict the future and tries to save civilization.', 5),
            ('I, Robot', 'Isaac Asimov', 'Technology', 1950, 253, 'English',
             'A collection of nine science fiction short stories exploring the interaction of humans and robots through the Three Laws of Robotics.', 4),
            ('The End of Eternity', 'Isaac Asimov', 'Science', 1955, 191, 'English',
             'A science fiction novel about an organization that can travel through time and alter reality for the benefit of humanity.', 3),
            ('Sapiens', 'Yuval Noah Harari', 'History', 2011, 443, 'English',
             'A brief history of humankind exploring how Homo sapiens came to dominate the world through cognitive, agricultural and scientific revolutions.', 5),
            ('Homo Deus', 'Yuval Noah Harari', 'Technology', 2016, 449, 'English',
             'A look into the future of humanity, exploring the projects, dreams and nightmares that will shape the twenty-first century.', 4),
            ('21 Lessons for the 21st Century', 'Yuval Noah Harari', 'Philosophy', 2018, 372, 'English',
             'Addresses the biggest questions of the present moment: What is really happening right now? What are the greatest challenges and choices?', 3),
            ('Meditations', 'Marcus Aurelius', 'Philosophy', 180, 256, 'English',
             'A series of personal writings by the Roman Emperor recording his private notes to himself on Stoic philosophy and self-improvement.', 4),
            ('Steve Jobs', 'Walter Isaacson', 'Biography', 2011, 656, 'English',
             'The authorized biography of the co-founder of Apple Inc. Based on more than forty interviews with Jobs conducted over two years.', 4),
            ('Einstein: His Life and Universe', 'Walter Isaacson', 'Biography', 2007, 704, 'English',
             'A biography of Albert Einstein exploring how his scientific imagination sprang from the rebellious nature of his personality.', 3),
            ('Leonardo da Vinci', 'Walter Isaacson', 'Biography', 2017, 624, 'English',
             'A biography based on thousands of pages from Leonardo da Vincis notebooks that reveals the fullest possible picture of the artist.', 4),
        ]

        for title, author_name, cat_name, year, pages, lang, desc, copies in books_data:
            Book.objects.get_or_create(
                title=title,
                defaults={
                    'author': authors[author_name],
                    'category': categories[cat_name],
                    'publication_year': year,
                    'pages': pages,
                    'language': lang,
                    'description': desc,
                    'total_copies': copies,
                    'available_copies': copies,
                },
            )

        # admin user
        if not User.objects.filter(username='admin').exists():
            admin_user = User.objects.create_superuser('admin', 'admin@elibrary.com', 'admin1234')
            UserProfile.objects.get_or_create(user=admin_user)

        # student users
        students = []
        student_data = [
            ('student1', 'Ali', 'Hassan', 'student1@email.com'),
            ('student2', 'Sara', 'Ahmed', 'student2@email.com'),
        ]
        for uname, first, last, email in student_data:
            user, created = User.objects.get_or_create(
                username=uname,
                defaults={
                    'first_name': first,
                    'last_name': last,
                    'email': email,
                },
            )
            if created:
                user.set_password('pass1234')
                user.save()
            UserProfile.objects.get_or_create(user=user)
            students.append(user)

        # sample borrows and reviews
        all_books = list(Book.objects.all())
        for student in students:
            # borrow 2 random books
            picked = random.sample(all_books, min(2, len(all_books)))
            for book in picked:
                if not BorrowRecord.objects.filter(user=student, book=book).exists():
                    record = BorrowRecord.objects.create(
                        user=student,
                        book=book,
                        due_date=timezone.now().date() + timedelta(days=14),
                        is_returned=True,
                        return_date=timezone.now().date(),
                    )
                    # add a review
                    if not Review.objects.filter(user=student, book=book).exists():
                        Review.objects.create(
                            user=student,
                            book=book,
                            rating=random.randint(3, 5),
                            comment=random.choice([
                                'Great read, highly recommended.',
                                'Very informative and well written.',
                                'Enjoyed it from start to finish.',
                                'A solid book, worth the time.',
                                'Interesting perspective on the topic.',
                            ]),
                        )

        self.stdout.write(self.style.SUCCESS('Sample data created successfully.'))
