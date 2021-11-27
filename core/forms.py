from django import forms
from import_export.admin import ExportActionMixin
from import_export.forms import ImportForm, ExportForm, ConfirmImportForm
from core.models import Question, Choice, Author, Book, Category, Task


class BookCustomImportForm(ImportForm):
    author = forms.ModelChoiceField(queryset=Author.objects.all(), required=True)


class BookCustomConfirmImportForm(ConfirmImportForm):
    author = forms.ModelChoiceField(queryset=Author.objects.all(), required=True)
    

class TaskCustomExportForm(ExportForm):
    # author = forms.ModelChoiceField(queryset=Author.objects.all(), required=True)
    pass


class TaskCustomImportForm(ImportForm):
    # author = forms.ModelChoiceField(queryset=Author.objects.all(), required=True)
    pass


class TaskCustomConfirmImportForm(ConfirmImportForm):
    # author = forms.ModelChoiceField(queryset=Author.objects.all(), required=True)
    pass