from django.core.management.base import BaseCommand
from securityplanmanager.models import Control, Implementation
import csv
import os
from collections import defaultdict
from openpyxl import load_workbook
from django.db.models import Q

class Command(BaseCommand):
    help = 'Fill the database with controls'

    def handle(self, *Args, **options):
        Control.objects.all().delete()
        control_list_file = csv.reader(
            open('securityplanmanager\management\commands\control-list.csv', 'r'))
        control_list = dict(control_list_file)
#        control_numbers, control_text = get_control()
        controls_created = 0
        # control_baselines = get_control_baselines()
        for num, text in control_list.items():
            if not Control.objects.filter(number=num).exists():
                control = Control(number=num, control_text=text)
                # print(num)
                # print(control_baselines[num])
                # control.low_baseline = control_baselines[num]['LOW']
                # control.mod_baseline=control_baselines[num]['MODERATE']
                # control.high_baseline=control_baselines[num]['HIGH']
                control.save()

                controls_created += 1
        control_list_file = csv.reader(
            open('securityplanmanager\management\commands\control_guidance_list.csv', 'r'))
        control_list = dict(control_list_file)
        for num, text in control_list.items():
            control_object = Control.objects.filter(number=num).get()
            control_object.supplemental_guidance = text
            control_object.save()
        set_control_baselines()
        print('Controls created: ' + str(controls_created))
        print('Total controls: ' + str(len(Control.objects.all())))

def set_control_baselines():
    baselines_wb = load_workbook('securityplanmanager\management\commands\\baselines.xlsx')
    baselines_ws = baselines_wb.active
    # baselines = [high_baseline, mod_baselines, low_baselines]
    for row in baselines_ws:
        control = Control.objects.get(number=row[0].value)
        low, mod, high = row[1].value, row[2].value, row[3].value
        if low:
            control.low_baseline=True
        if mod:
            control.mod_baseline=True
        if high:
            control.high_baseline=True
        control.save()
