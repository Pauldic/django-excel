import django_excel as excel
from _compact import JsonResponse
from django import forms
from django.http import HttpResponse, HttpResponseBadRequest, Http404
from django.shortcuts import redirect, render
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
import subprocess, shlex, re
from core.models import Choice, Question
import os
import shutil
from django.conf import settings
from django.core.files.storage import FileSystemStorage
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout


data = [[1, 2, 3], [4, 5, 6]]

class UploadFileForm(forms.Form):
    file = forms.FileField()


# Create your views here.....
def upload(request):
    if request.method == "POST":
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            filehandle = request.FILES["file"]
            return excel.make_response(
                filehandle.get_sheet(), "csv", file_name="download"
            )
    else:
        form = UploadFileForm()
    return render(
        request,
        "upload_form.html",
        {
            "form": form,
            "title": "Excel file upload and download example",
            "header": (
                "Please choose any excel file "
                + "from your cloned repository:"
            ),
        },
    )


def download(request, file_type):
    sheet = excel.pe.Sheet(data)
    return excel.make_response(sheet, file_type)


def download_as_attachment(request, file_type, file_name):
    return excel.make_response_from_array(data, file_type, file_name=file_name)


def export_data(request, atype):
    if atype == "sheet":
        return excel.make_response_from_a_table(
            Question, "xls", file_name="sheet"
        )
    elif atype == "book":
        return excel.make_response_from_tables(
            [Question, Choice], "xls", file_name="book"
        )
    elif atype == "custom":
        question = Question.objects.get(slug="ide")
        query_sets = Choice.objects.filter(question=question)
        column_names = ["choice_text", "id", "votes"]
        return excel.make_response_from_query_sets(
            query_sets, column_names, "xls", file_name="custom"
        )
    else:
        return HttpResponseBadRequest(
            "Bad request. please put one of these "
            + "in your url suffix: sheet, book or custom"
        )


def import_data(request):
    if request.method == "POST":
        form = UploadFileForm(request.POST, request.FILES)

        def choice_func(row):
            q = Question.objects.filter(slug=row[0])[0]
            row[0] = q
            return row

        if form.is_valid():
            request.FILES["file"].save_book_to_database(
                models=[Question, Choice],
                initializers=[None, choice_func],
                mapdicts=[
                    ["question_text", "pub_date", "slug"],
                    {"Question": "question", "Choice": "choice_text", "Votes": "votes"},
                ],
            )
            return redirect("handson_view")
        else:
            return HttpResponseBadRequest()
    else:
        form = UploadFileForm()
    return render(
        request,
        "upload_form.html",
        {
            "form": form,
            "title": "Import excel data into database example",
            "header": "Please upload sample-data.xls:",
        },
    )


def import_sheet(request):
    if request.method == "POST":
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            request.FILES["file"].save_to_database(
                name_columns_by_row=2,
                model=Question,
                mapdict=["question_text", "pub_date", "slug"],
            )
            return HttpResponse("OK")
        else:
            return HttpResponseBadRequest()
    else:
        form = UploadFileForm()
    return render(request, "upload_form.html", {"form": form})


def exchange(request, file_type):
    form = UploadFileForm(request.POST, request.FILES)
    if form.is_valid():
        filehandle = request.FILES["file"]
        return excel.make_response(filehandle.get_sheet(), file_type)
    else:
        return HttpResponseBadRequest()


def parse(request, data_struct_type):
    form = UploadFileForm(request.POST, request.FILES)
    if form.is_valid():
        filehandle = request.FILES["file"]
        if data_struct_type == "array":
            return JsonResponse({"result": filehandle.get_array()})
        elif data_struct_type == "dict":
            return JsonResponse(filehandle.get_dict())
        elif data_struct_type == "records":
            return JsonResponse({"result": filehandle.get_records()})
        elif data_struct_type == "book":
            return JsonResponse(filehandle.get_book().to_dict())
        elif data_struct_type == "book_dict":
            return JsonResponse(filehandle.get_book_dict())
        else:
            return HttpResponseBadRequest()
    else:
        return HttpResponseBadRequest()


def handson_table(request):
    return excel.make_response_from_tables(
        [Question, Choice], "handsontable.html"
    )


def embed_handson_table(request):
    """
    Renders two table in a handsontable
    """
    content = excel.pe.save_book_as(
        models=[Question, Choice],
        dest_file_type="handsontable.html",
        dest_embed=True,
    )
    content.seek(0)
    return render(
        request,
        "custom-handson-table.html",
        {"handsontable_content": content.read()},
    )


