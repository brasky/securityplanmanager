from collections import defaultdict
from docx import *
from .models import Control, Implementation, Team, ControlOrigination, Certification
from django.db.models import Q
from .helper import get_control_parts
from time import sleep
import sys

def get_customer_responsibility(implementation_details):
    teams = Team.objects.all()
    split_details = implementation_details.split('\n')
    # print(split_details)
    cust_resp_flag = False
    customer_responsibility = ''
    for part in split_details:
        if "Customer Responsibility:" in part:
            cust_resp_flag = True
            customer_responsibility = part
            continue
        if cust_resp_flag:
            for team in teams:
                if team.name + ":" in part or "Part 1" in part or "Part 2" in part or 'Part 1,2,3' in part:
                    return customer_responsibility
            customer_responsibility = customer_responsibility +'\n' + part

    return False



def get_team_list():
    pass

def get_part_text(implementation_details, control_parts):
    split_details = implementation_details.split('Part')
    part_text = ''
    part_num_colon = control_parts['part_num'] + ':'
    part_num_comma = control_parts['part_num'] + ','
    for part in split_details:
        if part_num_colon in part:
            part_text = part.lstrip('1234567890:, \n')
            return part_text
        elif part_num_comma in part:
            part_text = part.lstrip('1234567890:, \n') 
            return part_text


def create_implementation(new_implementation):

    if new_implementation['customer_resp']:
        new_implementation_object = Implementation(
            control=new_implementation['control_object'],
            parameter=new_implementation['parameter'],
            responsible_role=new_implementation['responsible_role'],
            customer_responsibility=new_implementation['customer_resp'],
            solution=new_implementation['solution'],
            implementation_status=new_implementation['implementation_status'],
            
            )
    else:
        new_implementation_object = Implementation(
            control=new_implementation['control_object'],
            parameter=new_implementation['parameter'],
            responsible_role=new_implementation['responsible_role'],
            customer_responsibility='',
            solution=new_implementation['solution'],
            implementation_status=new_implementation['implementation_status'],
            
            )
    
    # new_implementations.append(new_implementation_object)
    # for implementation in new_implementations:
    #     implementation.save()
    #     implementation.teams.set(new_implementation['teams'])
    try:
        new_implementation_object.save()
        new_implementation_object.control_origination.set(new_implementation['control_origination'])
        new_implementation_object.teams.set(new_implementation['teams'])
        cert = Certification.objects.get(name__contains="High")
        cert.implementations.add(new_implementation_object)
        # cert.save()
    except:
        e = sys.exc_info()[0]
        print( "Error: %s" % e )
        

def parse_solution_table(table, control_object, control_parts):
    control_number = control_object.number
    

    if  not control_parts['part_letter'] and not control_parts['part_num']: #no letter, no part, no enhancement
        implementation_details = table.cell(0,1).text
        # print(implementation_details)
        # print(control_number)
        customer_responsibility = get_customer_responsibility(implementation_details)
        if customer_responsibility:
            implementation_details = implementation_details.replace(customer_responsibility, '').strip()


        # teams = get_team_list(implementation_details)


    elif not control_parts['part_num']:#letter, no part, no enhancement
        try:
            implementation_details = table.cell(control_parts['part_letter'],1).text
        except:
            print("parse solution table error:")
            # print(table.cell(4,0).text)
            print(control_number)
            print(control_parts)
            print(table.cell(0,0).text)

        # print(control_number)

        customer_responsibility = get_customer_responsibility(implementation_details)
        if customer_responsibility:
            implementation_details = implementation_details.replace(customer_responsibility, '').strip()
        # print(customer_responsibility)
    else:#letter, part, no enhancement
        implementation_details = table.cell(control_parts['part_letter'],1).text
        # print(control_number)
        # print(implementation_details)
        customer_responsibility = get_customer_responsibility(implementation_details)
        if customer_responsibility:
            implementation_details = implementation_details.replace(customer_responsibility, '').strip()
        # print(customer_responsibility)
    # else:
    #     raise ValueError('A case was not handled by the implementation table section of parse ssp')
    
    return implementation_details, customer_responsibility

def get_implementation_status_from_cell(implementation_cell):
    implementation_status = ''
    for paragraph in implementation_cell.paragraphs:
        p = paragraph._element
        checkBoxes = p.xpath('.//w:checkBox')
        
        if 'w14:checked w14:val="1"' in p.xml:
        #     if len(checkBoxes[0].getchildren()) >= 2:
        #         if checkBoxes[0].find('.//w:checked', namespace) is not None:
        #             if not checkBoxes[0].find('.//w:checked', namespace).values():
            xpath_elements = p.xpath('.//w:t')
            implementation_status = xpath_elements[len(xpath_elements)-1].text.strip()
            # print(control_parent)
            # print(implementation_status)
            if 'Partially' in implementation_status:
                implementation_status = 'PI'
            elif 'Implemented' in implementation_status:
                implementation_status = 'IM'
            elif 'Planned' in implementation_status:
                implementation_status = 'PL'
            elif 'Alternative' in implementation_status:
                implementation_status = 'AI'
            elif 'Not' in implementation_status:
                implementation_status = 'NA'
    return implementation_status


