import decimal
import io
import os
import locale
import pathlib

import shutil

from django.contrib import admin, messages
from django.shortcuts import render, redirect
from import_export import resources
import collections
from import_export.admin import (ExportActionMixin, ImportExportMixin,
                                 ImportExportModelAdmin, ImportMixin)
from import_export.fields import Field

from core.forms import (BookCustomConfirmImportForm, BookCustomImportForm,
                        TaskCustomConfirmImportForm, TaskCustomImportForm)
from core.models import Author, Book, Category, Choice, Question, Task, TaskReport

from PyPDF2 import PdfFileWriter, PdfFileReader, PdfFileMerger
from pathlib import Path
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from django.conf import settings


# def get_export_queryset(self, request):
#         """
#         Bla bla bla
#         Returns export queryset.
#         Default implementation respects applied search and filters.
#         """
#         list_display = self.get_list_display(request)
#         list_display_links = self.get_list_display_links(request, list_display)
#         list_filter = self.get_list_filter(request)
#         search_fields = self.get_search_fields(request)
#         if self.get_actions(request):
#             list_display = ['action_checkbox'] + list(list_display)

#         ChangeList = self.get_changelist(request)
#         cl = ChangeList(request, self.model, list_display,
#                         list_display_links, list_filter, self.date_hierarchy,
#                         search_fields, self.list_select_related, self.list_per_page,
#                         self.list_max_show_all, self.list_editable, self, None
#                         )

#         return cl.get_queryset(request)
    
    
class BookResource(resources.ModelResource):
    
    class Meta:
        model = Book
        use_transactions = True
    
    def import_data(self, *args, **kwargs):
        self.user = kwargs.get("user") # Here, we are assigning the requested user to the `ModelResource` object.
        data = super().import_data(*args, **kwargs)
        return data

    def skip_row(self, instance, original):
        # You can access the current logged-in user by `self.user`
        # and later, do some logical operations
        # and at last, return either `True` or `False`
        pass

# class BookAdmin(ExportActionMixin, admin.ModelAdmin):
#     resource_class = BookResource

# class BookAdmin(ImportExportModelAdmin):
#     resource_class = BookResource


def is_time(timee):
    if timee and len(timee.split("-")) == 2:
        try: 
            timee = timee.split("-")
            int(timee[0].split(":")[0])
            int(timee[1].split(":")[0])
            return True
        except:
            return False
    else:
        return False
    
def worked(start, end, paused=0):
    # print("{} - {} - {}".format(end, start, paused))
    h = str(end).split(":")
    h = h if len(h) > 1 else str(end).split(".")
    end = (int(h[0]) if int(h[0]) > 0 else 24) + (int(h[1])/60)
    h = str(start).split(":")
    h = h if len(h) > 1 else str(start).split(".")
    start = int(h[0]) + (int(h[1])/60)
    # print("{} - {} - {} = {}\n".format(end, start, float(paused), end - start - float(paused)))
    return end - start - float(paused)
    
class BookCustomAdmin(ImportMixin, admin.ModelAdmin):
    resource_class = BookResource

    def get_import_form(self):
        return BookCustomImportForm

    def get_confirm_import_form(self):
        return BookCustomConfirmImportForm

    def get_form_kwargs(self, form, *args, **kwargs):
        # pass on `author` to the kwargs for the custom confirm form
        if isinstance(form, BookCustomImportForm):
            if form.is_valid():
                author = form.cleaned_data['author']
                kwargs.update({'author': author.id})
        return kwargs
    
class TaskReportResource(resources.ModelResource):
    
    class Meta:
        model = TaskReport
        fields = ('task', 'worked', 'site')
        

def empty_database(modeladmin, request, queryset):
    print("Empty Database")
    Task.objects.all().delete()
    TaskReport.objects.all().delete()
    messages.add_message(request, messages.INFO, "Database Empty Operation Successful: You can import new records....")
    return redirect('/admin/core/task/',)
    
empty_database.short_description = 'Empty Database'

    
def export_grouped_summary(modeladmin, request, queryset):
    print("Group Export Summary")
    for s in Task.objects.all().values_list('site',flat=True).distinct():
        export_summary(modeladmin, request, Task.objects.filter(site=s), True)
    
    return redirect('/admin/core/taskreport/',)
    
