from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse, FileResponse, Http404
from .models import Book
from .forms import BookForm
import PyPDF2
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import os
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.utils.encoding import smart_str
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.models import Group



def logout_view(request):
    logout(request)
    return redirect('login')

def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('dashboard')
        else:
            messages.error(request, "Invalid username or password")
    return render(request, 'compare/login.html')


@login_required
@user_passes_test(lambda u: u.is_superuser)
def register_user(request):
    form = UserCreationForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = form.save()
        role = request.POST.get('role')

        if role:
            group, created = Group.objects.get_or_create(name=role)
            user.groups.add(group)

        messages.success(request, "User created successfully.")
        return redirect('dashboard')

    return render(request, 'compare/register_user.html', {'form': form})


def get_user_role(user):
    if user.is_superuser:
        return 'Admin'
    elif user.groups.filter(name='Supervisor').exists():
        return 'Supervisor'
    else:
        return 'Student'

@login_required
@user_passes_test(lambda u: u.is_superuser)
def users_list(request):
    users = User.objects.all()
    return render(request, 'compare/users_list.html', {'users': users})

# ✅ Only allow PDF
def read_pdf(file):
    try:
        reader = PyPDF2.PdfReader(file)
        text = ""
        for page in reader.pages:
            extracted_text = page.extract_text()
            if extracted_text:
                text += extracted_text
        return text
    except Exception as e:
        return f"Error extracting PDF content: {str(e)}"

# ✅ Removed DOCX logic - accept only PDF
def extract_file_content(file):
    ext = file.name.split('.')[-1].lower()
    if ext == 'pdf':
        return read_pdf(file)
    else:
        return None

def calculate_similarity(text1, text2):
    try:
        tfidf_vectorizer = TfidfVectorizer(stop_words='english')
        tfidf_matrix = tfidf_vectorizer.fit_transform([text1, text2])
        similarity_matrix = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])
        return similarity_matrix[0][0]
    except Exception as e:
        print(f"Error calculating similarity: {str(e)}")
        return 0.0

def check_title(request):
    message = ''
    if request.method == 'POST':
        title = request.POST.get('title')
        normalized_title = title.strip().lower()
        books = Book.objects.filter(book_title__icontains=title)
        matched_books = [book for book in books if book.book_title.strip().lower() == normalized_title]
        if matched_books:
            matched_book = matched_books[0]
            message = f"Your title '{title}' is already covered in the book '{matched_book.book_title}' by {matched_book.authors}."
        else:
            message = f"No books found matching the title '{title}'."
    return render(request, 'compare/check_title.html', {'message': message})

# ✅ View only PDF files
def view_book_file(request, book_id):
    try:
        book = Book.objects.get(book_id=book_id)
        file_path = book.file.path
        ext = book.file.name.split('.')[-1].lower()

        if ext == 'pdf':
            # View PDF inline
            response = FileResponse(open(file_path, 'rb'), content_type='application/pdf')
            response['Content-Disposition'] = f'inline; filename="{smart_str(book.file.name)}"'
            return response
        elif ext in ['doc', 'docx']:
            # Download Word document
            response = FileResponse(open(file_path, 'rb'), content_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document')
            response['Content-Disposition'] = f'attachment; filename="{smart_str(book.file.name)}"'
            return response
        else:
            raise Http404("Unsupported file type.")
    except Book.DoesNotExist:
        raise Http404("Book not found.")
    except Exception as e:
        raise Http404(f"Error loading file: {e}")

def compare_uploaded_books(request):
    if request.method == 'POST' and request.FILES.get('file1'):
        file1 = request.FILES['file1']
        uploaded_content = extract_file_content(file1)
        if not uploaded_content:
            return render(request, 'compare/compare_result.html', {
                'message': 'Failed to extract content. Unsupported file type or empty content.'
            })
        file_name = os.path.splitext(file1.name)[0].strip().lower()
        books = Book.objects.all()
        matched_book = None
        for book in books:
            if file_name == book.book_title.strip().lower():
                matched_book = book
                break
        if matched_book:
            matched_file_content = extract_file_content(matched_book.file)
            if matched_file_content:
                similarity = calculate_similarity(uploaded_content, matched_file_content)
                eligibility_message = "Your book is eligible."
                if similarity > 0.20:
                    eligibility_message = "Your book is not eligible due to high similarity."
                return render(request, 'compare/compare_result.html', {
                    'most_similar_book': matched_book,
                    'similarity_percentage': round(similarity * 100, 2),
                    'eligibility_message': eligibility_message
                })
        highest_similarity = 0
        most_similar_book = None
        for book in books:
            if book.file:
                book_content = extract_file_content(book.file)
                if book_content:
                    similarity = calculate_similarity(uploaded_content, book_content)
                    if similarity > highest_similarity:
                        highest_similarity = similarity
                        most_similar_book = book
        eligibility_message = "Your book is eligible."
        if highest_similarity > 0.20:
            eligibility_message = "Your book is not eligible due to high similarity."
        return render(request, 'compare/compare_result.html', {
            'most_similar_book': most_similar_book,
            'similarity_percentage': round(highest_similarity * 100, 2),
            'eligibility_message': eligibility_message
        })
    return redirect('index')

@login_required
def dashboard(request):
    role = get_user_role(request.user)
    return render(request, 'compare/dashboard.html', {'role': role})


def index(request):
    return render(request, 'compare/index.html')

def books_list(request):
    books = Book.objects.all()
    return render(request, 'compare/book_list.html', {'books': books})

def add_or_edit_book(request, book_id=None):
    book = get_object_or_404(Book, book_id=book_id) if book_id else None
    form = BookForm(request.POST or None, request.FILES or None, instance=book)
    if request.method == 'POST' and form.is_valid():
        form.save()
        return redirect('books_list')
    return render(request, 'compare/registration.html', {'form': form})

def delete_book(request, book_id):
    book = get_object_or_404(Book, book_id=book_id)
    if request.method == 'POST':
        book.delete()
        return redirect('books_list')
    return render(request, 'compare/delete_book.html', {'book': book})

# ✅ Allow only PDF in AJAX uploads
def handle_uploaded_file(request):
    if request.method == 'POST' and request.FILES.get('file'):
        file = request.FILES['file']
        ext = file.name.split('.')[-1].lower()
        if ext != 'pdf':
            return JsonResponse({'error': 'Only PDF files are allowed.'}, status=400)
        file_content = extract_file_content(file)
        if file_content:
            return JsonResponse({'file_content': file_content})
        return JsonResponse({'error': 'Failed to extract content from the file.'}, status=400)
    return JsonResponse({'error': 'No file uploaded or invalid request.'}, status=400)
