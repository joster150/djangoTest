from django import forms
import sys,os
from importnb import Notebook
from importlib import reload,import_module
from django.core.validators import MaxLengthValidator
from .models import NotebookModel,DocumentationPosts,DocumentationImage,Book
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.conf import settings

from datetime import datetime
from django_neomodel import DjangoNode
from neomodel import StructuredNode, StringProperty, DateTimeProperty, UniqueIdProperty
class CreateUserForm(UserCreationForm):
    class Meta:
        model =User
        fields=['username','email','password1','password2']

class BookForm(forms.ModelForm):
    file =forms.FileField()
    node_name=forms.CharField(max_length=50)
    class Meta:
        model = Book
        fields = ['title']

class UploadFileForm(forms.Form):
    file = forms.FileField()
    title = forms.CharField(max_length=50)

from django.forms.widgets import Select, SelectMultiple

class SelectWOA(Select):
    """
    Select With Option Attributes:
        subclass of Django's Select widget that allows attributes in options,
        like disabled="disabled", title="help text", class="some classes",
              style="background: color;"...

    Pass a dict instead of a string for its label:
        choices = [ ('value_1', 'label_1'),
                    ...
                    ('value_k', {'label': 'label_k', 'foo': 'bar', ...}),
                    ... ]
    The option k will be rendered as:
        <option value="value_k" foo="bar" ...>label_k</option>
    """

    def create_option(self, name, value, label, selected, index,
                      subindex=None, attrs=None):
        if isinstance(label, dict):
            opt_attrs = label.copy()
            label = opt_attrs.pop('label')
        else:
            opt_attrs = {}
        option_dict = super(SelectWOA, self).create_option(name, value,
            label, selected, index, subindex=subindex, attrs=attrs)
        for key,val in opt_attrs.items():
            option_dict['attrs'][key] = val
        return option_dict

class RawStepCardForm(forms.Form):
    def __init__(self,mod_choices_param=None,choices_param=None, *args, **kwargs):
        super(RawStepCardForm,self).__init__(*args, **kwargs)
        if choices_param!=None and mod_choices_param!=None:
            self.fields['using_function'].choices=choices_param
            self.fields['using_module'].choices=mod_choices_param
    using_module= forms.ChoiceField(
        choices=[(0,"")],
         widget=SelectWOA(
         attrs={"class":"form-control ajax-using_modules"}
               )
        )
    using_function=forms.ChoiceField(
        choices=[(0,"")],
         widget=SelectWOA(
         attrs={"class":"form-control ajax-using_functions"}
               )
        )
    description=forms.CharField(
        widget=forms.Textarea(attrs={
                            "placeholder":"Description of step",
                            "class":"form-control ajax-description",
                            "rows":4
                            })
                            )
    output= forms.CharField(
        widget=forms.TextInput(attrs={
                                "placeholder":"Output Variable",
                                "class":"form-control ajax-output"
                                })
                                )

class RawStepCardFormSubmit(forms.Form):
    title=forms.CharField(
        widget=forms.TextInput(attrs={
                                "placeholder":"Pipeline title",
                                "class":"form-control pipeline-title"
                                })
                                )
    description=forms.CharField(
        widget=forms.Textarea(attrs={
                            "placeholder":"Description of pipeline",
                            "class":"form-control pipeline-description",
                            "rows":4
                            })
                            )
class TextInput(forms.Form):
    form_val=forms.CharField(max_length=50)
class BooleanInput(forms.Form):
    form_val=forms.BooleanField(required=False)
class NumberInput(forms.Form):
    form_val=forms.FloatField()
class Variable(forms.Form):
    def __init__(self,choices_param=None, *args, **kwargs):
        super(Variable,self).__init__(*args, **kwargs)
        if choices_param!=None:
            self.fields['form_val'].choices=choices_param
    form_val=forms.ChoiceField(
         choices=[(0,"")],
         widget=SelectWOA(
         attrs={"class":"form-control ajax-using_functions"}))
