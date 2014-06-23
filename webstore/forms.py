from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.forms import ModelForm, Textarea, CharField, ValidationError, IntegerField, Form
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit

from webstore.models import Product
from .models import Cart, Rating, DeliveryDetails


class RegisterForm(UserCreationForm):
    first_name = CharField(max_length=30)
    last_name = CharField(max_length=30)

    def __init__(self, *args, **kwargs):
        super(RegisterForm, self).__init__(*args, **kwargs)
        del self.fields['password2']
     
    class Meta:
        model = User
        fields = ("first_name", "last_name", 'username', 'password1') 
   
        
class UserEditForm(ModelForm):
    class Meta:
        model = User 
        fields = ("first_name", "last_name", "email") 
        
class SearchForm(Form):
    query = CharField(max_length=100)         

       
 
        
class DeliveryDetailsForm(ModelForm):    
    class Meta:
        model = DeliveryDetails 
        fields = ("address", "phonenumber")            
  
  
class CartForm(Form): 
    qty = IntegerField()
    prod_id = IntegerField() 
        
    def clean_qty(self):
        quantity = int(self.cleaned_data['qty'])
        if quantity <0:
            raise ValidationError("Quantity must be a positive number")
        return quantity 
    
    def clean_prod_id(self):
        product_id = int(self.cleaned_data['prod_id'])
        if not Product.objects.filter(id=product_id).exists():
            raise ValidationError("Product does not exist")
        return product_id  
    
    def clean(self):
        form_data = self.cleaned_data
        prod = Product.objects.get(pk=form_data['prod_id'])
        if prod.quantity < form_data['qty']:
            self._errors['qty'] = "Quantity is to big"
            del form_data['qty']    
        return form_data 
    
        
class RatingForm(ModelForm): 
    rating = IntegerField()
    prod_id = IntegerField()   
      
    def clean_rating(self):
        rating = int(self.cleaned_data['rating'])
        if rating<0 or rating>5:
            raise ValidationError("Rating must be between 0 and 5")
        return rating 
    
    def clean_prod_id(self):
        product_id = int(self.cleaned_data['prod_id'])
        if not Product.objects.filter(id=product_id).exists():
            raise ValidationError("Product does not exist")
        return product_id  
    
    class Meta:
        model = Rating 
        fields = ("rating", "prod_id")   
  
        
class ProductRatingsForm(Form): 
    prod_id = IntegerField() 
    
    def clean_prod_id(self):
        data = self.data
        ids = data.getlist('prod_id')
        for product_id in ids:
            if not Product.objects.filter(id=product_id).exists():
                raise ValidationError("Product does not exist")
        return ids     