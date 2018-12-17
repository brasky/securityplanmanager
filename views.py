from django.shortcuts import render, render_to_response
from django.http import HttpResponse
from .models import Control
from fuzzywuzzy import fuzz
from fuzzywuzzy import process
from functools import lru_cache


#@lru_cache(maxsize=128)
def get_all_controls():
	all_controls = list(Control.objects.all())
	control_name_plus_text = []
	for control in all_controls:
		control_name_plus_text.append(control.number + ": " + control.control_text)
	return control_name_plus_text

def index(request):
	args = {}

	return render(request, 'search_box.html', args)	

def search(request):
	if request.method == "POST":
		search_text = request.POST['search_text']
	else:
		search_text = ''
#	controls = Control.objects.filter(control_text__contains=search_text)
#	print(controls)	
	all_controls = get_all_controls()
	print(search_text)	

	results = process.extract(search_text, all_controls, limit=10, scorer=fuzz.partial_ratio)
	

#	controls = process.extract(search_text, all_controls,limit=5 )
	

			
#	print(controls)
	return render_to_response('ajax_search.html', {'controls' : results})




