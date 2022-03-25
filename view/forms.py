import datetime
from django import forms

from .models import Paper

class PaperForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super(PaperForm, self).__init__(*args, **kwargs)
        for name in self.fields.keys():
            self.fields[name].widget.attrs.update({
                'class': 'form-control',
            })
    class Meta:
        model = Paper
        fields = ("__all__")
