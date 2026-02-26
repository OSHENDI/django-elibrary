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
    help = 'Seed the entire database from scratch'

    def handle(self, *args, **options):
        self.stdout.write('Seeding database...')

        SiteSettings.load()

        # --- categories ---
        cats = {}
        for name, icon in [
            ('Fiction', 'fa-feather'),
            ('Science', 'fa-flask'),
            ('History', 'fa-landmark'),
            ('Technology', 'fa-microchip'),
            ('Philosophy', 'fa-brain'),
            ('Biography', 'fa-user-tie'),
            ('Poetry', 'fa-pen-fancy'),
            ('Psychology', 'fa-head-side-virus'),
            ('Business', 'fa-briefcase'),
            ('Self-Help', 'fa-hands-helping'),
        ]:
            c, _ = Category.objects.get_or_create(name=name, defaults={'icon': icon})
            cats[name] = c
        self.stdout.write(f'  {len(cats)} categories')

        # --- authors ---
        auths = {}
        for name, bio in [
            ('George Orwell', 'English novelist known for his sharp criticism of political oppression. He wrote some of the most influential works of the 20th century.'),
            ('Jane Austen', 'English novelist known for her wit and social commentary. Her works explore the lives and manners of the British landed gentry.'),
            ('Isaac Asimov', 'American writer and professor known for his works of science fiction and popular science. He was one of the most prolific writers of all time.'),
            ('Yuval Noah Harari', 'Israeli historian and professor at the Hebrew University of Jerusalem. He is the author of popular science bestsellers.'),
            ('Marcus Aurelius', 'Roman emperor and Stoic philosopher. His personal writings are a significant source of understanding Stoic philosophy.'),
            ('Walter Isaacson', 'American author and journalist known for his biographies of important historical figures.'),
            ('J.R.R. Tolkien', 'English writer and philologist, creator of Middle-earth.'),
            ('Fyodor Dostoevsky', 'Russian novelist and philosopher, master of psychological fiction.'),
            ('F. Scott Fitzgerald', 'American novelist of the Jazz Age.'),
            ('Franz Kafka', 'German-speaking Bohemian novelist known for surreal fiction.'),
            ('Charles Dickens', 'English writer and social critic of the Victorian era.'),
            ('Agatha Christie', 'English writer known as the Queen of Crime.'),
            ('Ernest Hemingway', 'American novelist and journalist, Nobel Prize winner.'),
            ('Albert Camus', 'French philosopher and author, Nobel Prize in Literature.'),
            ('Mary Shelley', 'English novelist who wrote the first science fiction novel.'),
            ('Stephen Hawking', 'English theoretical physicist and cosmologist.'),
            ('Daniel Kahneman', 'Israeli-American psychologist and Nobel laureate in economics.'),
            ('Daniel Goleman', 'American psychologist and science journalist.'),
            ('Angela Duckworth', 'American psychologist known for her research on grit.'),
            ('Robert Greene', 'American author known for books on strategy and power.'),
            ('James Clear', 'American author and speaker focused on habits and decision making.'),
            ('Brene Brown', 'American researcher and storyteller studying courage and vulnerability.'),
            ('Sylvia Plath', 'American poet and novelist known for confessional poetry.'),
            ('Victor Hugo', 'French poet and novelist of the Romantic movement.'),
        ]:
            a, _ = Author.objects.get_or_create(name=name, defaults={'bio': bio})
            auths[name] = a
        self.stdout.write(f'  {len(auths)} authors')

        # --- books ---
        # (title, author, category, year, pages, language, description, total_copies)
        books_data = [
            ('1984', 'George Orwell', 'Fiction', 1949, 328, 'English', 'A dystopian novel set in a totalitarian society ruled by Big Brother. It explores themes of surveillance, truth, and individual freedom.', 5),
            ('Animal Farm', 'George Orwell', 'Fiction', 1945, 112, 'English', 'An allegorical novella reflecting events leading up to the Russian Revolution. A group of farm animals rebel against their human farmer.', 4),
            ('Pride and Prejudice', 'Jane Austen', 'Fiction', 1813, 432, 'English', 'A romantic novel following Elizabeth Bennet as she deals with issues of manners, upbringing, morality and marriage in early 19th-century England.', 4),
            ('Sense and Sensibility', 'Jane Austen', 'Fiction', 1811, 409, 'English', 'The story follows the Dashwood sisters as they navigate love and heartbreak, contrasting emotional and rational temperaments.', 3),
            ('Emma', 'Jane Austen', 'Fiction', 1815, 474, 'English', 'A comedy of manners about the perils of misconstrued romance. Emma Woodhouse is a well-meaning but misguided matchmaker.', 3),
            ('Foundation', 'Isaac Asimov', 'Science', 1951, 244, 'English', 'The first novel in the Foundation series. A mathematician develops a theory to predict the future and tries to save civilization.', 5),
            ('I, Robot', 'Isaac Asimov', 'Technology', 1950, 253, 'English', 'A collection of nine science fiction short stories exploring the interaction of humans and robots through the Three Laws of Robotics.', 4),
            ('The End of Eternity', 'Isaac Asimov', 'Science', 1955, 191, 'English', 'A science fiction novel about an organization that can travel through time and alter reality for the benefit of humanity.', 3),
            ('Sapiens', 'Yuval Noah Harari', 'History', 2011, 443, 'English', 'A brief history of the humankind exploring how Homo sapiens came to dominate the world through cognitive, agricultural and scientific revolutions.', 5),
            ('Homo Deus', 'Yuval Noah Harari', 'Technology', 2016, 449, 'English', 'A look into the future of humanity, exploring the projects, dreams and nightmares that will shape the twenty-first century.', 4),
            ('21 Lessons for the 21st Century', 'Yuval Noah Harari', 'Philosophy', 2018, 372, 'English', 'Addresses the biggest questions of the present moment: What is really happening right now? What are the greatest challenges and choices?', 3),
            ('Meditations', 'Marcus Aurelius', 'Philosophy', 180, 256, 'English', 'A series of personal writings by the Roman Emperor recording his private notes to himself on Stoic philosophy and self-improvement.', 4),
            ('Steve Jobs', 'Walter Isaacson', 'Biography', 2011, 656, 'English', 'The authorized biography of the co-founder of Apple Inc. Based on more than forty interviews with Jobs conducted over two years.', 4),
            ('Einstein: His Life and Universe', 'Walter Isaacson', 'Biography', 2007, 704, 'English', 'A biography of Albert Einstein exploring how his scientific imagination sprang from the rebellious nature of his personality.', 3),
            ('Leonardo da Vinci', 'Walter Isaacson', 'Biography', 2017, 624, 'English', 'A biography based on thousands of pages from Leonardo da Vincis notebooks that reveals the fullest possible picture of the artist.', 4),
            ('The Hobbit', 'J.R.R. Tolkien', 'Fiction', 1937, 310, 'English', 'Bilbo Baggins embarks on an unexpected journey with a company of dwarves to reclaim their homeland from the dragon Smaug.', 3),
            ('Crime and Punishment', 'Fyodor Dostoevsky', 'Fiction', 1866, 671, 'English', 'A young student in St. Petersburg commits a murder and deals with the moral consequences.', 3),
            ('The Great Gatsby', 'F. Scott Fitzgerald', 'Fiction', 1925, 180, 'English', 'A mysterious millionaire pursues an elusive dream in the decadent Jazz Age of 1920s New York.', 3),
            ('The Metamorphosis', 'Franz Kafka', 'Fiction', 1915, 55, 'English', 'Gregor Samsa wakes up one morning to find himself transformed into a giant insect.', 3),
            ('A Tale of Two Cities', 'Charles Dickens', 'Fiction', 1859, 489, 'English', 'A story of love and sacrifice set against the backdrop of the French Revolution.', 3),
            ('Murder on the Orient Express', 'Agatha Christie', 'Fiction', 1934, 274, 'English', 'Detective Hercule Poirot investigates a murder aboard the famous train.', 3),
            ('The Old Man and the Sea', 'Ernest Hemingway', 'Fiction', 1952, 127, 'English', 'An aging fisherman battles a giant marlin in the Gulf Stream.', 3),
            ('The Stranger', 'Albert Camus', 'Fiction', 1942, 123, 'English', 'Meursault, an indifferent French Algerian, becomes involved in a senseless murder.', 3),
            ('Frankenstein', 'Mary Shelley', 'Fiction', 1818, 280, 'English', 'A young scientist creates a sapient creature in an unorthodox experiment.', 3),
            ('A Brief History of Time', 'Stephen Hawking', 'Science', 1988, 256, 'English', 'An exploration of the universe from the Big Bang to black holes, written for non-scientists.', 3),
            ('The Universe in a Nutshell', 'Stephen Hawking', 'Science', 2001, 224, 'English', 'Hawking explores the latest advances in theoretical physics and cosmology.', 3),
            ('Cosmos', 'Isaac Asimov', 'Science', 1980, 365, 'English', 'An exploration of the wonders of the universe through scientific discovery.', 3),
            ('The Innovators', 'Walter Isaacson', 'Technology', 2014, 560, 'English', 'The story of the people who created the computer and the internet.', 3),
            ('The Myth of Sisyphus', 'Albert Camus', 'Philosophy', 1942, 212, 'English', 'Camus introduces the philosophy of the absurd and the question of suicide.', 3),
            ('Thinking, Fast and Slow', 'Daniel Kahneman', 'Psychology', 2011, 499, 'English', 'Explores the two systems that drive the way we think: fast intuitive thinking and slow deliberate thinking.', 3),
            ('Emotional Intelligence', 'Daniel Goleman', 'Psychology', 1995, 352, 'English', 'Why emotional intelligence can matter more than IQ for personal and professional success.', 3),
            ('Grit', 'Angela Duckworth', 'Psychology', 2016, 352, 'English', 'The power of passion and perseverance with why talent alone does not guarantee success.', 3),
            ('The 48 Laws of Power', 'Robert Greene', 'Business', 1998, 452, 'English', 'A guide to gaining and maintaining power drawn from historical figures across 3000 years.', 3),
            ('The Laws of Human Nature', 'Robert Greene', 'Business', 2018, 624, 'English', 'An exploration of the hidden forces that drive human behavior.', 3),
            ('Atomic Habits', 'James Clear', 'Self-Help', 2018, 320, 'English', 'A practical guide to building good habits, breaking bad ones, and getting 1 percent better every day.', 3),
            ('Daring Greatly', 'Brene Brown', 'Self-Help', 2012, 320, 'English', 'How the courage to be vulnerable transforms the way we live, love, parent, and lead.', 3),
            ('The Bell Jar', 'Sylvia Plath', 'Poetry', 1963, 244, 'English', 'A semi-autobiographical novel exploring themes of identity, depression, and societal expectations.', 3),
            ('Les Miserables', 'Victor Hugo', 'Fiction', 1862, 1463, 'English', 'An epic tale of broken dreams, unrequited love, and redemption in 19th-century France.', 3),
        ]

        for title, auth_name, cat_name, year, pages, lang, desc, copies in books_data:
            Book.objects.get_or_create(
                title=title,
                defaults={
                    'author': auths[auth_name],
                    'category': cats[cat_name],
                    'publication_year': year,
                    'pages': pages,
                    'language': lang,
                    'description': desc,
                    'total_copies': copies,
                    'available_copies': copies,
                },
            )
        self.stdout.write(f'  {len(books_data)} books')

        # --- admin ---
        if not User.objects.filter(username='admin').exists():
            admin_user = User.objects.create_superuser('admin', 'admin@elibrary.com', 'admin1234')
            UserProfile.objects.get_or_create(user=admin_user)
            self.stdout.write('  admin user created (admin / admin1234)')

        # --- students ---
        students_data = [
            ('student1', 'Ali', 'Hassan', 'student1@email.com', ''),
            ('student2', 'Sara', 'Ahmed', 'student2@email.com', ''),
            ('ahmada', 'ahmad', 'ali', 'ahmad@mail.com', '0592000012'),
            ('sameh', 'sameh', 'radi', 'sameh@email.com', '0591234123'),
            ('nora_k', 'Nora', 'Khalid', 'nora.khalid@students.edu', '0501234567'),
            ('omar_sy', 'Omar', 'Syed', 'omar.syed@students.edu', '0559876543'),
            ('lina_m', 'Lina', 'Mansour', 'lina.mansour@students.edu', '0541112233'),
            ('youssef_a', 'Youssef', 'Ali', 'youssef.ali@students.edu', '0567778899'),
            ('reem_h', 'Reem', 'Haddad', 'reem.haddad@students.edu', '0533445566'),
            ('khalid_w', 'Khalid', 'Waleed', 'khalid.waleed@students.edu', '0512345678'),
            ('maya_z', 'Maya', 'Zahra', 'maya.zahra@students.edu', '0549998877'),
            ('tariq_n', 'Tariq', 'Nasser', 'tariq.nasser@students.edu', '0556667788'),
            ('hana_b', 'Hana', 'Basim', 'hana.basim@students.edu', '0521231234'),
            ('faisal_r', 'Faisal', 'Rahman', 'faisal.rahman@students.edu', '0534564567'),
        ]

        students = []
        for uname, first, last, email, phone in students_data:
            user, created = User.objects.get_or_create(
                username=uname,
                defaults={'first_name': first, 'last_name': last, 'email': email},
            )
            if created:
                user.set_password('test_123')
                user.date_joined = timezone.now() - timedelta(days=random.randint(10, 90))
                user.save()
            UserProfile.objects.get_or_create(user=user, defaults={'phone': phone})
            students.append(user)
        self.stdout.write(f'  {len(students)} students (password: test_123)')

        # --- borrows and reviews ---
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
        borrow_count = 0
        review_count = 0

        for i, student in enumerate(students):
            if BorrowRecord.objects.filter(user=student).exists():
                continue

            num_borrows = random.randint(2, min(5, len(all_books)))
            picked = random.sample(all_books, num_borrows)

            for book in picked:
                days_ago = random.randint(5, 60)
                borrow_date = timezone.now().date() - timedelta(days=days_ago)

                BorrowRecord.objects.create(
                    user=student,
                    book=book,
                    due_date=borrow_date + timedelta(days=14),
                    is_returned=True,
                    return_date=borrow_date + timedelta(days=random.randint(3, 13)),
                )
                borrow_count += 1

                if random.random() < 0.7:
                    if not Review.objects.filter(user=student, book=book).exists():
                        Review.objects.create(
                            user=student,
                            book=book,
                            rating=random.randint(3, 5),
                            comment=random.choice(review_comments),
                        )
                        review_count += 1

            # first 3 students get an active borrow
            if i < 3:
                remaining = [b for b in all_books if b not in picked and b.available_copies > 0]
                if remaining:
                    active_book = random.choice(remaining)
                    BorrowRecord.objects.create(
                        user=student,
                        book=active_book,
                        due_date=timezone.now().date() + timedelta(days=random.randint(3, 12)),
                        is_returned=False,
                    )
                    active_book.available_copies -= 1
                    active_book.save()
                    borrow_count += 1

        self.stdout.write(f'  {borrow_count} borrows, {review_count} reviews')
        self.stdout.write(self.style.SUCCESS('Done.'))
