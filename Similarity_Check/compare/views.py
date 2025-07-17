from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from .models import Book
from .forms import BookForm
import PyPDF2
import docx
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import os
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.shortcuts import render, redirect
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout

def logout_view(request):
    logout(request)  # Logs the user out
    return redirect('login')  # Redirect to the login page after logout

# Login View
def login_view(request):
    # If the user is already authenticated, redirect them to the dashboard
    if request.user.is_authenticated:
        return redirect('dashboard')  # Redirect to dashboard if the user is already logged in

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        # Authenticate the user using Django's built-in authentication
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)  # Log the user in
            return redirect('dashboard')  # Redirect to the dashboard page after login
        else:
            messages.error(request, "Invalid username or password")  # Show error if login fails

    return render(request, 'compare/login.html')  # Render the login page if not POST or failed login

# Function to read PDF files
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

# Function to read DOCX files
def read_docx(file):
    try:
        doc = docx.Document(file)
        text = "\n".join([para.text for para in doc.paragraphs])
        return text
    except Exception as e:
        return f"Error extracting DOCX content: {str(e)}"

# Function to extract content from uploaded file
def extract_file_content(file):
    ext = file.name.split('.')[-1].lower()
    if ext == 'pdf':
        return read_pdf(file)
    elif ext == 'docx':
        return read_docx(file)
    else:
        return None  # Unsupported file type

# Function to calculate cosine similarity using TF-IDF
def calculate_similarity(text1, text2):
    try:
        tfidf_vectorizer = TfidfVectorizer(stop_words='english')
        tfidf_matrix = tfidf_vectorizer.fit_transform([text1, text2])
        similarity_matrix = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])
        return similarity_matrix[0][0]
    except Exception as e:
        print(f"Error calculating similarity: {str(e)}")
        return 0.0

# Function to check title in the database
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

# Function to compare uploaded file content
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
            if file_name == book.book_title.strip().lower():  # Title match
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

        # Compare with all books in database
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

# Dashboard page
@login_required
def dashboard(request):
    return render(request, 'compare/dashboard.html')

# Home page view
def index(request):
    return render(request, 'compare/index.html')

# View to list all books
def books_list(request):
    books = Book.objects.all()
    return render(request, 'compare/book_list.html', {'books': books})

# View to add or edit a book
def add_or_edit_book(request, book_id=None):
    book = get_object_or_404(Book, book_id=book_id) if book_id else None
    form = BookForm(request.POST or None, request.FILES or None, instance=book)
    if request.method == 'POST' and form.is_valid():
        form.save()
        return redirect('books_list')
    return render(request, 'compare/registration.html', {'form': form})

# View to delete a book
def delete_book(request, book_id):
    book = get_object_or_404(Book, book_id=book_id)
    if request.method == 'POST':
        book.delete()
        return redirect('books_list')
    return render(request, 'compare/delete_book.html', {'book': book})

# View to handle file upload via AJAX
def handle_uploaded_file(request):
    if request.method == 'POST' and request.FILES.get('file'):
        file = request.FILES['file']
        allowed_extensions = ['pdf', 'docx']
        ext = file.name.split('.')[-1].lower()
        if ext not in allowed_extensions:
            return JsonResponse({'error': 'Unsupported file extension. Only PDF and DOCX are allowed.'}, status=400)
        file_content = extract_file_content(file)
        if file_content:
            return JsonResponse({'file_content': file_content})
        return JsonResponse({'error': 'Failed to extract content from the file.'}, status=400)
    return JsonResponse({'error': 'No file uploaded or invalid request.'}, status=400)
