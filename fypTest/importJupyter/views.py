from django.shortcuts import render,redirect
from django import forms
from django.conf import settings
import io,base64,urllib,json,sys,os
import matplotlib.pyplot as plt
from .forms import BookForm,DocumentationImageForm,DocumentationPostsForm,BooleanInput,CreateUserForm,NotebookForm,UploadFileForm,RawStepCardForm,RawStepCardFormSubmit,TextInput,NumberInput,Variable,TableParam,FileInput,tableCreation,FieldCreation,DataInt,DataFloat,DataString
import pandas as pd
from django.http import JsonResponse,QueryDict
from .models import step_tracker,Pipelines,Pipeline,ModelDefinition,Data,NotebookModel,DocumentationPosts,DocumentationImage
from django.template.defaultfilters import slugify
from importnb import Notebook
from importlib import reload,import_module
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required

from neomodel import (db,core,config, StructuredNode, StringProperty, IntegerProperty,
    UniqueIdProperty, RelationshipTo, remove_all_labels, install_all_labels,RelationshipDefinition)

param_type_dict={'file_browse':'<input value="VAL" name="NAME" type="file" required>','files_browse':'<input name="NAME" type="file" required multiple>','variable':'','text_input':'<input value="VAL" name="NAME" type="text">',
                'number_input':'<input value="VAL" name="NAME" type="number">'}
form_dict={'file_browse':FileInput,'files_browse':forms.FileField,'variable':Variable,'choice':Variable,
            'text_input':TextInput,'number_input':NumberInput,'table_param':TableParam,'boolean':BooleanInput}
imported_notebooks={}
dir = settings.SCRIPTS_ROOT
nb_script_groups=NotebookModel.objects.values_list('notebook_group',flat=True).distinct()
if nb_script_groups.exists():
    # for fldr in nb_script_groups:
    #     sys.path.append(os.path.join(dir,fldr.upper()))
    #     with Notebook(lazy=True):
    #         for temp in os.listdir(os.path.join(dir,fldr.upper())):
    #             if temp.endswith('.ipynb'):
    #                 path,tail=os.path.split(temp)
    #                 if not tail.startswith('test'):
    #                     tail=tail[:tail.index(".")]
    #                     module_temp=import_module(tail)
    #                     print(tail)
    #                     imported_notebooks[tail]=module_temp
    #                     reload(module_temp)
    notebooks=NotebookModel.objects.all()
    for fldr in nb_script_groups:
        sys.path.append(os.path.join(dir,fldr.upper()))
    for nb in notebooks:
        path,tail=os.path.split(nb.notebook.path)
        tail=tail[:tail.index(".")]
        if tail not in sys.modules:
            with Notebook(lazy=True):
                module_temp=import_module(tail)
                imported_notebooks[nb.name]=module_temp
    imported_notebooks_functions={}
    for tail,module_temp in imported_notebooks.items():
        func_dict={}
        for func_name in list(module_temp.in_out_def().keys()):
            func_dict[func_name]=getattr(module_temp, func_name)
        imported_notebooks_functions[tail]={
        'functions':func_dict,
        }
def fig_to_html(fig):
    buf=io.BytesIO()
    fig.savefig(buf,format='png',bbox_inches = "tight")
    buf.seek(0)
    stringImage=base64.b64encode(buf.read())
    return urllib.parse.quote(stringImage)

def data_validate(data,f_dict):
    #print(f_dict)
    required_in=f_dict["required"]
    if f_dict['data_type'].lower() == 'string':
        if len(data)>f_dict['max_length']:
            return False
        sd=DataString(required_in=required_in,data={'stringField':data})
        if sd.is_valid():
            return True
    elif f_dict['data_type'].lower() == 'integer':
        if data=="" and (not required_in):
            return True
        try:
            data=int(data)
        except:
            return False
        id=DataInt(required_in=required_in,data={'intField':data})
        if id.is_valid():
            return True
    elif f_dict['data_type'].lower() == 'float':
        if data=="" and (not required_in):
            return True
        try:
            data=float(data)
        except:
            return False
        fd=DataFloat(required_in=required_in,data={'floatField':data})
        if fd.is_valid():
            return True
    else:
        return False
    return False
