from django import forms 
from . import models 

class CreatePost(forms.ModelForm): 
    class Meta: 
        model = models.Post
        fields = ['name', 'any_file']