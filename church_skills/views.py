# Django imports
from django.views.generic import ListView, DetailView, FormView, View
from django.core.exceptions import ValidationError
from django.shortcuts import HttpResponseRedirect, reverse, redirect, render
from django.db.models import Count, F
from django import db
from django.core.serializers import serialize
from django.http import JsonResponse
from django.contrib.auth import login, views as auth_views, get_user_model as users
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.forms import AuthenticationForm, PasswordChangeForm

# Local imports
from .models import *
from .forms import *
from urllib.parse import urlencode


# -------------------------------------------------Base Views ----------------------------------------------------------
class SearchMixin(View):
    search = SearchForm

    def get_context_data(self, **kwargs):
        context = {'search_form': self.search}
        return context


class BaseUpdateView(SearchMixin, FormView):
    def get_context_data(self, **kwargs):
        context = super(BaseUpdateView, self).get_context_data()
        return context


# ------------------------------------- Main and Search Views ----------------------------------------------------------
class MainView(SearchMixin, ListView):
    model = Category
    template_name = 'skills/main_page.html'
    context_object_name = 'categories'
    queryset = None

    def get_context_data(self, *args, **kwargs):
        context = super(MainView, self).get_context_data()
        categories = Category.objects.all().annotate(recipe_count=Count('recipe')).order_by('recipe_count')[:5]
        recipes = Recipe.objects.all().order_by('-id')[:10]

        context['categories'] = categories
        context['recipes'] = recipes
        return context


class SearchView(SearchMixin, ListView):
    model = Recipe
    template_name = 'skills/search_results.html'
    context_object_name = 'search_results'
    queryset = None

    def get_context_data(self, *args, **kwargs):
        context = super(SearchView, self).get_context_data()
        name = self.request.GET.get('name')
        recipes = Recipe.objects.filter(name__icontains=name)
        for recipe in recipes:
            recipe.total_time = recipe.cook_time + recipe.prep_time
            if "http" in recipe.source:
                recipe.link = recipe.source
        form = self.search

        context['name'] = name
        context['recipes'] = recipes
        context['form'] = form
        return context

    def get(self, request, *args, **kwargs):
        if self.request.headers.get('x_requested_with') == 'XMLHttpRequest':
            name = self.request.GET.get('name')
            sorting_method = self.request.GET.get('sorting_method')
            ascending = self.request.GET.get('ascending')
            data = []
            if ascending == "true":
                if sorting_method == "source":
                    query = None
                elif sorting_method == "total_time":
                    query = Recipe.objects.filter(name__icontains=name)\
                        .annotate(total_time=F('prep_time') + F('cook_time')).order_by('total_time')
                else:
                    query = Recipe.objects.filter(name__icontains=name)\
                        .annotate(total_time=F('prep_time') + F('cook_time')).order_by(sorting_method)
            elif ascending != "true":
                if sorting_method == "source":
                    query = None
                elif sorting_method == "total_time":
                    query = Recipe.objects.filter(name__icontains=name)\
                        .annotate(total_time=F('prep_time') + F('cook_time')).order_by('total_time').reverse()
                else:
                    query = Recipe.objects.filter(name__icontains=name)\
                        .annotate(total_time=F('prep_time') + F('cook_time')).order_by(sorting_method).reverse()
            else:
                query = None
                data = serialize('json', None)

            if query is not None:
                for obj in query:
                    url_link = '<a href="' + obj.get_absolute_url() + '">' + obj.name + '</a>'
                    if "http" in obj.source:
                        source = '<a href="' + obj.source + '">' + obj.source + '</a>'
                    else:
                        source = obj.source
                    json_data = {"name": url_link, "servings": obj.servings, "time": format_time(obj.total_time),
                                 "source": source}
                    data.append(json_data)

            return JsonResponse(data=data, safe=False)
        else:
            return render(self.request, self.template_name, context=self.get_context_data())

    @staticmethod
    def post(request):
        if request.method == 'POST':
            form = SearchForm(request.POST)
            if form.is_valid():
                name = form.cleaned_data['search_name']
                base_url = reverse('RecipeBook:search_results')
                query_string = urlencode({'name': name})
                url = '{}?{}'.format(base_url, query_string)
                return HttpResponseRedirect(url)
            else:
                raise ValidationError


# ------------------------------------- Category views -----------------------------------------------------------------
class CategoryListView(SearchMixin, ListView):
    model = Category
    template_name = 'skills/category_list.html'
    context_object_name = 'category_list'
    queryset = None

    def get_context_data(self, *args, **kwargs):
        context = super(CategoryListView, self).get_context_data()
        categories = Category.objects.all()
        for category in categories:
            category.recipes = Recipe.objects.filter(categories=category)
        # context = {'categories': categories}
        context['categories'] = categories
        return context

    def get(self, request, *args, **kwargs):
        if self.request.headers.get('x_requested_with') == 'XMLHttpRequest':
            sorting_method = self.request.GET.get('sorting_method')
            ascending = self.request.GET.get('ascending')
            query_base = Category.objects.all().annotate(recipe_count=Count('recipe'))
            data = []
            if ascending == "true":
                if sorting_method == "recipe_count":
                    query = query_base.order_by('recipe_count')
                else:
                    query = query_base.order_by(sorting_method)
            elif ascending != "true":
                if sorting_method == "recipe_count":
                    query = query_base.order_by('recipe_count').reverse()
                else:
                    query = query_base.order_by(sorting_method).reverse()
            else:
                query = None
                data = serialize('json', None)

            if query is not None:
                for obj in query:
                    if obj.recipe_count > 0:
                        url_link = '<a href="' + obj.get_absolute_url() + '">' + obj.name + '</a>'
                        json_data = {"name": url_link, "recipe_count": obj.recipe_count}
                        data.append(json_data)
                    else:
                        pass

            return JsonResponse(data=data, safe=False)
        else:
            return render(self.request, self.template_name, context=self.get_context_data())


