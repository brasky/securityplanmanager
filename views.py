from django.shortcuts import render, render_to_response
from django.http import HttpResponse
from .models import Control, Implementation, Certification, Team
from fuzzywuzzy import fuzz
from fuzzywuzzy import process
from functools import lru_cache
import re
from .forms import *
from django.contrib import messages
from django.shortcuts import redirect
from django.forms import modelformset_factory
from django.db.models import Count

@lru_cache(maxsize=128)
def get_all_controls():
    all_controls = list(Control.objects.all())
    control_name_plus_text = []
    control_text = {}
    control_guidance = {}
    for control in all_controls:
        control_text[control.number] = control.control_text
        control_name_plus_text.append(
            control.number + ": " + control.control_text)
        control_guidance[control.number] = control.supplemental_guidance
    return control_name_plus_text, control_text, control_guidance


def highlight_matches(query, text):
    def span_matches(match):
        html = '<span class="query">{0}</span>'
        return html.format(match.group(0))
    return re.sub(query, span_matches, text, flags=re.I)


def index(request):
    args = {}
    return render(request, 'search_box.html', args)


def search(request):
    if request.method == "POST":
        search_text = request.POST['search_text']
    else:
        search_text = ''
    all_controls, control_dict, control_guidance = get_all_controls()
    print(search_text)
    search_results = process.extract(
        search_text, all_controls, limit=10, scorer=fuzz.partial_ratio)
#	print(search_results)
    results = []
    counter = 0
    for result in search_results:
        #		print(result[0].split(':')[0])
        temp_result = []
        control = result[0].split(':')[0]
#		print(control_dict[control])
        temp_result.append(counter)
        counter += 1
        temp_result.append(control)
        if len(search_text) > 2:
            control_text = highlight_matches(
                search_text, control_dict[control])
        else:
            control_text = control_dict[control]
        temp_result.append(control_text)
        temp_result.append(control_guidance[control])
        results.append(temp_result)

    return render_to_response('ajax_search.html', {'controls': results})


def implementations(request, control_pk):
    control = Control.objects.get(pk=control_pk)
    all_implementations = Implementation.objects.all().filter(control=control)
    
    return render(request, 'implementations.html',
                  {'control': control, 'implementations': all_implementations, 'pk': control_pk})


def add_implementation(request, control_pk):
    control = Control.objects.get(pk=control_pk)
    data = {'control': control}
    form = AddImplementationForm(initial=data)
    if request.method == "POST":
        form = AddImplementationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Implementation added successfully')
            return redirect('/controls/implementations/' + str(control_pk))

    return render(request, 'add-implementation.html', {'form': form, 'pk': control_pk})

def edit_implementations(request, control_pk):
    control = Control.objects.get(pk=control_pk)
    # implementations = Implementation.objects.filter(control=control)
    # data = {'control': control, 'parameter': 'test'}

    ImplementationFormSet = modelformset_factory(Implementation, fields = ['control', 'parameter', 'customer_responsibility',
                  'solution', 'implementation_status', 'control_origination', 'teams'], can_delete=True, extra=0)
    formset = ImplementationFormSet(queryset=Implementation.objects.filter(control=control), initial=[{'control': control}])
    if request.method == "POST":
        
        form = ImplementationFormSet(request.POST)
        print(form.errors)
        if form.is_valid():
            form.save()
            messages.success(request, 'Implementation(s) edited successfully')
            return redirect('/controls/implementations/' + str(control_pk))
    return render(request, 'edit-implementation.html', {'formset': formset, 'pk': control_pk, 'control': control})

def certifications(request):
    # all_certifications = Certification.objects.all()
    all_certifications = Certification.objects.annotate(num_controls = Count('controls'))
    high_total_controls = all_certifications[0].num_controls
    high_implemented_controls = len(all_certifications[0].implementations.filter(implementation_status='IM'))
    high_partial_contorls = len(all_certifications[0].implementations.filter(implementation_status='PI'))
    percent_partial = (high_partial_contorls/high_total_controls)*100
    percent_implemented = (high_implemented_controls/high_total_controls)*100

    data = {'certifications': all_certifications,
            'percent_implemented': percent_implemented,
            'percent_partial': percent_partial,}
    for team in Team.objects.all():
        data[team.name + '_percent_implemented'] = (len(team.implementations.filter(implementation_status='IM'))/high_total_controls)*100
        data[team.name + '_percent_partial'] = (len(team.implementations.filter(implementation_status='PI'))/high_total_controls)*100


    return render(request, 'certifications.html', data)

def link_implementations_to_certifications(cert_name):
    cert = Certification.objects.get(name=cert_name)
    for control in Control.objects.all():
        cert.controls.add(control)
        implementations_to_add = Implementation.objects.filter(control=control)
        cert.implementations.add(*list(implementations_to_add))

def add_certification(request):
    data = {}
    form = AddCertificationForm()
    data['form'] = form
    if request.method == "POST":
        form = AddCertificationForm(request.POST)
        print(form.errors)
        if form.is_valid():
            form.save()
            messages.success(request, 'Certification added successfully')
            return redirect('/controls/certifications/')
    return render(request, 'add-certification.html', data)


def edit_certifications(request):
    data = {}
    certFormSet = modelformset_factory(Certification, fields=['name', 'controls'], can_delete=True, extra=0)
    data['formset'] = certFormSet
    if request.method == "POST":
        form = certFormSet(request.POST)
        print(form.errors)
        if form.is_valid():
            form.save()
            messages.success(request, 'Certification(s) edited successfully')
            return redirect('/controls/certifications/')
    return render(request, 'edit-certifications.html', data)

def view_certification(request, certification_name):
    cert = Certification.objects.get(name=certification_name)
    implementations = cert.implementations.all()
    data = {'certification': cert,
            'implementations': implementations}

    return render(request, 'view-certification.html', data)
    pass

def teams(request):
    data = {}
    data['teams'] = Team.objects.all()
    
    return render(request, 'teams.html', data)
    
def add_team(request):
    data = {}
    data['form'] = AddTeamForm()
    if request.method == "POST":
        form = AddTeamForm(request.POST)
        print(form.errors)
        if form.is_valid():
            form.save()
            messages.success(request, 'Team added successfully')
            return redirect('/controls/teams/')
    return render(request, 'add-team.html', data)

def edit_teams(request):
    data = {}
    teamFormSet = modelformset_factory(Team, fields=['name'], can_delete=True, extra=1)
    data['formset'] = teamFormSet
    if request.method == "POST":
        form = teamFormSet(request.POST)
        print(form.errors)
        if form.is_valid():
            form.save()
            messages.success(request, 'Team(s) edited succesfully')
            return redirect('/controls/teams/')
    return render(request, 'edit-teams.html', data)



def certifications_test(request):
    
    # cert = Certification.objects.get(name="FedRAMP High")
    # for control in Control.objects.all():
    #     cert.controls.add(control)
    #     implementations_to_add = Implementation.objects.filter(control=control)
    #     cert.implementations.add(*list(implementations_to_add))
    return redirect('/controls/')

    # cert.controls.set([controls])
    # implementations_to_add = Implementation.objects.filter(control__in=[controls])
    # cert.implementations.set(*[implementations_to_add])
    # return redirect('/controls/')