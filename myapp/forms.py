from django import forms

class VideoUploadForm(forms.Form):
    input1 = forms.FileField(required=False)
    input2 = forms.FileField(required=False)
    input3 = forms.FileField(required=True)  # Body is required
