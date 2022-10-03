from django.db import models
from django.urls import reverse
from django.contrib.auth.models import User


# Create your models here.
class BaseModel(models.Model):
    id = models.AutoField(primary_key=True)
    date_added = models.DateTimeField(null=True, blank=True)
    last_updated = models.DateTimeField(null=True, blank=True)

    class Meta:
        abstract = True


class Category(BaseModel):
    name = models.CharField(max_length=100, default=None, null=True, blank=True, help_text="Major category like plumbing, construction, etc...")
    slug = models.CharField(max_length=150, default="")

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('church_skills:category_detail', args=[str(self.slug)])

    @staticmethod
    def create_url(slug):
        return reverse('church_skills:category_detail', args=[str(slug)])


class Provider(BaseModel, User):
    company_name = models.CharField(max_length=150, default=None, null=True, blank=True, help_text="Company name that you associate with")
    phone_number = models.CharField(max_length=30, default=None, null=True, blank=True, help_text="10 digit phone number you would like displayed")
    email_address = models.EmailField(default=None, null=True, blank=True, help_text="Valid e-mail address should you choose to add one")
    picture = models.ImageField(default=None, null=True, blank=True)
    about_me = models.TextField(default="", null=True, blank=True, help_text="Extra info you wish to display about yourself")
    website = models.URLField(default=None, null=True, blank=True, help_text="A link to your website, if you have one, for more info")
    categories = models.ManyToManyField(Category, blank=True)
    slug = models.CharField(max_length=150, default="")

    def __str__(self):
        return self.company_name

    def get_absolute_url(self):
        return reverse('church_skills:category_detail', args=[str(self.slug)])

    @staticmethod
    def create_url(slug):
        return reverse('church_skills:category_detail', args=[str(slug)])


class Skill(BaseModel):
    name = models.CharField(max_length=100)
    description = models.TextField(default="", null=True, blank=True, help_text="Please enter detailed description of this skill or service")
    cost_range = models.CharField(max_length=100, default=None, null=True, blank=True, help_text="Enter info like $20-$30/hour or Cost varies")
    provider = models.ForeignKey(Provider, on_delete=models.CASCADE, null=True, blank=True)
    slug = models.CharField(max_length=150, default="")

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('church_skills:category_detail', args=[str(self.slug)])

    @staticmethod
    def create_url(slug):
        return reverse('church_skills:category_detail', args=[str(slug)])