def neo_view(request):
    form=BookForm()
    context={'form':form}
    template_name="importJupyter/neo.html"
    if request.method=='POST':
        form=BookForm(request.POST,request.FILES)
        if form.is_valid():
            form.save()
            df=pd.read_csv(request.FILES.get('file'))
            class_content={}
            param_dict={"props":[]}
            for i in range(len(df.index)):
                mini_dict={}
                for j,c in enumerate(df.columns):
                    if isinstance(df.iloc[i,j],np.int64):
                        mini_dict[c]=int(df.iloc[i,j])
                    else:
                        mini_dict[c]=df.iloc[i,j]
                param_dict['props'].append(mini_dict)
            r,m=db.cypher_query("UNWIND $props AS map CREATE (n:Person) SET n = map",param_dict)

            r,m=db.cypher_query("MATCH (a:Person), (b:File) WHERE EXISTS (a.x) AND EXISTS (b.x) AND a.x=b.x CREATE (a)-[:LIVES]->(b);")
    ##MATCH(f:File {x:2}),(f2:first_file {x:2}) CREATE (f)-[:HAS_X]->(f2)
    r,m=db.cypher_query("MATCH (n) RETURN distinct labels(n)")
    nodes1=[r1[0][0] for r1 in r]
    context['labels']=nodes1
    keys_nodes=[]
    for node1 in nodes1:
        r,m=db.cypher_query("MATCH (l:"+node1+") UNWIND keys(l) as key RETURN distinct key")
        keys_nodes.append([r1[0] for r1 in r])
    context['label_keys']=keys_nodes
    print(keys_nodes)
    return render(request,template_name,context)
def loginPage(request):
    if request.user.is_authenticated:
        return redirect('/home/')
    else:
        context={'active_view':'login'}
        template_name="importJupyter/login.html"
        if request.method == "POST":
            username=request.POST.get("username")
            password=request.POST.get("password")
            user=authenticate(request,username=username,password=password)
            if user is not None:
                login(request,user)
                return redirect('/home/')
            else:
                messages.info(request,'Usename OR Password is incorrect')
                return render(request,template_name,context)
        return render(request,template_name,context)
@login_required(login_url="/login/")
def logoutUser(request):
    logout(request)
    return redirect('/login/')
def register(request):
    if request.user.is_authenticated:
        return redirect('/home/')
    else:
        context={'active_view':'login'}
        template_name="importJupyter/register.html"
        form=CreateUserForm()
        if request.method=='POST':
            form=CreateUserForm(request.POST)
            if form.is_valid():
                form.save()
                messages.success(request,"Account created for "+form.cleaned_data.get('username'))
                return redirect('/login/')
        context['form']=form
        return render(request,template_name,context)
@login_required(login_url="/login/")
def view_data(request,view_slug):
    context={"active_view":"tables"}
    template_name="importJupyter/view_data.html"
    table=ModelDefinition.objects.get(name=view_slug)
    datas=Data.objects.filter(model_definition=table)
    rows=[]
    fields=[t['name'] for t in table.definition['fields']]
    types=[t['data_type'] for t in table.definition['fields']]
    requireds=[("Required" if t['required'] else "") for t in table.definition['fields']]
    max_lengths=[('<'+str(t['max_length']) if 'max_length' in [*t.keys()] else "") for t in table.definition['fields']]
    for data in datas:
        data_dict={}
        for field in fields:
            if field in list(data.data.keys()):
                data_dict[field]=data.data[field]
        rows.append(data_dict)
    context['rows']=rows
    context["columns"]=fields
    context["types"]=types
    context["requireds"]=requireds
    context["max_lengths"]=max_lengths
    if request.is_ajax():
        if request.POST.get('ajax_type')=="add_row":
            status="success"
            row=request.POST.getlist('row_data[]')
            field_def=table.definition['fields']
            data_dict={}
            valid=True
            for data,col in zip(row,fields):
                print(data,col)
                for f_dict in field_def:
                    if slugify(col) == f_dict["name"]:
                        if data_validate(data,f_dict):
                            if f_dict['data_type']=="integer":
                                val=(int(data) if data!="" else None)
                            elif f_dict['data_type']=="float":
                                val=(float(data) if data!="" else None)
                            else:
                                val=data
                            data_dict[f_dict["name"]]=val
                        else:
                            valid=False
            print(row,data_dict,valid)
            if valid:
                try:
                    d_obj=Data.objects.create(model_definition=table,data=data_dict)
                    d_obj.save()
                except:
                    status='fail'
            else:
                status="fail"
            return JsonResponse({"status":status,"columns":fields,"row":list(data_dict.values())},status=200)
    return render(request,template_name,context)