export_grouped_summary.short_description = 'Group Export Summary'

    
def export_summary(modeladmin, request, queryset, is_custom=False):
    print("Export Summary")
    if request.method == "POST":
        print(".......... Post")
    else:
        print(".......... Get")
    
    # print("**** {} Queryset".format(len(queryset)))
    tasks = {}
    sites = set()
    y = 0
    for q in queryset:
        y += 1
        print(y)
        sites.add(q.site)
        for x in range(1, 21):
            worked = getattr(q, "worked_{}".format(x), "")
            if worked > 0:
                t = getattr(q, "tatigkeit_{}".format(x), "")
                t = t.strip() if t else ""
                tasks[t] = worked + tasks[t] if t in tasks.keys() else worked
                    
    if not is_custom:
        TaskReport.objects.all().delete()
        
    TaskReport.objects.bulk_create([TaskReport(**{'site' : ", ".join(list(sites)), 'task': t[0], 'worked': t[1]}) for t in tasks.items()])
    # print(len(TaskReport.objects.all()))
    
    return redirect('/admin/core/taskreport/',)
    
export_summary.short_description = 'Export Summary'


def save_page(packet, can, file_name, pages):
    template_path = "{}/{}/{}".format(settings.MEDIA_ROOT, "TEMPLATES", "InvoiceTemplate.pdf")
    
    print("************* {}".format(file_name))
    can.save()
    # move to the beginning of the StringIO buffer
    packet.seek(0)


    # create a new PDF with Reportlab
    new_pdf = PdfFileReader(packet)
    # read your existing PDF
    existing_pdf = PdfFileReader(str(template_path))
    output = PdfFileWriter()
    # add the "watermark" (which is the new pdf) on the existing page
    page = existing_pdf.getPage(0)
    page.mergePage(new_pdf.getPage(0))
    output.addPage(page)
    # finally, write "output" to a real file

    FOLDER_PATH = "{}/{}".format(settings.MEDIA_ROOT, "INVOICES")
    
    outputStream = open(file_name, "wb")
    output.write(outputStream)
    outputStream.close()
    
    if pages > 1:
        first_name = "{}.pdf".format(file_name[:len(file_name)-7])
        pdf_merger = PdfFileMerger()
        pdf_merger = PdfFileMerger()
        pdf_merger.append(first_name)
        pdf_merger.append(file_name)
        with Path("{}-m.pdf".format(file_name[:len(file_name)-7])).open(mode="wb") as output_file:
            pdf_merger.write(output_file)
        
        f = pathlib.Path(first_name)
        f.unlink()
        f = pathlib.Path(file_name)
        f.unlink()
        f = pathlib.Path("{}-m.pdf".format(file_name[:len(file_name)-7]))
        os.rename(f, first_name)
        
        return first_name
    
    
def get_total(content):
    res = {"ub": 0, "fahrtkosten": 0, "hours": 0}
    for c in content:
        res["ub"] += c["ub"]
        res["fahrtkosten"] += c["fahrtkosten"]
        res["hours"] += c["hours"]
    return res

    
