import datetime
from django import forms

from .models import Paper

class PaperForm(forms.Form):
    creator = forms.CharField(label='Creator', max_length=100)
    create_time = forms.DateTimeField(label='Create Time', input_formats='Y-m-d H:M:S')
    update_time = forms.DateTimeField(label='Update Time', input_formats='Y-m-d H:M:S')
    doi = forms.CharField(label='DOI', max_length=100, widget=forms.TextInput(attrs={'class':'with_button'}), required=False)
    pmid = forms.CharField(label='PMID', max_length=20, widget=forms.TextInput(attrs={'class':'with_button'}), required=False)
    arxiv_id = forms.CharField(label='arXiv ID', max_length=100, widget=forms.TextInput(attrs={'class':'with_button'}), required=False)
    pmcid = forms.CharField(label='PMCID', max_length=100, required=False)
    journal = forms.CharField(label='Journal', max_length=200, required=False)
    pub_date = forms.DateField(label='Publish Date', input_formats='Y-m-d', required=False)
    title = forms.CharField(label='Title', max_length=500, required=False)
    authors = forms.CharField(label='Authors', max_length=65536, widget=forms.Textarea, required=False)
    abstract = forms.CharField(label='Abstract', max_length=65536, widget=forms.Textarea, required=False)
    urls = forms.CharField(label='URLs', max_length=65536, widget=forms.Textarea, required=False)
    is_private = forms.BooleanField(widget=forms.RadioSelect, required=False)
    comments = forms.CharField(label='Comments', max_length=65536, widget=forms.Textarea, required=False)
    full_text = forms.FileInput()
