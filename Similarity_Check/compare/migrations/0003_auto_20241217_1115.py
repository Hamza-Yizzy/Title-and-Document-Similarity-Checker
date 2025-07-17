from django.db import migrations, models


def populate_book_id(apps, schema_editor):
    """Populate `book_id` with unique values."""
    Book = apps.get_model("compare", "Book")
    # Assign unique incremental IDs to all existing records
    for index, book in enumerate(Book.objects.all(), start=1):
        book.book_id = index
        book.save()


class Migration(migrations.Migration):

    dependencies = [
        ("compare", "0002_remove_book_id_book_book_id"),  # Last migration
    ]

    operations = [
        # Step 1: Add `book_id` field temporarily, allowing null
        migrations.AddField(
            model_name="book",
            name="book_id",
            field=models.BigIntegerField(unique=True, null=True),
        ),
        # Step 2: Populate `book_id` with unique values
        migrations.RunPython(populate_book_id),
        # Step 3: Alter `book_id` to make it a primary key
        migrations.AlterField(
            model_name="book",
            name="book_id",
            field=models.BigAutoField(primary_key=True),
        ),
    ]
