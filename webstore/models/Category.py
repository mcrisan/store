from django.db import models


class Category(models.Model):
    name = models.CharField("Name", max_length=50)
    
    def __unicode__(self):  # Python 3: def __str__(self):
        return self.name

    class Meta:
        db_table = 'webstore_category'
        app_label= 'webstore'