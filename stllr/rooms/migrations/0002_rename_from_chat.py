from django.db import migrations

class Migration(migrations.Migration):

    dependencies = [
        ('rooms', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelTable(
            name='Message',
            table=None,   # None = use Django's default: rooms_message
        ),
    ]