class TableParam(forms.Form):
    def __init__(self,choices_param=None, *args, **kwargs):
        super(TableParam,self).__init__(*args, **kwargs)
        if choices_param!=None:
         self.fields['form_val'].choices=choices_param
    form_val=forms.ChoiceField(
      choices=[(0,"")],
      widget=SelectWOA(
      attrs={"class":"form-control table_param"}))
class FileInput(forms.Form):
    form_val = forms.FileField()
class tableCreation(forms.Form):
    verbose_name = forms.CharField(widget=forms.TextInput(attrs={
                            "placeholder":"Table name",
                            "class":"form-control table-form-container-name"
                            })
                            )
    table_group = forms.CharField(initial="Test",widget=forms.TextInput(attrs={
                            "placeholder":"Table group",
                            "class":"form-control table-form-group"
                            })
                            )

class FieldCreation(forms.Form):
    def __init__(self,choices_param=None, *args, **kwargs):
        super(FieldCreation,self).__init__(*args, **kwargs)
        self.fields['max_length'].widget.attrs['class'] = 'ajax-max_length'
        self.fields['required'].widget.attrs['class'] = 'ajax-required'
        if choices_param!=None:
            self.fields['data_type'].choices=choices_param
    name=forms.CharField(
        widget=forms.TextInput(attrs={
                                "placeholder":"Field name",
                                "class":"form-control ajax-name"
                                })
                                )
    data_type=forms.ChoiceField(
         choices=[(0,"String"),(1,"Integer"),(2,"Float")],
         widget=SelectWOA(attrs={
                            "class":"form-control ajax-data_type"
                            }))
    max_length=forms.IntegerField(required=False)
    required=forms.BooleanField(required=False)
class DataInt(forms.Form):
    def __init__(self,required_in=None, *args, **kwargs):
        super(DataInt,self).__init__(*args, **kwargs)
        if required_in!=None:
            self.fields['intField'].required=required_in
    intField=forms.IntegerField(required=True)
class DataString(forms.Form):
    def __init__(self,required_in=None, *args, **kwargs):
        super(DataString,self).__init__(*args, **kwargs)
        if required_in!=None:
            self.fields['stringField'].required=required_in
    stringField=forms.CharField(required=True)
class DataFloat(forms.Form):
    def __init__(self,required_in=None, *args, **kwargs):
        super(DataFloat,self).__init__(*args, **kwargs)
        if required_in!=None:
            self.fields['floatField'].required=required_in
    floatField=forms.FloatField(required=True)
class NotebookForm(forms.ModelForm):
    class Meta:
        model = NotebookModel
        fields = ['verbose_name','notebook_group', 'notebook','notebook_test']
    update=forms.BooleanField(required=False)
    def clean(self):
        #print(self.cleaned_data.get('update'))
        if not self.cleaned_data.get('update'):
            file_path = os.path.join(settings.SCRIPTS_ROOT,
                self.cleaned_data.get('notebook_group').upper()+"/" + str(self.cleaned_data.get('notebook')))
            file_path2 = os.path.join(settings.SCRIPTS_ROOT,
                self.cleaned_data.get('notebook_group').upper()+"/" + str(self.cleaned_data.get('notebook_test')))
            if os.path.isfile(file_path):
                raise ValidationError('Notebook already exists')
            elif os.path.isfile(file_path2):
                raise ValidationError('Noteebook test already exists')
        return self.cleaned_data
class DocumentationPostsForm(forms.ModelForm):
    class Meta:
        model = DocumentationPosts
        fields = ['title','content']
    content=forms.CharField(widget=forms.Textarea(attrs={
        'style': 'width: 100%;resize: none;overflow: hidden;min-height: 50px;',
        'class':'form-control',
        'oninput':"auto_grow(this)"
    }))
    title=forms.CharField(widget=forms.TextInput(attrs={
        'style': 'width: 100%',
        'class':'form-control'
    }))
class DocumentationImageForm(forms.ModelForm):
    class Meta:
        model = DocumentationImage
        fields=['image','caption']
