from django.db import models
from django.utils.translation import ugettext as _
from django.urls import reverse


class Question(models.Model):
    question_text = models.CharField(max_length=200)
    pub_date = models.DateTimeField('date published')
    slug = models.CharField(max_length=10, unique=True,
                            default="question")

    def __str__(self):
        return self.question_text


class Choice(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    choice_text = models.CharField(max_length=200)
    votes = models.IntegerField(default=0)

    def __str__(self):
        return self.choice_text



class Author(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Category(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Book(models.Model):
    name = models.CharField('Book name', max_length=100)
    author = models.ForeignKey(Author, blank=True, null=True, on_delete=models.CASCADE)
    author_email = models.EmailField('Author email', max_length=75, blank=True)
    imported = models.BooleanField(default=False)
    published = models.DateField('Published', blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    categories = models.ManyToManyField(Category, blank=True)

    def __str__(self):
        return self.name
    
    
class Task(models.Model):
    mon = models.IntegerField('Mon', default=0)
    abg = models.CharField('Abg', max_length=255, blank=True, null=False)
    name = models.CharField('Name', max_length=255, blank=True, null=False)
    kunde = models.CharField('Kunde', max_length=255, blank=True, null=True)
    ass = models.CharField('A/S', max_length=255, blank=True, null=True)
    r = models.CharField('R', max_length=255, blank=True, null=True)
    x = models.CharField('X', max_length=255, blank=True, null=True)
    datum = models.DateField('Datum', max_length=255, blank=True, null=True)
    
    ub = models.DecimalField('Üb', max_digits=5, decimal_places=2, default=0.0)
    spesen = models.CharField('Spesen?', max_length=255, blank=True, null=True)
    site = models.CharField('Baustelle = Site', max_length=255, blank=True, null=True)
    worker = models.CharField('Bauleiter = Worker', max_length=255, blank=True, null=True)
    start = models.CharField('Start', max_length=16, blank=True, null=True)
    end = models.CharField('End', max_length=16, blank=True, null=True)
    pause = models.DecimalField('Pause', max_digits=5, decimal_places=2, default=0.0)
    cal_pause = models.DecimalField('Calculated Pause', max_digits=5, decimal_places=2, default=0.0)
    hours_worked = models.DecimalField('Gesamt = Hours Worked', max_digits=5, decimal_places=2, default=0.0)
    cal_hours_worked = models.DecimalField('Gesamt = Calculated Hours Worked', max_digits=5, decimal_places=2, default=0.0)
    
    fahrtkosten = models.DecimalField('Fahrtkosten', max_digits=5, decimal_places=2, default=0.0)
    km = models.CharField('€/km', max_length=8, blank=True, null=True)
    beschreibung = models.CharField('Fahrtkosten - Beschreibung', max_length=255, blank=True, null=True)
    
    zeitraum_1 = models.CharField('Zeitraum 1', max_length=16, blank=True, null=True)
    tatigkeit_1 = models.CharField('Tätigkeit 1', max_length=255, blank=True, null=True)
    worked_1 = models.DecimalField('HW 1', max_digits=5, decimal_places=2, default=0.0)
    zeitraum_2 = models.CharField('Zeitraum 2', max_length=16, blank=True, null=True)
    tatigkeit_2 = models.CharField('Tätigkeit 2', max_length=255, blank=True, null=True)
    worked_2 = models.DecimalField('HW 2', max_digits=5, decimal_places=2, default=0.0)
    zeitraum_3 = models.CharField('Zeitraum 3', max_length=16, blank=True, null=True)
    tatigkeit_3 = models.CharField('Tätigkeit 3', max_length=255, blank=True, null=True)
    worked_3 = models.DecimalField('HW 3', max_digits=5, decimal_places=2, default=0.0)
    zeitraum_4 = models.CharField('Zeitraum 4', max_length=16, blank=True, null=True)
    tatigkeit_4 = models.CharField('Tätigkeit 4', max_length=255, blank=True, null=True)
    worked_4 = models.DecimalField('HW 4', max_digits=5, decimal_places=2, default=0.0)
    zeitraum_5 = models.CharField('Zeitraum 5', max_length=16, blank=True, null=True)
    tatigkeit_5 = models.CharField('Tätigkeit 5', max_length=255, blank=True, null=True)
    worked_5 = models.DecimalField('HW 5', max_digits=5, decimal_places=2, default=0.0)
    zeitraum_6 = models.CharField('Zeitraum 6', max_length=16, blank=True, null=True)
    tatigkeit_6 = models.CharField('Tätigkeit 6', max_length=255, blank=True, null=True)
    worked_6 = models.DecimalField('HW 6', max_digits=5, decimal_places=2, default=0.0)
    zeitraum_7 = models.CharField('Zeitraum 7', max_length=16, blank=True, null=True)
    tatigkeit_7 = models.CharField('Tätigkeit 7', max_length=255, blank=True, null=True)
    worked_7 = models.DecimalField('HW 7', max_digits=5, decimal_places=2, default=0.0)
    zeitraum_8 = models.CharField('Zeitraum 8', max_length=16, blank=True, null=True)
    tatigkeit_8 = models.CharField('Tätigkeit 8', max_length=255, blank=True, null=True)
    worked_8 = models.DecimalField('HW 8', max_digits=5, decimal_places=2, default=0.0)
    zeitraum_9 = models.CharField('Zeitraum 9', max_length=16, blank=True, null=True)
    tatigkeit_9 = models.CharField('Tätigkeit 9', max_length=255, blank=True, null=True)
    worked_9 = models.DecimalField('HW 9', max_digits=5, decimal_places=2, default=0.0)
    zeitraum_10 = models.CharField('Zeitraum 10', max_length=16, blank=True, null=True)
    tatigkeit_10 = models.CharField('Tätigkeit 10', max_length=255, blank=True, null=True)
    worked_10 = models.DecimalField('HW 11', max_digits=5, decimal_places=2, default=0.0)
    zeitraum_11 = models.CharField('Zeitraum 11', max_length=16, blank=True, null=True)
    tatigkeit_11 = models.CharField('Tätigkeit 11', max_length=255, blank=True, null=True)
    worked_11 = models.DecimalField('HW 12', max_digits=5, decimal_places=2, default=0.0)
    zeitraum_12 = models.CharField('Zeitraum 12', max_length=16, blank=True, null=True)
    tatigkeit_12 = models.CharField('Tätigkeit 12', max_length=255, blank=True, null=True)
    worked_12 = models.DecimalField('HW 13', max_digits=5, decimal_places=2, default=0.0)
    zeitraum_13 = models.CharField('Zeitraum 13', max_length=16, blank=True, null=True)
    tatigkeit_13 = models.CharField('Tätigkeit 13', max_length=255, blank=True, null=True)
    worked_13 = models.DecimalField('HW 14', max_digits=5, decimal_places=2, default=0.0)
    zeitraum_14 = models.CharField('Zeitraum 14', max_length=16, blank=True, null=True)
    tatigkeit_14 = models.CharField('Tätigkeit 14', max_length=255, blank=True, null=True)
    worked_14 = models.DecimalField('HW 15', max_digits=5, decimal_places=2, default=0.0)
    zeitraum_15 = models.CharField('Zeitraum 15', max_length=16, blank=True, null=True)
    tatigkeit_15 = models.CharField('Tätigkeit 15', max_length=255, blank=True, null=True)
    worked_15 = models.DecimalField('HW 16', max_digits=5, decimal_places=2, default=0.0)
    zeitraum_16 = models.CharField('Zeitraum 16', max_length=16, blank=True, null=True)
    tatigkeit_16 = models.CharField('Tätigkeit 16', max_length=255, blank=True, null=True)
    worked_16 = models.DecimalField('HW 17', max_digits=5, decimal_places=2, default=0.0)
    zeitraum_17 = models.CharField('Zeitraum 17', max_length=16, blank=True, null=True)
    tatigkeit_17 = models.CharField('Tätigkeit 17', max_length=255, blank=True, null=True)
    worked_17 = models.DecimalField('HW 18', max_digits=5, decimal_places=2, default=0.0)
    zeitraum_18 = models.CharField('Zeitraum 18', max_length=16, blank=True, null=True)
    tatigkeit_18 = models.CharField('Tätigkeit 18', max_length=255, blank=True, null=True)
    worked_18 = models.DecimalField('HW 19', max_digits=5, decimal_places=2, default=0.0)
    zeitraum_19 = models.CharField('Zeitraum 19', max_length=16, blank=True, null=True)
    tatigkeit_19 = models.CharField('Tätigkeit 19', max_length=255, blank=True, null=True)
    worked_19 = models.DecimalField('HW 20', max_digits=5, decimal_places=2, default=0.0)
    zeitraum_20 = models.CharField('Zeitraum 20', max_length=16, blank=True, null=True)
    tatigkeit_20 = models.CharField('Tätigkeit 20', max_length=255, blank=True, null=True)
    worked_20 = models.DecimalField('HW 20', max_digits=5, decimal_places=2, default=0.0)
    
    class Meta:
        verbose_name = _("Task")
        verbose_name_plural = _("Tasks")

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("_detail", kwargs={"pk": self.pk})


class TaskList(models.Model):
    range = models.CharField('Zeitraum', max_length=16)
    label = models.CharField('Tätigkeit', max_length=255)
    tasks = models.ManyToManyField(Task, verbose_name=_('tasks'), blank=True, default=None)

    def __str__(self):
        return self.label
    
    class Meta:
        verbose_name = _("TaskList")
        verbose_name_plural = _("TaskLists")

    def get_absolute_url(self):
        return reverse("_detail", kwargs={"pk": self.pk})


class TaskReport(models.Model):
    site = models.CharField('Baustelle = Site', max_length=255, blank=True, null=True)
    task = models.CharField('Task', max_length=255, blank=True, null=True)
    worked = models.DecimalField('Hours Worked', max_digits=5, decimal_places=2, default=0.0)
    
    def __str__(self):
        return self.task
    
    class Meta:
        ordering = ['site', 'task']
        verbose_name = _("Task Report")
        verbose_name_plural = _("Task Reports")
    