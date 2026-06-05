from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('books', '0017_book_date_created'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='subject',
            name='emoji',
        ),
    ]
