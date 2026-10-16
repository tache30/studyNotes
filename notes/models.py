from django.db import models


class Note(models.Model):
    id = models.AutoField(primary_key=True)
    content = models.TextField()

    class Meta:
        managed = False
        db_table = 'notes'