def embed_handson_table_from_a_single_table(request):
    """
    Renders one table in a handsontable
    """
    content = excel.pe.save_as(
        model=Question, dest_file_type="handsontable.html", dest_embed=True
    )
    content.seek(0)
    return render(
        request,
        "custom-handson-table.html",
        {"handsontable_content": content.read()},
    )


def survey_result(request):
    question = Question.objects.get(slug="ide")
    query_sets = Choice.objects.filter(question=question)
    column_names = ["choice_text", "votes"]

    # Obtain a pyexcel sheet from the query sets
    sheet = excel.pe.get_sheet(
        query_sets=query_sets, column_names=column_names
    )
    sheet.name_columns_by_row(0)
    sheet.column.format("votes", int)

    # Transform the sheet into an svg chart
    svg = excel.pe.save_as(
        array=[sheet.column["choice_text"], sheet.column["votes"]],
        dest_file_type="svg",
        dest_chart_type="pie",
        dest_title=question.question_text,
        dest_width=600,
        dest_height=400,
    )

    return render(request, "survey_result.html", dict(svg=svg.read()))


def import_sheet_using_isave_to_database(request):
    if request.method == "POST":
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            request.FILES["file"].isave_to_database(
                model=Question, mapdict=["question_text", "pub_date", "slug"]
            )
            return HttpResponse("OK")
        else:
            return HttpResponseBadRequest()
    else:
        form = UploadFileForm()
    return render(request, "upload_form.html", {"form": form})


def import_data_using_isave_book_as(request):
    if request.method == "POST":
        form = UploadFileForm(request.POST, request.FILES)

        def choice_func(row):
            q = Question.objects.filter(slug=row[0])[0]
            row[0] = q
            return row

        if form.is_valid():
            request.FILES["file"].isave_book_to_database(
                models=[Question, Choice],
                initializers=[None, choice_func],
                mapdicts=[
                    ["question_text", "pub_date", "slug"],
                    {"Question": "question", "Choice": "choice_text", "Votes": "votes"},
                ],
            )
            return redirect("handson_view")
        else:
            return HttpResponseBadRequest()
    else:
        form = UploadFileForm()
    return render(
        request,
        "upload_form.html",
        {
            "form": form,
            "title": "Import excel data into database example",
            "header": "Please upload sample-data.xls:",
        },
    )


def import_without_bulk_save(request):
    if request.method == "POST":
        form = UploadFileForm(request.POST, request.FILES)

        def choice_func(row):
            q = Question.objects.filter(slug=row[0])[0]
            row[0] = q
            return row

        if form.is_valid():
            request.FILES["file"].save_book_to_database(
                models=[Question, Choice],
                initializers=[None, choice_func],
                mapdicts=[
                    ["question_text", "pub_date", "slug"],
                    ["question", "choice_text", "votes"],
                ],
                bulk_save=False,
            )
            return redirect("handson_view")
        else:
            return HttpResponseBadRequest()
    else:
        form = UploadFileForm()
    return render(
        request,
        "upload_form.html",
        {
            "form": form,
            "title": "Import excel data into database example",
            "header": "Please upload sample-data.xls:",
        },
    )


def site_work_summary(request):
    if request.method == "POST":
        print(".......... Post")
    else:
        print(".......... Get")
    
    
    
    return render(
        request,
        "task_site_summary_report.html",
        {
            "title": "Import excel data into database example",
            "header": "Please upload sample-data.xls:",
        },
    )
    

@login_required
def delete_invoices(request, file_name=None):
    if file_name:
        file_path="{}/{}/{}.pdf".format(settings.MEDIA_ROOT, "INVOICES", file_name)
        print(file_path)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
            return redirect("invoices")
        except Exception as e:
            print('Failed to delete %s. Reason: %s' % (file_path, e))
        raise Http404("File not Found")
    else:
        FOLDER = "{}/{}".format(settings.MEDIA_ROOT, "INVOICES")
        for filename in os.listdir(FOLDER):
            file_path = os.path.join(FOLDER, filename)
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
            except Exception as e:
                print('Failed to delete %s. Reason: %s' % (file_path, e))
    
        return redirect("invoices")
    

@login_required
def download_invoices(request, file_name="All.zip"):
    if file_name == "All.zip":
        file_path="{}/{}/{}".format(settings.MEDIA_ROOT, "INVOICES", file_name)
        print(file_path)
        if os.path.exists(file_path):
            with open(file_path, 'rb') as fh:
                response = HttpResponse(fh.read(), content_type="application/zip")
                response['Content-Disposition'] = 'inline; filename=Generated Invoices.zip'
                return response
    else:
        file_path="{}/{}/{}.pdf".format(settings.MEDIA_ROOT, "INVOICES", file_name)
        print(file_path)
        if os.path.exists(file_path):
            with open(file_path, 'rb') as fh:
                response = HttpResponse(fh.read(), content_type="application/pdf")
                response['Content-Disposition'] = 'inline; filename=' + os.path.basename(file_path)
                return response
    raise Http404("File not Found")
        

