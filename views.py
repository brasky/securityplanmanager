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
from .ssp_parser import parse_ssp
from .export import generate_docx_ssp, generate_cis_xlsx
from timeit import default_timer as timer
from collections import defaultdict



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

    return render(request, 'index.html')

def control_search(request):
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

        temp_result = []
        control = result[0].split(':')[0]
 

        temp_result.append(Control.objects.get(number=control).pk)
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

def nav_search(request):
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

        temp_result = []
        control = result[0].split(':')[0]
 

        temp_result.append(Control.objects.get(number=control).pk)
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


    return render_to_response('nav-search.html', {'controls': results})

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
            implementation = form.save()
            for certification in control.certifications.all():
                certification.implementations.add(implementation)
            messages.success(request, 'Implementation added successfully')
            return redirect('/implementations/' + str(control_pk))
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
            return redirect('/implementations/' + str(control_pk))
    return render(request, 'edit-implementation.html', {'formset': formset, 'pk': control_pk, 'control': control})


def certifications(request):
    # all_certifications = Certification.objects.all()
    def calculate_percentage(num, total):
        return (num/total) * 100

    data = {}
    if len(Certification.objects.all()) > 0:
        all_certifications = Certification.objects.annotate(num_controls = Count('controls'))
        high_total_controls = all_certifications[0].num_controls
        high_implemented_controls = all_certifications[0].implementations.filter(implementation_status='IM').values('control').distinct().count()
        high_partial_controls = all_certifications[0].implementations.filter(implementation_status='PI').values('control').distinct().count()
        high_na_controls = all_certifications[0].implementations.filter(implementation_status='NA').values('control').distinct().count()
        percent_partial = calculate_percentage(high_partial_controls, high_total_controls)
        percent_implemented = calculate_percentage(high_implemented_controls, high_total_controls)
        percent_na = calculate_percentage(high_na_controls, high_total_controls)
        print("percent implemented: ")
        print(high_implemented_controls)
        print(percent_implemented)
        data = {'certifications': all_certifications,
                'percent_implemented': percent_implemented,
                'percent_partial': percent_partial,
                'percent_na': percent_na,}
        teams = Team.objects.all()
        # for team in teams:
        #     data[team.name + '_percent_implemented'] = (len(team.implementations.filter(implementation_status='IM'))/high_total_controls)*100
        #     data[team.name + '_percent_partial'] = (len(team.implementations.filter(implementation_status='PI'))/high_total_controls)*100
        team_data = []
        for team in Team.objects.all():
            implemented = (team.implementations.filter(implementation_status='IM').count()/high_total_controls)*100
            partial = (team.implementations.filter(implementation_status='PI').count()/high_total_controls)*100
            team_data.append((team, implemented, partial))
        # teams = list(teams)
        # data['teams'] = teams
        data['team_data'] = team_data
    return render(request, 'certifications.html', data)

def add_certification(request):
    data = {}
    form = AddCertificationForm(request.POST or None)
    data['form'] = form
    if request.method == "POST":
        form = AddCertificationForm(request.POST)
        print(form.errors)
        if form.is_valid():
            data = form.cleaned_data
            controls = data['controls']
            implementations = Implementation.objects.filter(control__in=controls)
            cert = form.save()
            cert.implementations.set(implementations)
            messages.success(request, 'Certification added successfully')
            return redirect('/certifications/')
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
            return redirect('/certifications/')
    return render(request, 'edit-certifications.html', data)

def view_certification(request, certification_name):
    start = timer()
    cert = Certification.objects.get(name=certification_name)
    all_implementations = cert.implementations.all()
    
    end = timer()
    time = end - start
    #controls missing implementations from teams
    all_controls = cert.controls.all()
    answered_controls = [implementation.control for implementation in all_implementations]
    missing_controls = []
    for control in all_controls:
        if control not in answered_controls:
            missing_controls.append(control)
    
    teams = Team.objects.all()
    missing_controls_by_team = defaultdict(list)
    for team in teams:
        team_implementations = team.implementations.all()
        team_answered = [implementation.control for implementation in team_implementations]
        for control in all_controls:
            if control not in team_answered and control in answered_controls:
                missing_controls_by_team[team.name].append(control)
    missing_controls_by_team = dict(missing_controls_by_team)
    # print(missing_controls_by_team)
    # missing_controls_by_team = {'test': 'testing'}
    data = {'certification': cert,
            'implementations': all_implementations,
            'missing_controls': missing_controls,
            'team_missing': missing_controls_by_team}
    #control families with a percentage of how many are answered and the implementation status breakdown
    end = timer()
    time = end - start
    print("Certification load time: " + str(time))
    return render(request, 'view-certification.html', data)

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
            return redirect('/teams/')
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
            return redirect('/teams/')
    return render(request, 'edit-teams.html', data)

def view_team(request, team_name):
    data = {}
    team = Team.objects.get(name=team_name)
    all_implementations = Implementation.objects.filter(teams__in=[team])
    data['team'] = team
    data['all_implementations'] = all_implementations

    return render(request, 'view-team.html', data)


def certifications_test(request):
    imps = Implementation.objects.all()
    for imp in imps:
        imp.delete()
    # controls = Control.objects.all()
    # for control in controls:
    #     control.delete()
    # cert = Certification.objects.get(name="FedRAMP High")
    # for control in Control.objects.filter(high_baseline=True):
    #     cert.controls.add(control)

    return redirect('/import/ssp/')

    # cert.controls.set([controls])
    # implementations_to_add = Implementation.objects.filter(control__in=[controls])
    # cert.implementations.set(*[implementations_to_add])
    # return redirect('/controls/')

def import_home(request):
    return render(request, 'import-home.html')

def import_ssp(request):
    if request.method == "POST":
        print(request.FILES)
        form = SSPUploadForm(request.POST, request.FILES)
        print(form.errors)
        if form.is_valid():
            start = timer()
            data = form.cleaned_data
            certification = data['certification']
            parse_ssp(request.FILES['file'], certification)
            end = timer()
            time = end - start
            print('SSP Parser took: ' + str(time))
            messages.success(request, 'SSP Upload Complete')
            # return redirect('/certification-test/')
    form = SSPUploadForm()
    data = {}
    data['form'] = form
    return render(request, 'import-ssp.html', data)

def export_home(request):
    return render(request, 'export-home.html')

def export_download(request, doc_name, baseline, format):
    if doc_name == 'ssp' and format == 'docx' and baseline == 'high':
        return generate_docx_ssp(baseline)
    elif doc_name == "cis" and format == "xlsx" and baseline == "high":
        return generate_cis_xlsx(baseline)

    return redirect('/')

