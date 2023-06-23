from django.forms import ModelForm
from .models import Tag, Post

class TagForm(ModelForm):
    class Meta:
        model = Tag
        fields = ['name']


