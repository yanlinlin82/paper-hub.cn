import datetime
from django import forms

from .models import Paper

class PaperForm(forms.Form):
    creator = forms.CharField(label='Creator', max_length=100)
    create_time = forms.DateTimeField(label='Create Time', input_formats='%Y-%m-%d %H:%M:%S')
    update_time = forms.DateTimeField(label='Update Time', input_formats='%Y-%m-%d %H:%M:%S')

    doi = forms.CharField(label='DOI', max_length=100, widget=forms.TextInput(attrs={'class':'with_button'}), required=False)
    pmid = forms.CharField(label='PMID', max_length=20, widget=forms.TextInput(attrs={'class':'with_button'}), required=False)
    arxiv_id = forms.CharField(label='arXiv ID', max_length=100, widget=forms.TextInput(attrs={'class':'with_button'}), required=False)
    pmcid = forms.CharField(label='PMCID', max_length=100, widget=forms.TextInput(attrs={'class':'with_button'}), required=False)
    cnki_id = forms.CharField(label='CNKI ID', max_length=100, widget=forms.TextInput(attrs={'class':'with_button'}), required=False)

    journal = forms.CharField(label='Journal', max_length=200, required=False)
    pub_date = forms.DateField(label='Publish Date', required=False)
    title = forms.CharField(label='Title', max_length=500, required=False)
    authors = forms.CharField(label='Authors', max_length=65536, widget=forms.Textarea(attrs={'style': 'height:60px'}), required=False)
    abstract = forms.CharField(label='Abstract', max_length=65536, widget=forms.Textarea(attrs={'style': 'height:120px'}), required=False)
    keywords = forms.CharField(label='Keywords', max_length=65536, widget=forms.Textarea(attrs={'style': 'height:60px'}), required=False)
    urls = forms.CharField(label='URLs', max_length=65536, widget=forms.Textarea(attrs={'style': 'height:60px'}), required=False)
    #full_text = forms.FileField(label='Full Text', required=False)
    #full_text = forms.FileInput()
    is_review = forms.BooleanField(label='Is Review', required=False)
    is_open = forms.BooleanField(label='Is Open', required=False)

    is_private = forms.ChoiceField(label='Permission', widget=forms.RadioSelect, choices=[(False, 'Public'), (True, 'Private')])
    comments = forms.CharField(label='Comments', max_length=65536, widget=forms.Textarea(attrs={'style': 'height:200px'}), required=False)
    