def generate_invoice(modeladmin, request, queryset, is_custom=False):
    print("Generate Invoice")
    FOLDER = "{}/{}/".format(settings.MEDIA_ROOT, "INVOICES")
    # FOLDER = "INVOICES"
    if request.method == "POST":
        print(".......... Post")
    else:
        print(".......... Get")
    
    # First empty the folder
    for filename in os.listdir(FOLDER):
        file_path = os.path.join(FOLDER, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            print('Failed to delete %s. Reason: %s' % (file_path, e))
        
        
    # print("**** {} Queryset".format(len(queryset)))
    
    contents = {}
    
    locale.setlocale(locale.LC_ALL, 'de_DE')
    for dat in Task.objects.all().values_list('datum', flat=True).distinct():
        
        queryset = Task.objects.filter(datum=dat).order_by('name')
        
        # content_ = {"2021-09-28": [{"label": "Container: koppeln", "name": "Clemens von Behren", "hours": 5.0}],}
        
        tasks = []
        # sites = set()
        y = 0
        
        for q in queryset:
            y += 1
            # print(y)
            # sites.add(q.site)
            for x in range(1, 21):
                worked = getattr(q, "worked_{}".format(x), "")
                if worked > 0:
                    t = getattr(q, "tatigkeit_{}".format(x), "")
                    t = t.strip() if t else ""
                    
                    res = next((sub for sub in tasks if sub['name'] == q.name and sub["label"] == t), None)
                    
                    if res:
                        for sub in tasks:
                            if sub['name'] == q.name and sub["label"] == t:
                                sub['hours'] = worked + res["hours"]
                                break
                    else:
                        tasks.append({"label": t, "name": q.name, "hours": worked, "fahrtkosten": 0, "km": "", "beschreibung": "", "ub": 0})
                    
                    res = next((sub for sub in tasks if sub['name'] == q.name and sub["label"] == t), None)
        
            if q and len(tasks) > 0:
                    
                if q.km or q.fahrtkosten or q.beschreibung:
                    print("*****************1************************ {}".format(q.name))
                    print(q.id)
                    print(q.name)
                    print(q.fahrtkosten)
                    print(q.km)
                    print(q.beschreibung)
                tasks[-1]["fahrtkosten"] = q.fahrtkosten
                tasks[-1]["km"] = q.km if q.km else ""
                tasks[-1]["beschreibung"] = q.beschreibung if q.beschreibung else ""
        
                tasks[-1]["ub"] = q.ub
                    
        contents[dat.strftime("%d.%m.%Y")] = tasks
       
    maxi = 19
    x_line_a = 50
    x_line_b = 390
    x_line_c = 440
    x_line_d = 525
    y_line = 485
    line_diff = -17
    multi_pages = set()
    font_size = 8
    font_name = "Helvetica"
        
    packet = io.BytesIO()
    can = canvas.Canvas(packet, pagesize=letter)
    can.setFont(font_name, font_size)
    
    for key in contents.keys():
        content = contents[key]
        
        if key == "20.10.2021":
            print()
        pages = 1
        lower_counter = 0
        
        x = 0
        extra_line = 0
        is_saved = False
        for c in content:
            can.drawString(x_line_a, y_line+((extra_line + x)*line_diff), c["label"])
            can.drawString(x_line_b, y_line+((extra_line + x)*line_diff), str(key))
            can.drawString(x_line_c, y_line+((extra_line + x)*line_diff), c["name"])
            can.drawString(x_line_d, y_line+((extra_line + x)*line_diff), locale.format('%.2f', c["hours"], 1))
            
            if c["fahrtkosten"] or c["km"] or c["beschreibung"]:
                print("[{}, {}], lower_counter={}, line_diff={}".format(50, 143+(lower_counter*line_diff), lower_counter, line_diff))
                xx = 50
                yy = 143+(lower_counter*line_diff)
                
                # If it has printed upto 6 lines, need to move to the next column
                if lower_counter >= 6:
                    xx = 319
                    ls = lower_counter - 6
                    yy = 143+(ls*line_diff)
                    
                can.drawString(xx, yy, "{}: {}{} {}".format(c["name"], c["fahrtkosten"], c["km"], c["beschreibung"]))
                lower_counter += 1
                
                
            x += 1
            if (extra_line + x) >= (maxi * pages):
                lower_counter = 0
                multi = save_page(packet, can, "{}{}{}.pdf".format(FOLDER, key, "--{}".format(pages) if pages > 1 else ""), pages)
                if multi:
                    multi_pages.add(multi)
                x = 0
                extra_line = 0
                
                packet = io.BytesIO()
                can = canvas.Canvas(packet, pagesize=letter)
                can.setFont(font_name, font_size)
                
                pages += 1
                is_saved = True
        
        if not is_saved:
            multi = save_page(packet, can, "{}{}{}.pdf".format(FOLDER, key, "--{}".format(pages) if pages > 1 else ""), pages)
            if multi:
                multi_pages.add(multi)
            x = 0
            
            packet = io.BytesIO()
            can = canvas.Canvas(packet, pagesize=letter)
            can.setFont(font_name, font_size)
            
            pages += 1
            is_saved = True
        
    for key in multi_pages:
        print("***********  {}".format(key))
        
        # read your existing PDF
        existing_pdf = PdfFileReader(key)
        output = PdfFileWriter()

        total = existing_pdf.getNumPages()
        # Watermark all the pages
        for x in range(1, total+1):
            packet = io.BytesIO()
            can = canvas.Canvas(packet, pagesize=letter)
            can.setFont(font_name, font_size)
            can.drawString(525, 768, "Page {} of {}".format(x, total))
            can.save()

            # move to the beginning of the StringIO buffer
            packet.seek(0)

            # create a new PDF with Reportlab
            new_pdf = PdfFileReader(packet)
            
            page = existing_pdf.getPage(x-1)
            page.mergePage(new_pdf.getPage(0))
            output.addPage(page)

        # finally, write "output" to a real file
        outputStream = open("{}-temp.pdf".format(key[:len(key)-4]), "wb")
        output.write(outputStream)
        outputStream.close()
        
        # Rename and Delete
        f = pathlib.Path(key)
        f.unlink()
        f = pathlib.Path("{}-temp.pdf".format(key[:len(key)-4]))
        os.rename(f, key)
        
    # Create Summary Page
    template_path = "{}/{}/{}".format(settings.MEDIA_ROOT, "TEMPLATES", "SummaryPageTemplate.pdf")
    packet = io.BytesIO()
    can = canvas.Canvas(packet, pagesize=letter)
    can.setFont("Helvetica", 11)

    yy = 664
    line_gap = -15
    x = 0
    total_ub = 0
    total_hours = 0
    total_fahrtkosten = 0
    for key in contents.keys():
        content = contents[key]
        res = get_total(content)
        
        total_ub += res["ub"]
        total_hours += res["hours"]
        total_fahrtkosten += res["fahrtkosten"]
        
        can.drawString(42, yy+(line_gap*x), "{}".format(x+1))
        can.drawString(64, yy+(line_gap*x), "{}.pdf".format(key))
        can.drawString(302, yy+(line_gap*x), key)
        can.drawString(366, yy+(line_gap*x), locale.format('%.2f', res["hours"], 1))
        can.drawString(434, yy+(line_gap*x), locale.format('%.2f', res["ub"], 1))
        can.drawString(478, yy+(line_gap*x), locale.format('%.2f', res["fahrtkosten"], 1))
        
        x += 1

    can.drawString(100, 760, locale.format('%.2f', total_ub, 1))
    can.drawString(120, 738, locale.format('%.2f', total_hours, 1))
    can.drawString(160, 716, locale.format('%.2f', total_fahrtkosten, 1))
    
    can.save()

    packet.seek(0)


    # create a new PDF with Reportlab
    new_pdf = PdfFileReader(packet)
    # read your existing PDF
    existing_pdf = PdfFileReader(str(template_path))
    output = PdfFileWriter()
    # add the "watermark" (which is the new pdf) on the existing page
    page = existing_pdf.getPage(0)
    page.mergePage(new_pdf.getPage(0))
    output.addPage(page)
    # finally, write "output" to a real file

    outputStream = open("{}SummaryPage.pdf".format(FOLDER), "wb")
    output.write(outputStream)
    outputStream.close()
    
    # Create a Zip of All the files
    zip = shutil.make_archive("All", 'zip', FOLDER)
    shutil.move(zip, "{}/{}.zip".format(FOLDER, "All"))

generate_invoice.short_description = 'Generate Invoice'


class TaskResource(resources.ModelResource):
    
    class Meta:
        model = Task
        use_transactions = True
        import_id_fields = ('id',)
        skip_unchanged = True
        report_skipped = True   # whether skipped records appear in the import Result object, and if using the admin whether skipped records will show in the import preview page
        total_hours_worked = Field()

        ass = Field(attribute='ass', column_name='A/S') 
        # split_start = Field(column_name='split_start')
        # split_end = Field(column_name='split_end')

        fields = ('id', 'name', 'kunde', 'ass', 'r', 'x', 'datum', 'ub', 'spesen', 'site', 'worker', 
                  'start', 'end', 'pause', 'cal_pause', 'hours_worked', 'cal_hours_worked', 'fahrtkosten', 'beschreibung', 'km', 
                  'zeitraum_1', 'tatigkeit_1', 'zeitraum_2', 'tatigkeit_2', 'zeitraum_3', 'tatigkeit_3', 
                  'zeitraum_4', 'tatigkeit_4', 'zeitraum_5', 'tatigkeit_5', 'zeitraum_6', 'tatigkeit_6', 
                  'zeitraum_7', 'tatigkeit_7', 'zeitraum_8', 'tatigkeit_8', 'zeitraum_9', 'tatigkeit_9', 
                  'zeitraum_10', 'tatigkeit_10', 'zeitraum_11', 'tatigkeit_11', 'zeitraum_12', 'tatigkeit_12', 
                  'zeitraum_13', 'tatigkeit_13', 'zeitraum_14', 'tatigkeit_14', 'zeitraum_15', 'tatigkeit_15', 
                  'zeitraum_16', 'tatigkeit_16', 'zeitraum_17', 'tatigkeit_17', 'zeitraum_18', 'tatigkeit_18', 
                  'zeitraum_19', 'tatigkeit_19', 'zeitraum_20', 'tatigkeit_20', 
                  )
        export_order = ('id', 'name', 'kunde', 'ass', 'r', 'x', 'datum', 'ub', 'spesen', 'site', 'worker', 'start', 'end', 'pause', 
                        'cal_pause', 'hours_worked', 'cal_hours_worked', 'fahrtkosten', 'beschreibung', 'km', 
                        'zeitraum_1', 'tatigkeit_1', 'zeitraum_2', 'tatigkeit_2', 'zeitraum_3', 'tatigkeit_3', 
                        'zeitraum_4', 'tatigkeit_4', 'zeitraum_5', 'tatigkeit_5', 'zeitraum_6', 'tatigkeit_6', 
                        'zeitraum_7', 'tatigkeit_7', 'zeitraum_8', 'tatigkeit_8', 'zeitraum_9', 'tatigkeit_9', 
                        'zeitraum_10', 'tatigkeit_10', 'zeitraum_11', 'tatigkeit_11', 'zeitraum_12', 'tatigkeit_12', 
                        'zeitraum_13', 'tatigkeit_13', 'zeitraum_14', 'tatigkeit_14', 'zeitraum_15', 'tatigkeit_15', 
                        'zeitraum_16', 'tatigkeit_16', 'zeitraum_17', 'tatigkeit_17', 'zeitraum_18', 'tatigkeit_18', 
                        'zeitraum_19', 'tatigkeit_19', 'zeitraum_20', 'tatigkeit_20', 
        )
        
        # widgets = {'datum': {'format': '%d/%m/%Y'},}
            
        def dehydrate_ass(self, tasks):
            return '....: %s' % (tasks.ass)
        
        # def dehydrate_split_start(self, book):
        #     return '%s by %s' % (book.name, book.author.name)
        
        # def dehydrate_split_end(self, book):
        #     return '%s by %s' % (book.name, book.author.name)

        use_transactions = True
    
    # def get_export_headers(self):
    #     # from django.utils.encoding import force_str
    #     # hs = [force_str(field.column_name) for field in self.get_export_fields()]
    #     headers = []
    #     print("............. Headers****")
    #     for field in self.get_fields():
    #         headers.append(self.Meta.model._meta.get_field(field.column_name).verbose_name)
    #         # model_fields = self.Meta.model._meta.get_fields()
    #         # header = next((x.verbose_name for x in model_fields if x.name == field.column_name), field.column_name)
    #         # headers.append(header)
        
    #     # for field in self.get_fields():
    #     #     for col in self.Meta.model._meta.dict['_field_name_cache']:
    #     #         # if (col.dict['name']==field.column_name):
    #     #         headers.append(col.dict['verbose_name'])
    #     #         print(headers)
    
    #     # headers = [force_str(field.column_name) for field in self.get_export_fields()]
        
    #     return headers
        
    def before_save_instance(self, instance, using_transactions, dry_run):
        # instance.geom = Point(float(instance.longitude), float(instance.latitude))
        instance.worked_hours = worked(instance.start, instance.end, instance.pause)
        
        # print(" ID: {}  ****** {}".format(instance.id, instance))
        paused = 0.0
        hw = 0.0
        
        for x in range(1, 21):
            timeee = getattr(instance, "zeitraum_{}".format(x), "")
            
            try:
                w = 0.0 if timeee is None else float(timeee)
                is_timee = True
            except ValueError:
                is_timee = is_time(timeee)
                timee = timeee.split("-") if is_timee else ["0:0", "0:0"]
                w = worked(timee[0], timee[1], 0)
            
            hw += w
            t = getattr(instance, "tatigkeit_{}".format(x), "")
            setattr(instance, "tatigkeit_{}".format(x), t if t is None else t.strip())
            
            t = t if t else ""
            is_paused = t.lower() in ['pause', 'paused']
            
            # print(" ID: {}, Worked: {}, Is Paused: {}  ****** {}".format(instance.id, w, is_paused, instance))
            if is_timee and not is_paused:
                setattr(instance, "worked_{}".format(x), w)
            elif is_paused and is_timee:
                paused = paused + w
                
        instance.cal_pause = paused
        instance.cal_hours_worked = hw
        instance.site = instance.site.strip()
        instance.name = instance.name.strip()
        
        if paused != instance.pause:
            print("ID: {} *********************** Calculated {} != imported Paused {}".format(instance.id, paused, instance.pause))
        return instance
    
    def import_data(self, *args, **kwargs):
        self.user = kwargs.get("user") # Here, we are assigning the requested user to the `ModelResource` object.
        data = super().import_data(*args, **kwargs)
        
        return data

    def skip_row(self, instance, original):
        # You can access the current logged-in user by `self.user`
        # and later, do some logical operations
        # and at last, return either `True` or `False`
        pass


class ExportTaskCustomAdmin(ExportActionMixin, admin.ModelAdmin):
    pass


# class TaskAdmin(ImportExportModelAdmin):
# class TaskCustomAdmin(ImportMixin, admin.ModelAdmin):
class TaskCustomAdmin(ImportExportMixin, admin.ModelAdmin):
    list_per_page = 500
    list_display = ('id', 'name', 'kunde', 'ass', 'r', 'x', 'datum', 'ub', 'spesen', 'site', 'worker', 'start', 'end', 'pause', 'cal_pause', 
                        'hours_worked', 'cal_hours_worked', 'fahrtkosten', 'beschreibung', 'km', 
                        'zeitraum_1', 'tatigkeit_1', 'worked_1', 'zeitraum_2', 'worked_2', 'tatigkeit_2', 'zeitraum_3', 'worked_3', 'tatigkeit_3', 
                        'zeitraum_4', 'worked_4', 'tatigkeit_4', 'zeitraum_5', 'worked_5', 'tatigkeit_5', 'zeitraum_6', 'worked_6', 'tatigkeit_6', 
                        'zeitraum_7', 'worked_7', 'tatigkeit_7', 'zeitraum_8', 'worked_8', 'tatigkeit_8', 'zeitraum_9', 'worked_9', 'tatigkeit_9', 
                        'zeitraum_10', 'worked_10', 'tatigkeit_10', 'zeitraum_11', 'worked_11', 'tatigkeit_11', 'zeitraum_12', 'worked_12', 'tatigkeit_12', 
                        'zeitraum_13', 'worked_13', 'tatigkeit_13', 'zeitraum_14', 'worked_14', 'tatigkeit_14', 'zeitraum_15', 'worked_15', 'tatigkeit_15', 
                        'zeitraum_16', 'worked_16', 'tatigkeit_16', 'zeitraum_17', 'worked_17', 'tatigkeit_17', 'zeitraum_18', 'worked_18', 'tatigkeit_18', 
                        'zeitraum_19', 'worked_19', 'tatigkeit_19', 'zeitraum_20', 'worked_20', 'tatigkeit_20', 
        )
    search_fields = ['name', 'kunde', 'ass', 'r', 'x', 'datum', 'ub', 'spesen', 'site', 'worker', 'fahrtkosten', 'beschreibung', 'km', 
                     'tatigkeit_1', 'tatigkeit_2', 'tatigkeit_3', 'tatigkeit_4', 'tatigkeit_5', 'tatigkeit_6', 'tatigkeit_7', 'tatigkeit_8', 
                     'tatigkeit_9', 'tatigkeit_10', 'tatigkeit_11', 'tatigkeit_12', 'tatigkeit_13', 'tatigkeit_14', 'tatigkeit_15', 
                     'tatigkeit_16', 'tatigkeit_17', 'tatigkeit_18', 'tatigkeit_19', 'tatigkeit_20', ]
    ordering = ('id', 'name', 'kunde', 'ass', 'r', 'x', 'datum', 'site', 'worker', 'hours_worked', 'fahrtkosten', 'beschreibung', 'km',
                'tatigkeit_1', 'worked_1', 'tatigkeit_2', 'worked_2', 'tatigkeit_3', 'worked_3', 'tatigkeit_4', 'worked_4', 'tatigkeit_5', 'worked_5', 
                'tatigkeit_6', 'worked_6', 'tatigkeit_7', 'worked_7', 'tatigkeit_8', 'worked_8', 'tatigkeit_9', 'worked_9', 'tatigkeit_10', 'worked_10', 
                'tatigkeit_11', 'worked_11', 'tatigkeit_12', 'worked_12',  'tatigkeit_13', 'worked_13',  'tatigkeit_14', 'worked_14',  'tatigkeit_15', 'worked_15',
                'tatigkeit_16', 'worked_16',  'tatigkeit_17', 'worked_17',  'tatigkeit_18', 'worked_18',  'tatigkeit_19', 'worked_19',  'tatigkeit_20', 'worked_20', )
    list_filter = ('site', 'name', 'kunde', 'datum', 'worker', 'fahrtkosten', 'beschreibung', 'tatigkeit_1', 'tatigkeit_2', 'tatigkeit_3', 'tatigkeit_4', 'tatigkeit_5', 
                   'tatigkeit_6', 'tatigkeit_7', 'tatigkeit_8', 'tatigkeit_9', 'tatigkeit_10', 'tatigkeit_11', 'tatigkeit_12', 'tatigkeit_13', 'tatigkeit_14', 'tatigkeit_15',
                   'tatigkeit_16', 'tatigkeit_17', 'tatigkeit_18', 'tatigkeit_19', 'tatigkeit_20')
    actions = [empty_database, generate_invoice, export_summary, export_grouped_summary, ]
    resource_class = TaskResource
    

    def get_import_form(self):
        return TaskCustomImportForm

    def get_confirm_import_form(self):
        return TaskCustomConfirmImportForm

    def get_form_kwargs(self, form, *args, **kwargs):
        # pass on `author` to the kwargs for the custom confirm form
        # if isinstance(form, TaskCustomImportForm):
        #     if form.is_valid():
        #         author = form.cleaned_data['author']
        #         kwargs.update({'author': author.id})
        return kwargs
    
class TaskReportCustomAdmin(ExportActionMixin, admin.ModelAdmin):
    list_per_page = 500
    list_display = ('worked', 'task', 'site',)
    list_filter = ('site', )
    ordering = ('site','task',)
    
    resource_class = TaskReportResource

    def get_confirm_import_form(self):
        return TaskCustomConfirmImportForm

    def get_form_kwargs(self, form, *args, **kwargs):
        return kwargs
    


# Register your models here.
# admin.site.register(Question)
# admin.site.register(Choice)

# admin.site.register(Author)
# # admin.site.register(Book, BookAdmin)
# admin.site.register(Book, BookCustomAdmin)
# admin.site.register(Category)


admin.site.register(TaskReport, TaskReportCustomAdmin)

# admin.site.register(Task, TaskAdmin)
admin.site.register(Task, TaskCustomAdmin)
# admin.site.register(Task, ExportTaskCustomAdmin)
# admin.site.register(Task, ImportTaskCustomAdmin)

