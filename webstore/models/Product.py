from django.db import models

from Category import Category

class Product(models.Model):
    name = models.CharField("Name", max_length=100)
    quantity = models.IntegerField("Quantity",)
    price = models.FloatField("Price",)
    category = models.ForeignKey(Category, related_name ='products')

    def __unicode__(self):  # Python 3: def __str__(self):
        return self.name
    
    class Meta:
        db_table = 'webstore_product'
        app_label= 'webstore'