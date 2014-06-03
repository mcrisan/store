from django.forms import ModelForm, Textarea, CharField, ValidationError
from django.contrib.auth.models import User


class RegisterForm(ModelForm):
    
    class Meta:
        model = User
        exclude = ['from_user', 'to_user' ]
        fields = ( 'first_name', 'last_name', 'username', 'password')
    def clean_username(self):
        name = self.cleaned_data['username']
        # check the name if you need to
        try:
            # maybe check if it already exists?
            
            user = User.objects.get(username=name)
            aux=0
        except User.DoesNotExist:
            aux=1    
            #raise ValidationError("The username is taken")
            # you probably only want to save this when the form is saved (in the view)
        if aux==0:
            raise ValidationError("The username is taken")   
        return name