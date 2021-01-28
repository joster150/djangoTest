from django.db import models
from django.dispatch import receiver
from django.utils.translation import ugettext_lazy as _
from django.utils.text import slugify
from django.conf import settings
import jsonfield
import sys,os,uuid
from importnb import Notebook
from importlib import reload,import_module
import pytest,pathlib,contextlib
import nbformat
from nbconvert import HTMLExporter
html_exporter = HTMLExporter()
User =settings.AUTH_USER_MODEL
dir = settings.SCRIPTS_ROOT
from django_neomodel import DjangoNode
from neomodel import StructuredNode, StringProperty, DateProperty

class Book(DjangoNode):
    title = StringProperty(unique_index=True)
    class Meta:
        app_label = 'library'
#print(dir)
class DocumentationPosts(models.Model):
    user = models.ForeignKey(User,default=1, on_delete=models.SET_DEFAULT)
    title = models.CharField(max_length=50)
    slug = models.SlugField(unique=True)
    content = models.TextField()
    def get_post_url(self):
        return f"/docs/{self.slug}"
    def get_edit_url(self):
        return f"/docs/{self.slug}/edit/"
    def save(self, *args, **kwargs):
        self.slug = slugify(self.title)
        super().save(*args, **kwargs)
class DocumentationImage(models.Model):
    def generate_image_path(self, filename):
        foldername = "media/%s/%s" % (self.post.slug.upper(), filename)
        return foldername
    post=models.ForeignKey(DocumentationPosts,on_delete=models.CASCADE)
    image=models.ImageField(upload_to=generate_image_path)
    #print(image.url)
    image_number=models.IntegerField(default=1)
    caption=models.CharField(max_length=100)
    class Meta:
        unique_together = ('post', 'image_number')
class ModelDefinition(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    verbose_name = models.CharField(max_length=50)
    name = models.CharField(max_length=50, unique=True)
    table_group = models.CharField(max_length=50,default="Test")
    definition = jsonfield.JSONField()

    def save(self, *args, **kwargs):
        self.name = slugify(self.verbose_name)
        super().save(*args, **kwargs)

class Data(models.Model):
    model_definition = models.ForeignKey(ModelDefinition, on_delete=models.CASCADE)
    data = jsonfield.JSONField(unique=True)

class step_tracker(models.Model):
    step=models.IntegerField()

class Pipelines(models.Model):
    user = models.ForeignKey(User, default=1,null=True, on_delete=models.SET_NULL)
    title = models.CharField(max_length=120)
    slug = models.SlugField(unique=True)
    description = models.TextField()
    def get_complete_url(self):
        return f"/pipelines/use/{self.slug}"
def generate_filename(self, filename):
    foldername = "nbscripts/%s/%s" % (self.notebook_group.upper(), filename)
    return foldername
class NotebookModel(models.Model):
    verbose_name = models.CharField(max_length=50)
    name = models.SlugField(unique=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    notebook_group=models.CharField(max_length=50, default="Test_Group")
    notebook = models.FileField(upload_to=generate_filename)
    notebook_html= models.TextField()
    notebook_test=models.FileField(upload_to=generate_filename)
    notebook_test_html= models.TextField()
    description=models.CharField(null=True,max_length=120)
    functions= jsonfield.JSONField()
    def get_complete_notebook_url(self):
        return f"/module_list/module_html/{self.name}"
    def get_complete_notebook_test_url(self):
        return f"/module_list/module_test_html/{self.name}"
    def save(self, *args, **kwargs):
        self.name = slugify(self.verbose_name)
        sys.path.append(dir+"/"+self.notebook_group)
        super().save(*args, **kwargs)
    def save2(self,*args,**kwargs):
        if self.notebook.path.endswith(".ipynb") and self.notebook_test.path.endswith(".ipynb"):
            with Notebook(lazy=True):
                #try:
                path,tail=os.path.split(self.notebook.path)
                tail=tail[:tail.index(".")]
                module_temp=import_module(tail)
                nb=nbformat.read(self.notebook.path, as_version=4)
                (body, resources) = html_exporter.from_notebook_node(nb)
                self.notebook_html=body
                #imported_notebooks_0[tail]N=module_temp
                self.description = module_temp.__doc__
                func_dict={}
                for func_name in list(module_temp.in_out_def().keys()):
                    func_dict[func_name]=getattr(module_temp, func_name).__doc__
                self.functions = func_dict
                path,tail=os.path.split(self.notebook_test.path)
                #with open(os.devnull, "w") as f, contextlib.redirect_stdout(f):
                var=pytest.main([str(self.notebook_test.path)])
                print(tail,":",var,', value: ',var.value)
                nb2=nbformat.read(self.notebook_test.path, as_version=4)
                (body2, resources2) = html_exporter.from_notebook_node(nb2)
                self.notebook_test_html=body2
                if var.value==0:
                    super().save(*args, **kwargs)
                    print('success')
                    return "success"
                #except:
                #    pass
        super().delete()
        print('fail')
        return "fail"
class Pipeline(models.Model):
    pipeline_id=models.ForeignKey(Pipelines, on_delete=models.CASCADE)
    step_num=models.IntegerField(default=1)
    module = models.ForeignKey(NotebookModel,on_delete=models.CASCADE,)#models.CharField(max_length=120)
    function = models.CharField(max_length=120)
    description = models.TextField()
    output = models.CharField(max_length=120)
    class Meta:
        unique_together = ('pipeline_id', 'step_num')

@receiver(models.signals.post_delete, sender=DocumentationImage)
def auto_delete_image_on_delete(sender, instance, **kwargs):
    """
    Deletes notebook from filesystem
    when corresponding `image` object is deleted.
    """
    if instance.image:
        #print(instance.image.path)
        if os.path.isfile(instance.image.path):
            os.remove(instance.image.path)
# These two auto-delete files from filesystem when they are unneeded:

@receiver(models.signals.post_delete, sender=NotebookModel)
def auto_delete_file_on_delete(sender, instance, **kwargs):
    """
    Deletes notebook from filesystem
    when corresponding `NotebookModel` object is deleted.
    """
    if instance.notebook:
        #print(instance.notebook.path)
        if os.path.isfile(instance.notebook.path):
            os.remove(instance.notebook.path)
    if instance.notebook_test:
        if os.path.isfile(instance.notebook_test.path):
            os.remove(instance.notebook_test.path)

@receiver(models.signals.pre_save, sender=NotebookModel)
def auto_delete_file_on_change(sender, instance, **kwargs):
    """
    Deletes old notebook from filesystem
    when corresponding `NotebookModel` object is updated
    with new notebook.
    """
    if not instance.pk:
        return False

    try:
        old_file = NotebookModel.objects.get(pk=instance.pk).notebook
        old_file2 = NotebookModel.objects.get(pk=instance.pk).notebook_test
    except NotebookModel.DoesNotExist:
        return False

    new_file = instance.notebook
    new_file2 = instance.notebook_test
    if not old_file == new_file:
        if os.path.isfile(old_file.path):
            os.remove(old_file.path)
    if not old_file2 == new_file2:
        if os.path.isfile(old_file2.path):
            os.remove(old_file2.path)
