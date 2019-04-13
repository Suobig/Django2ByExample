from django import forms
from .models import Comment, Post

class EmailPostForm(forms.Form):
    name = forms.CharField(max_length=25)
    email = forms.EmailField()
    to = forms.EmailField()
    comments = forms.CharField(required=False,
                               widget=forms.Textarea)

class CommentForm(forms.ModelForm):
    post = forms.ModelChoiceField(
        widget=forms.HiddenInput,
        queryset=Post.objects.all(),
        disabled=True,
    )

    class Meta:
        model = Comment
        fields = ('post', 'name', 'email', 'body')

class SearchForm(forms.Form):
    query = forms.CharField(max_length=250)