def home(request):
    context={'active_view':'home'}
    template_name="importJupyter/index.html"
    pipelines=[]
    if request.user.is_authenticated:
        for p in Pipelines.objects.all():
            pipeline_dict={
            'title':p.title,
            'user':p.user,
            'description':p.description,
            'completion_url':p.get_complete_url(),
            }
            pipelines.append(pipeline_dict)
    context['pipeline_list']=pipelines
    return render(request,template_name,context)
def pipeline_view(request):
    context={'active_view':'pipelines'}
    template_name="importJupyter/pipeline_list.html"
    pipelines=[]
    if request.user.is_authenticated:
        for p in Pipelines.objects.all():
            pipeline_dict={
            'title':p.title,
            'user':p.user,
            'description':p.description,
            'completion_url':p.get_complete_url()
            }
            pipelines.append(pipeline_dict)
    context['pipeline_list']=pipelines
    context['create_url']="/pipelines/create/"
    return render(request,template_name,context)
@login_required(login_url="/login/")
def list_tables(request):
    context={'active_view':'tables'}
    template_name="importJupyter/table_list.html"
    table_list=[]
    tables=ModelDefinition.objects.all()
    for tab in tables:
        column_list=[]
        for c in tab.definition['fields']:
            column_list.append(
            {
            'name':c['verbose_name'],
            'd_type':c['data_type'],
            'max_length':(c['max_length'] if c['data_type'].lower()=='string' else ""),
            'required':c['required']
            }
            )
        table_list.append({
        "title":tab.verbose_name,
        "table_group":tab.table_group,
        "columns":column_list,
        "user":tab.user,
        "view_data":"/view_table/"+tab.name+"/"
        })
    context['table_list']=table_list
    context['create_url']="/tables/create/"
    return render(request,template_name,context)
@login_required(login_url="/login/")
def createTable(request):
    context={'active_view':'tables'}
    template_name="importJupyter/createTable.html"
    if request.is_ajax():
        if request.POST.get('ajax_type')=="add_field":
            s=step_tracker.objects.get(pk=request.session['id'])
            s.step=s.step+1
            s.save()
            field_count=s.step
            field_form=FieldCreation()
            return JsonResponse({"field_form":field_form.as_p(),"field_num":field_count},status=200)
        elif request.POST.get('ajax_type')=="post_table":
            table_name=request.POST.get('ajax_name')
            table_group=request.POST.get('ajax_group')
            names=request.POST.getlist('names[]')
            data_types=request.POST.getlist('data_types[]')
            max_lengths=request.POST.getlist('max_lengths[]')
            requireds=request.POST.getlist('requireds[]')
            requireds=[(True if i=="true" else False) for i in requireds]
            form_list=[]
            nums_list=[i+1 for i in range(len(names))]
            alert="success"
            for name, d_type, m_len, required in zip(names,data_types,max_lengths,requireds):
                field_f=FieldCreation(data={
                'name':name
                ,'data_type':d_type
                ,'max_length':m_len
                ,'required':required
                })
                if not field_f.is_valid():
                    alert='false'
                form_list.append(field_f.as_p())
            t_form=tableCreation(data={'table_group':table_group,'verbose_name':table_name})
            if not t_form.is_valid():
                alert='false'
            if alert=='success':
                verbose_name = table_name
                definition = {"fields": [],"global_options": {"guest": {"verbose_name": "Allow guests to enter data","option": true},
                  "public": {"verbose_name": "Data is publicly accessible","option": false}}}
                types=[(0,"String"),(1,"Integer"),(2,"Float")]
                for name, d_type, m_len, required in zip(names,data_types,max_lengths,requireds):
                    data={
                      "name": slugify(name),
                      "verbose_name": name,
                      "data_type": types[int(d_type)][1],
                      "required": required,
                    }
                    if (types[int(d_type)][1]).lower()=='string':
                        data["max_length"]=int(m_len)
                    definition['fields'].append(data)
                mod_def=ModelDefinition(**{
                'user':request.user,
                'verbose_name' : table_name,
                'table_group':table_group,
                'definition':definition
                })
                mod_def.save()
            return JsonResponse({"field_nums":nums_list,"forms":form_list,'table_form':t_form.as_p(),'status':alert},status=200)
    new_step=step_tracker.objects.create(step=0)
    new_step.save()
    request.session.__setitem__('id', new_step.pk)
    table_form=tableCreation()
    context['form_table']=table_form
    return render(request,template_name,context)
