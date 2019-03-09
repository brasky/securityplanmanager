from django.core.management.base import BaseCommand
from control_search.models import Control, Implementation
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
            open('control_search\management\commands\control-list.csv', 'r'))
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
            open('control_search\management\commands\control_guidance_list.csv', 'r'))
        control_list = dict(control_list_file)
        for num, text in control_list.items():
            control_object = Control.objects.filter(number=num).get()
            control_object.supplemental_guidance = text
            control_object.save()
        set_control_baselines()
        print('Controls created: ' + str(controls_created))
        print('Total controls: ' + str(len(Control.objects.all())))


# def get_control_baselines():
#     baselines_catalog = defaultdict(lambda: defaultdict(bool))
#     with open('control_search\management\commands\\baselines.csv', 'r') as baselines:
#         for row in csv.reader(baselines):
#             baselines_catalog[row[0]] = {
#                 'LOW': bool(row[1]), 'MODERATE': bool(row[2]), 'HIGH': bool(row[3])}
#         # print(baselines_catalog)
#         return baselines_catalog

def set_control_baselines():
    baselines_wb = load_workbook('control_search\management\commands\\baselines.xlsx')
    high_baseline = baselines_wb['High Baseline Controls']
    mod_baselines = baselines_wb['Moderate Baseline Controls']
    low_baselines = baselines_wb['Low Baseline Controls']
    baselines = [high_baseline, mod_baselines, low_baselines]

    for baseline in baselines:
        for row in baseline:
            if row[0].row > 2:
                control = row[3].value
                if control:
                    if " " in control:
                        matching_control = Control.objects.filter(number__contains=control)
                        for control_instance in matching_controls:
                            if "High" in baseline.title:
                                control_instance.high_baseline=True
                            elif "Moderate" in baseline.title:
                                control_instance.mod_baseline=True
                            elif "Low" in baseline.title:
                                control_instance.low_baseline=True
                            control_instance.save()

                    else:
                        matching_controls = Control.objects.filter(Q(number__contains=control + "(") & ~Q(number__contains=" "))
                        if not matching_controls:
                            matching_controls = Control.objects.filter(number=control)
                        for control_instance in matching_controls:
                            if "High" in baseline.title:
                                control_instance.high_baseline=True
                            elif "Moderate" in baseline.title:
                                control_instance.mod_baseline=True
                            elif "Low" in baseline.title:
                                control_instance.low_baseline=True
                            control_instance.save()


def get_control():
    control_numbers = ['ac-01(a)(1)', 'ac-01(a)(2)',
                       'ac-01(a)(3)', 'ac-01(a)(4)', 'ac-01(b)(1)']
    control_text = ['testing a 1 ', 'testing a 2',
                    'testing a 3', 'testing a 4', 'testing b 1']
    return control_numbers, control_text
