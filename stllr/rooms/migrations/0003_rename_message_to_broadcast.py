# Done by Claude, requires review
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rooms', '0002_rename_sent_on_message_created'),
        ('pages', '0007_alter_page_rise'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.RenameModel(
            old_name='Message',
            new_name='Broadcast',
        ),
        migrations.AlterField(
            model_name='broadcast',
            name='user',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name='broadcasts',
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AlterField(
            model_name='broadcast',
            name='page',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name='broadcasts',
                to='pages.page',
            ),
        ),
    ]
