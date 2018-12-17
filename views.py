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
	control_text = {}
	control_guidance = {}
	for control in all_controls:
		control_text[control.number] = control.control_text
		control_name_plus_text.append(control.number + ": " + control.control_text)
		control_guidance[control.number] = control.supplemental_guidance
	return control_name_plus_text, control_text, control_guidance

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
	search_results = process.extract(search_text, all_controls, limit=10, scorer=fuzz.partial_ratio)
#	print(search_results)	
	results = []
	counter = 0
	for result in search_results:
#		print(result[0].split(':')[0])
		temp_result = []
		control=result[0].split(':')[0]
#		print(control_dict[control])
		temp_result.append(counter)
		counter += 1
		temp_result.append(control)
		temp_result.append(control_dict[control])
		temp_result.append(control_guidance[control])
		results.append(temp_result)

	return render_to_response('ajax_search.html', {'controls': results})




