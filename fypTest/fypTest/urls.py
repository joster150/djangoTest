"""fypTest URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from . import settings
from django.contrib.staticfiles.urls import static
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from importJupyter.views import neo_view,edit_doc_post,view_doc_post,create_doc_post,list_modules,documentation,home,pipeline_creation,pipeline_completion,createTable,list_tables,view_data,module_test_html_view,module_html_view,loginPage,register,logoutUser,pipeline_view
urlpatterns = [
    path('',home),
    path('home/',home),
    path('create_doc_post/',create_doc_post),
    path('docs/<str:doc_slug>/edit/',edit_doc_post),
    path('docs/<str:doc_slug>',view_doc_post),
    path('neo/',neo_view),
    path('docs/',documentation),
    path('admin/', admin.site.urls),
    path('login/',loginPage,name="login"),
    path('logout/',logoutUser,name="logout"),
    path('register/',register,name="register"),
    path('module_list/module_test_html/<str:mod_slug>/',module_test_html_view),
    path('module_list/module_html/<str:mod_slug>/',module_html_view),
    path('module_list/', list_modules),
    path('tables/create/',createTable),
    path('tables/', list_tables),
    path('pipelines/create/',pipeline_creation),
    path('pipelines/use/<str:pipe_slug>/',pipeline_completion),
    path('pipelines/',pipeline_view),
    path('view_table/<str:view_slug>/',view_data),
]
urlpatterns += staticfiles_urlpatterns()
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
