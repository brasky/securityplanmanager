from django.core.management.base import BaseCommand
from control_search.models import Control, Implementation
import csv
import os


class Command(BaseCommand):
	help = 'Fill the database with controls'
	def handle(self, *Args, **options):
		Control.objects.all().delete()
		control_list_file = csv.reader(open('control_search\management\commands\control-list.csv', 'r'))
		control_list = dict(control_list_file)
#		control_numbers, control_text = get_control()
		controls_created = 0
		for num, text in control_list.items():
			if not Control.objects.filter(number=num).exists():
				Control(number=num, control_text=text).save()
				controls_created+=1
		control_list_file = csv.reader(open('control_search\management\commands\control_guidance_list.csv', 'r'))
		control_list = dict(control_list_file)
		for num, text in control_list.items():
			control_object = Control.objects.filter(number=num).get()
			control_object.supplemental_guidance = text
			control_object.save()
		print('Controls created: ' + str(controls_created))
		print('Total controls: ' + str(len(Control.objects.all())))
	


def get_control():
	control_numbers = ['ac-01(a)(1)','ac-01(a)(2)','ac-01(a)(3)','ac-01(a)(4)','ac-01(b)(1)']	
	control_text = ['testing a 1 ','testing a 2','testing a 3','testing a 4','testing b 1']
	return control_numbers, control_text