class CategoryDetailView(SearchMixin, DetailView):
    model = Category
    template_name = 'skills/category_detail.html'
    context_object_name = 'category_recipe_list'
    queryset = None
    slug_field = 'slug'
    slug_url_kwarg = 'slug'

    def get_context_data(self, *args, **kwargs):
        context = super(CategoryDetailView, self).get_context_data()
        category = self.get_object()
        category.recipes = Recipe.objects.filter(categories=category)
        for recipe in category.recipes:
            recipe.total_time = format_time(recipe.prep_time + recipe.cook_time)
            if "http" in recipe.source:
                recipe.link = recipe.source

        context['category'] = category
        return context

    def get(self, request, *args, **kwargs):
        if self.request.headers.get('x_requested_with') == 'XMLHttpRequest':
            sorting_method = self.request.GET.get('sorting_method')
            ascending = self.request.GET.get('ascending')
            query_base = Recipe.objects.filter(categories=self.get_object())\
                .annotate(total_time=F('prep_time') + F('cook_time'))
            data = []
            if ascending == "true":
                if sorting_method == "source":
                    query = None
                elif sorting_method == "total_time":
                    query = query_base.order_by('total_time')
                else:
                    query = query_base.order_by(sorting_method)
            elif ascending != "true":
                if sorting_method == "source":
                    query = None
                elif sorting_method == "total_time":
                    query = query_base.order_by('total_time').reverse()
                else:
                    query = query_base.order_by(sorting_method).reverse()
            else:
                query = None
                data = serialize('json', None)

            if query is not None:
                for obj in query:
                    url_link = '<a href="' + obj.get_absolute_url() + '">' + obj.name + '</a>'
                    if "http" in obj.source:
                        source = '<a href="' + obj.source + '">' + obj.source + '</a>'
                    else:
                        source = obj.source
                    json_data = {"name": url_link, "servings": obj.servings, "time": format_time(obj.total_time),
                                 "source": source}
                    data.append(json_data)

            return JsonResponse(data=data, safe=False)
        else:
            return render(self.request, self.template_name, context=self.get_context_data())


# --------------------------------------------- Authentication views ---------------------------------------------------
class CreateUserView(SearchMixin, FormView):
    template_name = 'registration/account_creation.html'
    account_form = AccountCreationForm

    def get_context_data(self, *args, **kwargs):
        self.search.autofocus = False
        context = super(CreateUserView, self).get_context_data()
        context['account_form'] = self.account_form
        return context

    def post(self, request, *args, **kwargs):
        if request.method == 'POST':
            form = AccountCreationForm(request.POST)
            if form.is_valid():
                print(True)
                username = form.clean_username()
                password = form.clean_password2()
                email = form.clean_email()
                first_name = form.clean_first_name()
                last_name = form.clean_last_name()
                user = users().objects.create_user(username=username,
                                                   password=password,
                                                   email=email)
                user.first_name = first_name
                user.last_name = last_name

                print(user)

                while True:
                    try:
                        user.save()
                        break
                    except db.utils.OperationalError:
                        print("DB is locked")

                print(users().objects.get(username=username))

                login(request, user)

                return redirect('RecipeBook:main')
            else:
                print("form was not valid")
                print(form.error_messages)
                return render('RecipeBook:create_user', template_name='registration/account_creation.html',
                              context={'account_form': form})

        else:
            return render(self.request, self.template_name, self.get_context_data())


class LoginView(SearchMixin, auth_views.LoginView):
    template_name = 'registration/login.html'
    redirect_field_name = "redirect"
    redirect_authenticated_user = True
    form = AuthenticationForm

    def get_context_data(self, **kwargs):
        context = super(LoginView, self).get_context_data()
        self.search.autofocus = False
        context['login_form'] = self.form
        if self.request.GET.get('next'):
            context['redirect'] = self.request.GET.get('next')
        return context


class LogoutView(SearchMixin, auth_views.LogoutView):
    pass


class PasswordChangeView(SearchMixin, auth_views.PasswordChangeView):
    template_name = 'registration/password_change.html'
    form = PasswordChangeForm

    def get_context_data(self, **kwargs):
        context = super(PasswordChangeView, self).get_context_data()
        self.search.autofocus = False
        context['password_change_form'] = self.form(user=self.request.user)
        return context


class PasswordChangeDoneView(SearchMixin, auth_views.PasswordChangeDoneView):
    template_name = 'registration/password_change_done.html'


class ProfileListView(SearchMixin, ListView):
    model = users()
    queryset = None

    # Only here to serve as a path for the profiles


class ProfileDetailView(SearchMixin, DetailView):
    model = users()
    template_name = 'skills/profile_page.html'
    queryset = None
    slug_field = 'username'
    slug_url_kwarg = 'username'

    def get_context_data(self, **kwargs):
        context = super(ProfileDetailView, self). get_context_data()
        user = self.get_object()
        recipes_submitted = Recipe.objects.filter(submitter=user)

        context['username'] = user
        context['recipes_submitted'] = recipes_submitted

        return context