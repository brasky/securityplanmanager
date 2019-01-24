from docx import *
from .models import Control, Implementation, Team
from django.db.models import Q
import re
from django.http import HttpResponse
from time import sleep
from django.contrib.staticfiles.storage import staticfiles_storage
import os 
from django.conf import settings
from .helper import get_control_parts

def generate_docx_ssp(baseline):
    template = __package__ + '\static\\fedramp_templates\\' + baseline + '.docx'
    document = Document(os.path.join(settings.BASE_DIR, template))
    previous_matched = None
    control_tables = {}
    control_to_implementation = {}
    for table in document.tables:
        try:    
            table_title = table.cell(0, 0).text
            table_title_column_two = table.cell(0, 1).text
            # if len(table_title) == 4 or len(table_title) == 5 and "-" in table_title:
            
            # print(table_title)
            if "Control Summary Information" in table_title_column_two:
                control_parent = table_title
                if "(" not in control_parent:
                    control = control_parent + "("
                    matching_controls = Control.objects.filter(Q(number__contains=control) & ~Q(number__contains=' '))
                    if not matching_controls:
                        control = control_parent
                        matching_controls = Control.objects.filter(Q(number__contains=control) & ~Q(number__contains=' '))
                else:
                    control = control_parent
                    matching_controls = Control.objects.filter(Q(number__contains=control))
                # if not matching_controls:
                #     print(control_parent)
                #     print(matching_controls)
                previous_matched = matching_controls
                for matched_control in matching_controls:
                    matching_implementation = Implementation.objects.get(control=matched_control)
                    control_to_implementation[matched_control.number] = matching_implementation
                    # print(control_to_implementation)
                    

                    rows = len(table.rows)
                    for row in range(1,rows):
                        cell_text = table.cell(row, 0).text
                        if "Responsible Role" in cell_text:
                            pass
                        elif "Parameter" in cell_text:
                            pass
                        elif "Implementation" in cell_text:
                            pass
                        elif "Control Origination" in cell_text:
                            pass

            elif "solution" in table_title:
                # print(table_title)
                # print(previous_matched)
                matching_controls = previous_matched
                for matched_control in matching_controls:
                    
                    control_parts = get_control_parts(matched_control.number)
                    # print(matched_control.number)
                    # print(control_to_implementation)
                    implementation = control_to_implementation[matched_control.number]
                    

                   
                    add_implementation_to_table(table, implementation, control_parts)

                    # print(matched_control.number)
                    # print(control_parts)

                # print(table_title)
                
        except:
            print("exception")
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document')
    response['Content-Disposition'] = 'attachment; filename=high-ssp.docx'
    document.save(response)

    return response



def add_implementation_to_table(table, implementation_object, control_parts):
    implementation_details = implementation_object.solution
    customer_responsibility = implementation_object.customer_responsibility
    if  not control_parts['part_letter'] and not control_parts['part_num']: #no letter, no part, no enhancement
        if customer_responsibility:
            table.cell(0,1).text = "Customer Responsibility:" + "\n" + customer_responsibility + "\n" + implementation_details
        else:
            table.cell(0,1).text = implementation_details

    elif not control_parts['part_num']:#letter, no part, no enhancement
        
        if customer_responsibility:
            table.cell(control_parts['part_letter'],1).text = (table.cell(control_parts['part_letter'], 1).text
                                                               + "Customer Responsibility:" + "\n"
                                                               + customer_responsibility + "\n"
                                                               + implementation_details + "\n")
        else:
            table.cell(control_parts['part_letter'],1).text = (table.cell(control_parts['part_letter'], 1).text
                                                               + implementation_details + "\n")

    else:#letter, part, no enhancement
        if customer_responsibility:
            table.cell(control_parts['part_letter'],1).text = (table.cell(control_parts['part_letter'], 1).text
                                                               + "Part " + control_parts['part_num'] + "\n"
                                                               + "Customer Responsibility:" + "\n"
                                                               + customer_responsibility + "\n"
                                                               + implementation_details + "\n")
        else:
            table.cell(control_parts['part_letter'],1).text = (table.cell(control_parts['part_letter'], 1).text
                                                               + "Part " + control_parts['part_num'] + "\n"
                                                               + implementation_details + "\n")
    