@login_required
def list_invoices(request):
    mypath="{}/{}".format(settings.MEDIA_ROOT, "INVOICES")
    only_files = [f for f in os.listdir(mypath) if os.path.isfile(os.path.join(mypath, f))]
    only_files = [x[:-4] for x in only_files if x != "All.zip"]

    only_files.sort()
    print(only_files)
    
    
    return render(
        request,
        "task_site_summary_report.html",
        # "upload_form.html",
        {
            "title": "Creablo SuperTool",
            "header": "Creablo",
            "files": only_files
        },
    )
    
      

@login_required
def templates_list(request, file_name=None):
    if file_name is not None and file_name not in ["SummaryPageTemplate.pdf", "InvoiceTemplate.pdf"]:
        raise Http404("File not Found")
    
    file_path = "{}/{}/{}".format(settings.MEDIA_ROOT, "TEMPLATES", file_name)
    print(file_path)
    if file_name and os.path.exists(file_path):
        with open(file_path, 'rb') as fh:
            response = HttpResponse(fh.read(), content_type="application/pdf")
            response['Content-Disposition'] = 'inline; filename=' + os.path.basename(file_path)
            return response
            
    mypath="{}/{}".format(settings.MEDIA_ROOT, "TEMPLATES")
    only_files = [f for f in os.listdir(mypath) if os.path.isfile(os.path.join(mypath, f))]
    
    return render(
        request,
        "template_list.html",
        {
            "title": "Creablo SuperTool",
            "header": "Creablo",
            "files": only_files
        },
    )
      
      
@login_required
def templates_upload(request, file_name):
    helo =file_name
    if file_name in ["SummaryPageTemplate.pdf", "InvoiceTemplate.pdf"]:
        if request.method == 'POST' and request.FILES['template'] and request.POST.get('name') in ["SummaryPageTemplate", "InvoiceTemplate"]:
            myfile = request.FILES['template']
            fs = FileSystemStorage()
            filename = request.POST.get('name')
            file_path = "{}/{}/{}.pdf".format(settings.MEDIA_ROOT, "TEMPLATES", filename)
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            saved = fs.save(file_path, myfile)
            # uploaded_file_url = fs.url(filename)
            messages.success(request, 'File Uploaded Successfully!!!')
            return redirect('templates' )
        return render(request, 'upload_form.html', {"name": file_name[:-4]})
    else:
        raise Http404("Page not Found")


    

@csrf_exempt
def git(request):
    
    # print("****Request From: {}".format(request.META['HTTP_HOST']))
    # if request.method == "POST":
    #     print(dict(request.POST.items()))
    #     print("..........2 Post")
    # else:
    #     print("..........1 Get")
    
    # print("**** Body   ....")
    # for key, value in request.POST.items():
    #     print("{}: {} \n".format(key, value))
    
    # print("**** Header....")
    # for key, value in request.headers.items():
    #     print("{}: {} \n".format(key, value))
    
    restart = False
    if request.method == "POST":
        git_cmd = 'git pull'
        # kwargs = {}
        # kwargs['stdout'] = subprocess.PIPE
        # kwargs['stderr'] = subprocess.PIPE
        # proc = subprocess.Popen(shlex.split(git_cmd), **kwargs)
        # (stdout_str, stderr_str) = proc.communicate()
        # (stdout_str, stderr_str) = proc.communicate()
        # return_code = proc.wait()

        output, error = subprocess.Popen(shlex.split(git_cmd), stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()
        
        if error:
            print("*********`{}` Comman Error***********".format(git_cmd))
            print(error.decode("utf-8"))
            
        if output:
            print("*********`{}` Comman Output***********".format(git_cmd))
            print(output.decode("utf-8"))
            res = re.search(r'([^\s]+)\.py', output.decode("utf-8"))
            restart = res and len(res.groups()) > 0
            
        
    # TODO: Restart if on Production
    if False and restart:
        print("\n--------Issued Service Restart After Git Update----------\n")
        print(subprocess.run(["sudo", "service", "uwsgi", "restart"]))
    return HttpResponse(status=204)
    

def logout_view(request):
    logout(request)
    return redirect('/admin')