def get_control_origination_from_cell(control_origination_cell):
    control_originations = []
    for paragraph in control_origination_cell.paragraphs:
        # print(paragraph.text)
        p = paragraph._element
        # checkBoxes = p.xpath('.//w:checkBox')
        # if len(checkBoxes) > 0:
        if 'w14:checked w14:val="1"' in p.xml:
            xpath_elements = p.xpath('.//w:t')
            control_origination = xpath_elements[len(xpath_elements)-1].text.strip()
            # print(control_parent + ": " + control_origination)
            if "Service Provider Corporate" in control_origination:
                control_originations.append(ControlOrigination.objects.get(source='SPC'))
            elif "Service Provider System Specific" in control_origination:
                control_originations.append(ControlOrigination.objects.get(source='SPS'))
            elif "Hybrid" in control_origination:
                control_originations.append(ControlOrigination.objects.get(source='SPH'))
            elif "Configured" in control_origination:
                control_originations.append(ControlOrigination.objects.get(source='CBC'))
            elif "Provided" in control_origination:
                control_originations.append(ControlOrigination.objects.get(source='PBC'))
            elif "Shared" in control_origination:
                control_originations.append(ControlOrigination.objects.get(source='SHA'))
            elif "Inherited" in control_origination:
                control_originations.append(ControlOrigination.objects.get(source='INH'))
            elif "Not" in control_origination:
                control_originations.append(ControlOrigination.objects.get(source='NOT'))
    return control_originations


namespace = {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
implementations = []

def parse_ssp(file):
    document = Document(file)
    # print('we made it here')
    for table in document.tables:
        try:
            table_title = table.cell(0,0).text
        except:
            continue
        # print(table_title)
        if "Req" in  table_title or "req" in table_title:
            continue
        if len(table_title) < 20 and '-' in table_title:
            control_parent = table_title
            parameters = defaultdict(str)
            controls = {}
            parameter = ''
            rows = len(table.rows)
            for cell in range(1,rows):

                if "Implementation" in table.cell(cell,0).text:
                    implementation_status = get_implementation_status_from_cell(table.cell(cell,0))
                    # if implementation_status == '':
                    #     print(control_parent, implementation_status)
                                    
                elif "Control Origination" in table.cell(cell,0).text:
                    control_originations = get_control_origination_from_cell(table.cell(cell, 0))
                    # print(control_parent, control_originations)
                    # if control_origination == '':
                    #     print(control_parent, control_origination)
                                       

                elif "Responsible Role" in table.cell(cell,0).text:
                    responsible_role = table.cell(cell,0).text.split(':')[1].strip()

                elif "Parameter" in table.cell(cell,0).text:
                    control = table.cell(cell, 0).text.split(':')[0]
                    parameter = table.cell(cell, 0).text.replace(control, '').strip(':').strip()
                    control = control.replace('Parameter ', '').strip().replace('-0', '-').replace(' ', '')
                    
                    if control.count('-') == 2:
                        param_number = control[-1:] + ': '
                        control = control[:-2]
                        parameters[control] += param_number + parameter + '\n'
                    else:
                        parameters[control] += parameter + '\n'
        
        elif "solution" in table_title:
            
            if len(control_parent) == 5:
                # print('first')
                control = control_parent.replace('-0', '-') + "("
                matching_controls = Control.objects.filter(Q(number__contains=control) & ~Q(number__contains=' '))
                if not matching_controls:
                    control = control_parent.replace('-0', '-')
                    matching_controls = Control.objects.filter(number=control)
                for control_object in matching_controls:
                    # control_parts = get_control_parts(control_object.number)
                    control_parts = get_control_parts(control_object.number)
                    implementation_details, customer_responsibility = parse_solution_table(table, control_object, control_parts)
                    if control_parts['part_num']:
                        implementation_details = get_part_text(implementation_details, control_parts)
                        # print(control_object.number)
                        # print(implementation_details)
                    parameter = parameters[control_object.number]
                    if implementation_details:
                        implementations_grouped_by_team = split_implementations(implementation_details)
                        for split_implementation in implementations_grouped_by_team:
                            teams, solution = split_implementation
                            new_implementation = {
                                'control_object': control_object,
                                'solution': solution,
                                'customer_resp': customer_responsibility,
                                'teams': teams,
                                'control_origination': control_originations,
                                'implementation_status': implementation_status,
                                'parameter': parameter,
                                'responsible_role': responsible_role
                            }
                            create_implementation(new_implementation)

