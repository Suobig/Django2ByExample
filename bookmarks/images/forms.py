from .models import Image
from django import forms
from urllib import request
from django.core.files.base import ContentFile
from django.utils.text import slugify
from .utils import file_extension

class ImageCreateForm(forms.ModelForm):
    class Meta:
        model = Image
        fields = ('title', 'url', 'description')
        widgets = {
            'url': forms.HiddenInput,
        }

    def clean_url(self):
        url = self.cleaned_data['url']
        valid_extensions = ['jpg', 'jpeg']
        extension = file_extension(url)
        if extension not in valid_extensions:
            raise forms.ValidationError("The given URL doesn't "\
                                        "match valid image extensions.")
        return url

    def save(self, 
             force_insert=True, 
             force_update=True, 
             commit=True):
        image = super().save(commit=False)
        image_url = self.cleaned_data['url']
        extension = file_extension(image_url)
        image_name = f'{slugify(image.title)}.{extension}'

        #download image from the given URL:
        response = request.urlopen(image_url)
        image.image.save(image_name,
                         ContentFile(response.read()),
                         save=False)
        if commit:
            image.save()
        return image

                    