@login_required(login_url="/login/")
def pipeline_completion(request,pipe_slug):
    context={'active_view':'pipelines'}
    template_name="importJupyter/pipeline_completion.html"
    nb_script_groups=NotebookModel.objects.values_list('notebook_group',flat=True).distinct()

    notebooks=NotebookModel.objects.all()
    if notebooks.exists():
        for fldr in nb_script_groups:
            sys.path.append(os.path.join(dir,fldr.upper()))
        for nb in notebooks:
            path,tail=os.path.split(nb.notebook.path)
            tail=tail[:tail.index(".")]
            if tail not in sys.modules:
                with Notebook(lazy=True):
                    module_temp=import_module(tail)
                    imported_notebooks[nb.name]=module_temp
        for fldr in nb_script_groups:
            #sys.path.append(os.path.join(dir,fldr.upper()))
            for temp in os.listdir(dir):
                if temp.endswith('.ipynb'):
                    path,tail=os.path.split(temp)
                    tail=tail[:tail.index(".")]
                    if tail not in sys.modules and (not tail.startswith('test')):
                        with Notebook(lazy=True):
                            module_temp=import_module(tail)
                            imported_notebooks[tail]=module_temp
    print(imported_notebooks)
    pipe=Pipelines.objects.get(slug=pipe_slug)
    pipe_steps=Pipeline.objects.filter(pipeline_id=pipe.pk)
    context['pipe_title']=pipe.title
    step_dict={}
    pre_pre_form='<div><h6 class="text-muted my-0 toggle">Param '
    pre_form=' \/</h6><div class="my-1" style="display:none">'
    post_form='</div></div>'
    pipeline_valid=True
    pipeline_out={}
    outputs={}
    out_choices_list=[]
    tables=ModelDefinition.objects.all()
    table_groups=[*set([t.table_group for t in tables])]
    unique_table_groups=[(i,t_group) for i,t_group in enumerate(table_groups)]
    table_group_form=Variable(choices_param=unique_table_groups)
    context['table_groups']=table_group_form.as_p().replace('<label for="id_form_val">Form val:</label>','').replace('ajax-using_functions','table_group')
    tables_in_group=[(i,t.name) for i,t in enumerate(tables) if t.table_group == unique_table_groups[0][1]]
    tables_in_group_form=Variable(choices_param=tables_in_group)
    context['tables_in_group']=tables_in_group_form.as_p().replace('<label for="id_form_val">Form val:</label>','').replace('ajax-using_functions','table_select')
    columns_in_table=[(i,f['name']) for i,f in enumerate(ModelDefinition.objects.get(name=tables_in_group[0][1]).definition["fields"])]
    columns_form=Variable(choices_param=columns_in_table)
    context['columns_in_table']=columns_form.as_p().replace('<label for="id_form_val">Form val:</label>','').replace('ajax-using_functions','search_column')

    datas=Data.objects.filter(model_definition=ModelDefinition.objects.get(name=tables_in_group[0][1]))
    rows=[]
    fields=[t['name'] for t in ModelDefinition.objects.get(name=tables_in_group[0][1]).definition['fields']]
    for data in datas:
        data_dict={}
        for field in fields:
            if field in list(data.data.keys()):
                data_dict[field]=data.data[field]
        rows.append(data_dict)
    context['rows']=rows
    context['table_data_columns']=fields

    if request.is_ajax():
        if request.POST.get('ajax_type')=="table_select":
            table=request.POST.get('ajax_table')
            table=ModelDefinition.objects.get(name=table)
            datas=Data.objects.filter(model_definition=table)
            rows=[]
            fields=[t['name'] for t in table.definition['fields']]
            for data in datas:
                data_dict={}
                for field in fields:
                    if field in list(data.data.keys()):
                        data_dict[field]=data.data[field]
                rows.append(data_dict)
            table_head_str=""
            table_body_str=""
            for field in fields:
                table_head_str+='<th scope="col">'+field+'</th>'
            search_cols=Variable(choices_param=[(i,f) for i,f in enumerate(fields)])
            search_cols=search_cols.as_p().replace('<label for="id_form_val">Form val:</label>','').replace('ajax-using_functions','search_column')
            print(fields,rows,search_cols)
            for row in rows:
                table_body_str+="<tr>"
                for field in fields:
                    table_body_str+="<td>"+str(row[field])+"</td>"
                table_body_str+="</tr>"
            return JsonResponse({'table_body':table_body_str,"table_head":table_head_str,"search_cols":search_cols},status=200)
        elif request.POST.get('ajax_type')=='table_group_choice':
            table_group=request.POST.get('ajax_table_group')
            tables_in_group=[(i,t.name) for i,t in enumerate(tables) if t.table_group == table_group]
            tables_in_group_form=Variable(choices_param=tables_in_group).as_p().replace('<label for="id_form_val">Form val:</label>',
            '').replace('ajax-using_functions','table_select')
            columns_in_table=[(i,f['name']) for i,f in enumerate(ModelDefinition.objects.get(name=tables_in_group[0][1]).definition["fields"])]
            columns_form=Variable(choices_param=columns_in_table).as_p().replace('<label for="id_form_val">Form val:</label>',
            '').replace('ajax-using_functions','search_column')
            rows=[]
            fields=[t['name'] for t in ModelDefinition.objects.get(name=tables_in_group[0][1]).definition['fields']]
            datas=Data.objects.filter(model_definition=ModelDefinition.objects.get(name=tables_in_group[0][1]))
            for data in datas:
                data_dict={}
                for field in fields:
                    if field in list(data.data.keys()):
                        data_dict[field]=data.data[field]
                rows.append(data_dict)
            table_head_str=""
            table_body_str=""
            for field in fields:
                table_head_str+='<th scope="col">'+field+'</th>'
            search_cols=Variable(choices_param=[(i,f) for i,f in enumerate(fields)])
            search_cols=search_cols.as_p().replace('<label for="id_form_val">Form val:</label>','').replace('ajax-using_functions','search_column')
            print(fields,rows,search_cols)
            for row in rows:
                table_body_str+="<tr>"
                for field in fields:
                    table_body_str+="<td>"+str(row[field])+"</td>"
                table_body_str+="</tr>"
            return JsonResponse({'table_body':table_body_str,"table_head":table_head_str,'tables_in_group':tables_in_group_form,"search_cols":columns_form},status=200)
    for step in pipe_steps:
        input_dict=imported_notebooks[step.module.name].in_out_def()[step.function]['inputs']
        output_dict=imported_notebooks[step.module.name].in_out_def()[step.function]['outputs']
        input_form_part=""
        outputs[step.step_num]=[step.module.name,step.function,step.output]
        pipeline_out[step.step_num]={}

        for param,type2 in input_dict.items():
            input_var=str()
            replace_name=str(step.step_num)+'_'+step.module.name+'_'+step.function+'_'+param+'_'+type2
            if replace_name in list(request.FILES.keys()):
                pipeline_out[step.step_num][param]='FILE'+replace_name
            if type2 == "table_param":
                form=form_dict[type2](choices_param=[])
            elif 'choice' in type2:
                choicelist=type2[type2.index("[")+1:type2.index("]")].split(',')
                print(choicelist)
                choicetuplelist=[(i,val) for i,val in enumerate(choicelist)]
                form=form_dict['choice'](choices_param=choicetuplelist)
            elif type2 != "variable":
                form=form_dict[type2]()
            else:
                out_choices_tuple=tuple(out_choices_list)
                form=form_dict[type2](choices_param=out_choices_tuple)

            if request.method == 'POST' and type2 not in ['file_browse','files_browse']:
                input_var=request.POST.get(replace_name)
                if type2 not in ['files_browse']:
                    if type2 == "table_param":
                        tuple_param=str(input_var)[str(input_var).index('--')+2:]
                        out_choices_list_2=[(input_var,tuple_param)]
                        out_choices_tuple_2=tuple(out_choices_list_2)
                        form=form_dict[type2](data={'form_val':input_var},choices_param=out_choices_tuple_2)
                    elif 'choice' in type2:
                        choicelist=type2[type2.index("[")+1:type2.index("]")].split(',')
                        print(choicelist)
                        choicetuplelist=[(i,val) for i,val in enumerate(choicelist)]
                        form=form_dict['choice'](data={'form_val':input_var},choices_param=choicetuplelist)
                    elif type2 != "variable":
                        form=form_dict[type2](data={'form_val':input_var})
                    else:
                        out_choices_tuple=tuple(out_choices_list)
                        form=form_dict[type2](data={'form_val':input_var},choices_param=out_choices_tuple)

                    if form.is_valid():
                        if type2 == "variable":
                            pipeline_out[step.step_num][param]=out_choices_tuple[int(form.cleaned_data['form_val'])][1]
                        elif 'choice' in type2:
                            pipeline_out[step.step_num][param]=choicetuplelist[int(form.cleaned_data['form_val'])][1]
                        elif type2 == "table_param":
                            pipeline_out[step.step_num][param]=tuple_param[tuple_param.index('//')+2:]
                        else:
                            pipeline_out[step.step_num][param]=form.cleaned_data['form_val']

                    else:
                        pipeline_valid=False


            input_form_part+=pre_pre_form+param+pre_form+form.as_p().replace('<label for="id_form_val">Form val:</label>','').replace('name="form_val"','name="'+replace_name+'"')+post_form
        for name_out,typ_out in output_dict.items():
            if typ_out =="variable" or typ_out=='graph':
                out_choices_list.append((len(out_choices_list),step.output+'_out/var_'+name_out))
        step_dict['Step '+str(step.step_num)]={'form':input_form_part,'output':step.output,'module_function':step.module.name+'/'+step.function,'description':step.description,'step_class_title':str(step.step_num).replace(" ","")}
    print(pipeline_out)
    context['step_dict']=step_dict
    if request.method == 'POST' and pipeline_valid:
        output_vals={}
        print(pipeline_out)
        for s_num in range(len(pipe_steps)):
            for name,val in pipeline_out[s_num+1].items():
                if type(val) == type(True):
                    pass
                elif "_out/var_" in val:
                    out_name=val[val.index("_out/var_"):].replace("_out/var_","")
                    out_prefix=val[:val.index("_out/var_")]
                    step_to_use=0
                    #outputs[step.step_num]=[step.module,step.function,step.output]
                    for step_number,li in outputs.items():
                        if li[2]==out_prefix:
                            #print('found step')
                            step_to_use=step_number
                    pipeline_out[s_num+1][name]=output_vals[outputs[step_to_use][2]]['values'][out_name]
                elif "FILE" in val:
                    pipeline_out[s_num+1][name]=request.FILES[val[val.index("FILE")+4:]]
            out_func=getattr(imported_notebooks[outputs[s_num+1][0]], outputs[s_num+1][1])
            output_vals[outputs[s_num+1][2]]={"types":imported_notebooks[outputs[s_num+1][0]].in_out_def()[outputs[s_num+1][1]]['outputs'],
                                            "values":out_func(**pipeline_out[s_num+1])}
            if s_num+1 == len(pipe_steps):
                out_types_vars=output_vals[outputs[s_num+1][2]]["types"].items()
                context['graphs']=[]
                context["vars"]=[]
                context['table_var']=[]
                for name,typ in out_types_vars:
                    if typ=="graph":
                        context['active']=True
                        context['graph']=True
                        context['graphs'].append(json.dumps(output_vals[outputs[s_num+1][2]]["values"][name]))
                    elif typ=="variable":
                        out_var=output_vals[outputs[s_num+1][2]]["values"][name]
                        context["active"]=True
                        if isinstance(out_var,pd.DataFrame):
                            context['table']=True
                            context['table_var'].append({
                            'cols':[*out_var.columns],
                            'rows':[out_var.iloc[i,:].to_list() for i in range(len(out_var.index))]
                            })
                            #print([out_var.iloc[i,:].to_list() for i in range(len(out_var.index))])
                        else:
                            context["variable"]=True
                            context["vars"].append({
                            "value":str(out_var),
                            "name":name})
                #print(context)
    return render(request,template_name,context)
