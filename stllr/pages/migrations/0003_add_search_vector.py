from django.db import migrations
from django.contrib.postgres.operations import TrigramExtension
from django.contrib.postgres.search import SearchVectorField
from django.contrib.postgres.indexes import GinIndex

class Migration(migrations.Migration):

    dependencies = [
        ('pages', '0002_domain_category'),
    ]

    operations = [
        TrigramExtension(),
        migrations.AddField(
            model_name='page',
            name='search_vector',
            field=SearchVectorField(null=True, editable=False),
        ),
        migrations.AddIndex(
            model_name='page',
            index=GinIndex(fields=['search_vector'], name='page_search_vector_gin'),
        ),
    ]