from django.core.management.base import BaseCommand
from securityplanmanager.models import Control, Implementation
import csv
import os

class Command(BaseCommand):
	help = 'Populate control guidance fields'
	def handle(self, *Args, **options):
		control_list_file = csv.reader(open('securityplanmanager\management\commands\control_guidance_list.csv', 'r'))
		control_list = dict(control_list_file)
		for num, text in control_list.items():
			control_object = Control.objects.filter(number=num).get()
			control_object.supplemental_guidance = text
			control_object.save()