@login_required(login_url="/login/")
def pipeline_creation(request):
    modules=NotebookModel.objects.all()
    mod_choices=tuple([(i,mod.name) for i,mod in enumerate(modules)])
    choices=tuple([(i,key) for i,key in enumerate(modules[0].functions.keys())])
    if request.is_ajax():
        if request.POST.get('ajax_type')=="add_step":
            s=step_tracker.objects.get(pk=request.session['id'])
            s.step=s.step+1
            step_count=s.step
            form=RawStepCardForm(mod_choices_param=mod_choices,choices_param=choices)
            s.save()
            return JsonResponse({'step_count':step_count,"form":form.as_p()},status=200)
        elif request.POST.get('ajax_type')=="post_pipe":
            title=request.POST.get('ajax_title')
            description=request.POST.get('ajax_description')
            descriptions=request.POST.getlist('descriptions[]')
            using_modules=request.POST.getlist('using_modules[]')
            using_functions=request.POST.getlist('using_functions[]')
            outputs=request.POST.getlist('outputs[]')
            step_nums=request.POST.getlist('step_nums[]')
            step_nums_int=[int(i[i.index(" "):]) for i in step_nums]
            forms=[]
            alert="success"
            pipeline_form=RawStepCardFormSubmit(data={'description':description,'title':title})
            if not pipeline_form.is_valid():
                alert=''
            for a,b,c,d,e in zip(descriptions,using_modules,using_functions,outputs,step_nums_int):
                choices=tuple([(i,key) for i,key in enumerate(modules[int(b)].functions.keys())])
                form=RawStepCardForm(data={'using_module':b,'using_function':c,
                                    'description':a,'output':d},mod_choices_param=mod_choices,choices_param=choices)

                forms.append(form.as_p())
                if not form.is_valid():
                    alert=''
            if alert=='success':
                new_pipe=Pipelines.objects.create(user=request.user,title=pipeline_form.cleaned_data['title'],
                slug=slugify(pipeline_form.cleaned_data['title']),description=pipeline_form.cleaned_data['description'])
                for a,b,c,d,e in zip(descriptions,using_modules,using_functions,outputs,step_nums_int):
                    choices=tuple([(i,key) for i,key in enumerate(modules[int(b)].functions.keys())])
                    form=RawStepCardForm(data={'using_module':b,'using_function':c,
                                        'description':a,'output':d},mod_choices_param=mod_choices,choices_param=choices)
                    if form.is_valid():
                        mod=NotebookModel.objects.filter(name=mod_choices[int(b)][1])
                        print(mod_choices[int(b)][1])
                        if mod.exists():
                            new_step=Pipeline.objects.create(pipeline_id=new_pipe,step_num=e,
                            module=mod[0],function=choices[int(c)][1],
                            description=form.cleaned_data['description'], output=form.cleaned_data['output'])
            return JsonResponse({'step_nums':step_nums_int,"forms":forms,'status':alert,'pipe_form':pipeline_form.as_p()},status=200)
        elif request.POST.get('ajax_type')=="select_modules":
            description=request.POST.get('ajax_description')
            using_module=request.POST.get('ajax_module')
            step=request.POST.get('ajax_step')
            step=int(step[step.index(" "):])
            output=request.POST.get('ajax_output')
            data={'using_module':using_module,'description':description,
                                'output':output,'using_function':'0'}
            choices=tuple([(i,key) for i,key in enumerate(modules[int(using_module)].functions.keys())])
            form=RawStepCardForm(initial=data,mod_choices_param=mod_choices,choices_param=choices)
            return JsonResponse({'step_num':step,'form':form.as_p()},status=200)
        #elif request.POST.get('ajax_type')=="add_param_output":
        #    add_to_output
        #    return JsonResponse({'step_num':step,'form':form.as_p()},status=200)
    elif request.method == 'POST':
            submit_form = RawStepCardFormSubmit(request.POST)
            if submit_form.is_valid():
                title=request.POST.get('title')
                slug=slugify(title)
                print(slug)
                return redirect('/pipeline_completion/'+slug+'/')
    new_step=step_tracker.objects.create(step=0)
    new_step.save()
    request.session.__setitem__('id', new_step.pk)
    request.session.__setitem__('forms', [])
    submit_form=RawStepCardFormSubmit()



    context={'active_view':'pipelines','form':submit_form}
    template_name="importJupyter/pipeline.html"
    return render(request,template_name,context)
