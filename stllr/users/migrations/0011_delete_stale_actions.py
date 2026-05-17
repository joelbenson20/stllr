from django.db import migrations


def delete_all_actions(apps, schema_editor):
    # Done by Claude, requires review
    Action = apps.get_model('users', 'Action')
    Action.objects.all().delete()


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0010_alter_action_verb'),
    ]

    operations = [
        migrations.RunPython(delete_all_actions, migrations.RunPython.noop),
    ]
