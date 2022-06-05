import datetime
from django import forms

from .models import Paper

class PaperForm(forms.Form):
    creator_nickname = forms.CharField(label='Nick Name', max_length=100, required=False) # 群友（昵称，用于搜索）
    creator_name = forms.CharField(label='Real Name', max_length=100, required=False) # 姓名
    creator_weixin_id = forms.CharField(label='Weixin ID', max_length=100, required=False) # 微信ID（跨系统的统一标识，但可能没法获取）
    creator_username = forms.CharField(label='User Name', max_length=100, required=False) # 关联到内部用户表（本系统的唯一标识）

    create_time = forms.DateTimeField(label='Create Time', input_formats='%Y-%m-%d %H:%M:%S', required=False)
    update_time = forms.DateTimeField(label='Update Time', input_formats='%Y-%m-%d %H:%M:%S', required=False)

    doi = forms.CharField(label='DOI', max_length=100, required=False)
    pmid = forms.CharField(label='PMID', max_length=20, required=False)
    arxiv_id = forms.CharField(label='arXiv ID', max_length=100, required=False)
    pmcid = forms.CharField(label='PMCID', max_length=100, required=False)
    cnki_id = forms.CharField(label='CNKI ID', max_length=100, required=False)

    journal = forms.CharField(label='Journal', max_length=200, required=False)
    pub_date = forms.DateField(label='Publish Date', required=False)
    title = forms.CharField(label='Title', max_length=500, required=False)
    authors = forms.CharField(label='Authors', max_length=65536, widget=forms.Textarea(attrs={'style': 'height:60px'}), required=False)
    abstract = forms.CharField(label='Abstract', max_length=65536, widget=forms.Textarea(attrs={'style': 'height:120px'}), required=False)
    keywords = forms.CharField(label='Keywords', max_length=65536, widget=forms.Textarea(attrs={'style': 'height:60px'}), required=False)
    urls = forms.CharField(label='URLs', max_length=65536, widget=forms.Textarea(attrs={'style': 'height:60px'}), required=False)
    #full_text = forms.FileField(label='Full Text', required=False)
    #full_text = forms.FileInput()
    is_preprint = forms.BooleanField(label='Is Preprint', required=False)
    is_review = forms.BooleanField(label='Is Review', required=False)
    is_open = forms.BooleanField(label='Is Open', required=False)

    is_favorite = forms.BooleanField(label='Is Favorite', required=False)
    is_private = forms.ChoiceField(label='Permission', widget=forms.RadioSelect, choices=[(False, 'Public'), (True, 'Private')])
    comments = forms.CharField(label='Comments', max_length=65536, widget=forms.Textarea(attrs={'style': 'height:400px'}), required=False)