@login_required(login_url="/login/")
def documentation(request):
    context={'active_view':'documentation'}
    template_name="importJupyter/documentation.html"
    doc_list=[]
    doc_posts=DocumentationPosts.objects.all()
    for post in doc_posts:
        doc_list.append({
            'title':post.title,
            'post_content':post.content,
            'url':post.get_post_url()
            })
    context['doc_list']=doc_list
    context['create_url']="/create_doc_post/"
    return render(request,template_name,context)
@login_required(login_url="/login/")
def view_doc_post(request,doc_slug=""):
    context={'active_view':'documentation'}
    template_name="importJupyter/doc_post.html"
    doc_post=DocumentationPosts.objects.filter(slug=doc_slug)
    if doc_post.exists():
        doc_images=DocumentationImage.objects.filter(post=doc_post[0])
        context['post']={
        'title':doc_post[0].title,
        'content':doc_post[0].content,
        'user':doc_post[0].user,
        'edit':doc_post[0].get_edit_url(),
        'images':[{'url':im.image.url,'caption':im.caption} for im in doc_images]
        }
    return render(request,template_name,context)
@login_required(login_url="/login/")
def create_doc_post(request):
    context={'active_view':'documentation'}
    template_name="importJupyter/create_doc_post.html"
    form=DocumentationPostsForm()
    if request.method=="POST":
        form=DocumentationPostsForm(request.POST)
        if form.is_valid():
            form.save()
            form=DocumentationPostsForm()
    context['form']=form
    return render(request,template_name,context)