            elif len(control_parent) == 4:
                # print('second')
                control = control_parent.replace('-0', '-') + "("
                matching_controls = Control.objects.filter(Q(number__contains=control) & ~Q(number__contains=' '))
                if not matching_controls:
                    control = control_parent.replace('-0', '-')
                    matching_controls = Control.objects.filter(number=control)
                for control_object in matching_controls:
                    control_parts = get_control_parts(control_object.number)
                    implementation_details, customer_responsibility = parse_solution_table(table, control_object, control_parts)
                    if control_parts['part_num']:
                        implementation_details = get_part_text(implementation_details, control_parts)
                    parameter = parameters[control_object.number]
                    if implementation_details:
                        implementations_grouped_by_team = split_implementations(implementation_details)
                        for split_implementation in implementations_grouped_by_team:
                            teams, solution = split_implementation
                            new_implementation = {
                                'control_object': control_object,
                                'solution': solution,
                                'customer_resp': customer_responsibility,
                                'teams': teams,
                                'control_origination': control_originations,
                                'implementation_status': implementation_status,
                                'parameter': parameter,
                                'responsible_role': responsible_role
                            }
                            create_implementation(new_implementation)

            elif ' ' in control_parent and "Req." not in control_parent: #enhancements with spaces
                # print('third')
                control = control_parent.replace('-0', '-')
                matching_controls = Control.objects.filter(number__contains=control)
                for control_object in matching_controls:
                    control_parts = get_control_parts(control_object.number)
                    implementation_details, customer_responsibility = parse_solution_table(table, control_object, control_parts)           
                    if control_parts['part_num']:
                        implementation_details = get_part_text(implementation_details, control_parts)
                    parameter = parameters[control_object.number.replace(' ', '')]
                    # print(parameters)
                    if implementation_details:
                        implementations_grouped_by_team = split_implementations(implementation_details)
                        for split_implementation in implementations_grouped_by_team:
                            teams, solution = split_implementation
                            new_implementation = {
                                'control_object': control_object,
                                'solution': solution,
                                'customer_resp': customer_responsibility,
                                'teams': teams,
                                'control_origination': control_originations,
                                'implementation_status': implementation_status,
                                'parameter': parameter,
                                'responsible_role': responsible_role
                            }
                            create_implementation(new_implementation)
                    # new_implementation = {
                    #     'control_object': control_object,
                    #     'solution': implementation_details,
                    #     'customer_resp': customer_responsibility,
                    #     'teams': Team.objects.all(),
                    #     'control_origination': control_originations,
                    #     'implementation_status': implementation_status,
                    #     'parameter': parameter,
                    #     'responsible_role': responsible_role
                    # }
                    # create_implementation(new_implementation)
                    
            elif "Req." not in control_parent: #enhancements without spaces
                control_base = control_parent[:5]

                control_enhancement = control_parent[5:]

                control = control_base + ' ' + control_enhancement
                control = control.replace('-0', '-')

                matching_controls = Control.objects.filter(number__contains=control)
                if not matching_controls:
                    control_base = control_parent[:4]
                    # print(control_base)
                    control_enhancement = control_parent[4:]
                    # print(control_enhancement)
                    control = control_base + ' ' + control_enhancement
                    control = control.replace('-0', '-')
                    # print(control)
                    matching_controls = Control.objects.filter(number__contains=control)
                for control_object in matching_controls:
                    control_parts = get_control_parts(control_object.number)
                    implementation_details, customer_responsibility = parse_solution_table(table, control_object, control_parts)           
                    if control_parts['part_num']:
                        implementation_details = get_part_text(implementation_details, control_parts)
                    parameter = parameters[control_object.number]
                    if implementation_details:
                        implementations_grouped_by_team = split_implementations(implementation_details)
                        for split_implementation in implementations_grouped_by_team:
                            teams, solution = split_implementation
                            new_implementation = {
                                'control_object': control_object,
                                'solution': solution,
                                'customer_resp': customer_responsibility,
                                'teams': teams,
                                'control_origination': control_originations,
                                'implementation_status': implementation_status,
                                'parameter': parameter,
                                'responsible_role': responsible_role
                            }
                            create_implementation(new_implementation)


def split_implementations(implementation_details):
    # teams = Team.objects.all()
    # [(['team1', 'team2'],'solution'), (['team3', 'team4'],'solution'), (['team5'],'solution')]
    newline_split = implementation_details.split('\n')
    result = []
    solution_flag = False
    team_list = []
    solution = ''
    for line in newline_split:

        comma_separated = line.split(',')
        if Team.objects.filter(name=comma_separated[0].strip(' ,:')) and ':' in line:
            if solution_flag:
                result.append((team_list, solution))
                team_list = []
                solution = ''
            for team in comma_separated:
                team_list.append(Team.objects.get(name__iexact=team.strip(' ,:')))
            solution_flag = True
        elif solution_flag:
            solution += line + '\n'
    if team_list:
        result.append((team_list, solution))
    return result
            #this is the solution

            

        