@login_required(login_url="/login/")
def edit_doc_post(request,doc_slug=""):
    context={'active_view':'documentation'}
    template_name="importJupyter/edit_doc_post.html"

    doc_post=DocumentationPosts.objects.filter(slug=doc_slug)
    if doc_post.exists():
        form=DocumentationPostsForm(data={'title':doc_post[0].title,'content':doc_post[0].content})
        imgs=DocumentationImage.objects.filter(post=doc_post[0])
        im_list=[]
        if imgs.exists():
            for im in imgs:
                im_list.append(im.caption)
            context['images']=im_list
        print(request.POST)
        if request.method=="POST" and 'caption' in request.POST:
            print("hello9")
            success=False
            img_form=DocumentationImageForm(request.POST,request.FILES)
            if img_form.is_valid():
                img=img_form.save(commit=False)
                img.post=doc_post[0]
                img.image_number=len(im_list)+1
                img.save()
                success=True
                imgs=DocumentationImage.objects.filter(post=doc_post[0])
                im_list=[]
                if imgs.exists():
                    for im in imgs:
                        im_list.append(im.caption)
                    context['images']=im_list
        img_form=DocumentationImageForm()
        if request.method=="POST" and 'title' in request.POST:
            form=DocumentationPostsForm(request.POST,instance=doc_post[0])
            if form.is_valid():
                form.save()
                #print(form.cleaned_data.get('title'))
                #doc_post[0].title=form.cleaned_data.get('title')
                #doc_post[0].content=form.cleaned_data.get('content')
                #doc_post[0].save()
        context['form']=form
        context['img_form']=img_form
    return render(request,template_name,context)
@login_required(login_url="/login/")
def module_test_html_view(request,mod_slug=""):
    context={'active_view':'modlist'}
    template_name="importJupyter/module_html.html"
    nb=NotebookModel.objects.filter(name=mod_slug)
    if nb.exists():
        context['html_content']=nb[0].notebook_test_html
    return render(request,template_name,context)
@login_required(login_url="/login/")
def module_html_view(request,mod_slug=""):
    context={'active_view':'modlist'}
    template_name="importJupyter/module_html.html"
    nb=NotebookModel.objects.filter(name=mod_slug)
    if nb.exists():
        context['html_content']=nb[0].notebook_html
    return render(request,template_name,context)
@login_required(login_url="/login/")
def list_modules(request):
    template_name="importJupyter/module_list.html"
    modules=[]
    if request.user.is_authenticated:
        form=NotebookForm()
        #update_form=BooleanInput().as_p().replace('Form val','Update').replace('name="form_val"','name="update"')
        if request.method=='POST':
            form=NotebookForm(request.POST, request.FILES)
            #update_form=BooleanInput(request.POST).as_p().replace('Form val','Update').replace('name="form_val"','name="update"')
            if form.is_valid():
                if form.cleaned_data.get("update"):
                    #print(form.cleaned_data)
                    obj=NotebookModel.objects.get(name=slugify(form.cleaned_data.get('verbose_name')))
                    old_file=obj.notebook
                    old_test_file=obj.notebook_test
                    obj.notebook=form.cleaned_data.get('notebook')
                    obj.notebook_test=form.cleaned_data.get('notebook_test')
                    obj.save()
                    success=obj.save2()
                    if success!='success':
                        print('revert to old')
                        obj.notebook=old_file
                        obj.notebook_test=old_test_file
                        obj.save()
                        success=obj.save2()
                    print(success)
                else:
                    obj=form.save(commit=False)
                    obj.user=request.user
                    obj.save()
                    success=obj.save2()
                    print(success)
                    form=NotebookForm()
        text=request.GET.get('module_name')
        if request.is_ajax():
            if request.GET.get('ajax_type')=="func_info":
                text=text[text.index(":")+1:]
                modname=text[text.index("!")+1:]
                funcname=text[:text.index("!")]
                notebook=NotebookModel.objects.get(name=modname)
                descript=notebook.functions[funcname]
                print(modname,funcname,descript)
                return JsonResponse({'funcname':funcname,'funcdoc':descript,'mod_name':modname},status=200)
        notebooks=NotebookModel.objects.all()
        if notebooks.exists():
            for nb in notebooks:
                functions=[*nb.functions.keys()]
                modules.append({
                'name':nb.verbose_name,
                'slug_name':nb.name,
                'notebook_html':nb.get_complete_notebook_url(),
                'notebook_test_html':nb.get_complete_notebook_test_url(),
                'first_func':nb.functions[functions[0]],
                'description':nb.description,
                'functions':functions,
                })
    context={'mod_list':modules,'active_view':'modlist','form':form}
    return render(request,template_name,context)
