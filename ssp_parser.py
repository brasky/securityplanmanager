from docx import *
from .models import Control, Implementation, Team
from django.db.models import Q
import re
from time import sleep

def get_control_parts(control):
    control_parts = {'enhancement' : '', 'part_num': '', 'part_letter': ''}
    alpha = re.compile('[A-Za-z]')
    number = re.compile('[0-9]*')
    ALPHA_INDEX = {
    'a':'1','b':'2','c':'3','d':'4','e':'5','f':'6','g':'7','h':'8',
    'i':'9','j':'10','k':'11','l':'12','m':'13','n':'14','o':'15','p':'16','q':'17',
    'r':'18','s':'19','t':'20','u':'21','v':'22','w':'23','x':'24','y':'25','z':'26'
    }
    control = control[5:]
    control = control.lstrip()
    parts = []
    parts = control.split(')(')
    if len(parts) == 1 and parts[0] == "":
        control_parts['enhancement'] = False
        control_parts['part_letter'] = False
        control_parts['part_num'] = False
        return control_parts
    parts[0] = re.sub('[()]','',parts[0])
    parts[len(parts)-1] = re.sub('[()]','',parts[len(parts)-1])
    if len(parts) == 3:
        control_parts['enhancement'] = parts[0]
        control_parts['part_letter'] = parts[1]
        if "Ext" not in control_parts['part_letter']:
            control_parts['part_letter'] = int(ALPHA_INDEX[control_parts['part_letter']])
        control_parts['part_num'] = parts[2]
    elif alpha.match(parts[0]):
        if len(parts) == 2:
            control_parts['enhancement'] = False
            control_parts['part_letter'] = parts[0]
            if "Ext" not in control_parts['part_letter']:
                control_parts['part_letter'] = int(ALPHA_INDEX[control_parts['part_letter']])
            control_parts['part_num'] = parts[1]
        elif len(parts) == 1:
            control_parts['enhancement'] = False
            control_parts['part_letter'] = parts[0]
            if "Ext" not in control_parts['part_letter']:
                control_parts['part_letter'] = int(ALPHA_INDEX[control_parts['part_letter']])
            control_parts['part_num'] = False
    elif number.match(parts[0]):
        if len(parts) == 1:
            control_parts['enhancement'] = parts[0]
            control_parts['part_letter'] = False
            control_parts['part_num'] = False
        elif len(parts) == 2: 
            control_parts['enhancement'] = parts[0]
            control_parts['part_letter'] = parts[1]
            if "Ext" not in control_parts['part_letter']:
                control_parts['part_letter'] = int(ALPHA_INDEX[control_parts['part_letter']])
            control_parts['part_num'] = False
    
    return control_parts



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
                if team.name + ":" in part or "Part 1" in part or "Part 2" in part:
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
new_implementations = []
def create_implementation(new_implementation):
    new_implementation_object = Implementation(
        control=new_implementation['control_object'],
        parameter=new_implementation['parameter'],
        customer_responsibility=new_implementation['customer_resp'],
        solution=new_implementation['solution'],
        implementation_status=new_implementation['implementation_status'],
        control_origination=new_implementation['control_origination'],
        )
    new_implementations.append(new_implementation_object)
    # for implementation in new_implementations:
    #     implementation.save()
    #     implementation.teams.set(new_implementation['teams'])
    new_implementation_object.save()
    new_implementation_object.teams.set(new_implementation['teams'])

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
        implementation_details = table.cell(control_parts['part_letter'],1).text
        # print(control_number)

        customer_responsibility = get_customer_responsibility(implementation_details)
        if customer_responsibility:
            implementation_details = implementation_details.replace(customer_responsibility, '').strip()
        # print(customer_responsibility)
    else:#letter, part, no enhancement
        implementation_details = table.cell(control_parts['part_letter'],1).text
        # print(control_number)
        customer_responsibility = get_customer_responsibility(implementation_details)
        if customer_responsibility:
            implementation_details = implementation_details.replace(customer_responsibility, '').strip()
        # print(customer_responsibility)
    # else:
    #     raise ValueError('A case was not handled by the implementation table section of parse ssp')
    
    return implementation_details, customer_responsibility, 


namespace = {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
implementations = []
def parse_ssp(file):
    document = Document(file)
    # print('we made it here')
    for table in document.tables:
        table_title = table.cell(0,0).text
        # print(table_title)
        
        if len(table_title) < 20 and '-' in table_title:
            control_parent = table_title
            parameters = {}
            controls = {}
            parameter = ''
            rows = len(table.rows)
            for cell in range(1,rows):

                if "Implementation" in table.cell(cell,0).text:
                    for paragraph in table.cell(cell,0).paragraphs:
                        p = paragraph._element
                        checkBoxes = p.xpath('.//w:checkBox')
                        
                        if len(checkBoxes) > 0:
                            if len(checkBoxes[0].getchildren()) >= 2:
                                if checkBoxes[0].find('.//w:checked', namespace) is not None:
                                    if not checkBoxes[0].find('.//w:checked', namespace).values():
                                        implementation_status = p.xpath('.//w:t')[0].text.strip()
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
                                    
                elif "Control Origination" in table.cell(cell,0).text:
                    for paragraph in table.cell(cell,0).paragraphs:
                        p = paragraph._element
                        checkBoxes = p.xpath('.//w:checkBox')
                        if len(checkBoxes) > 0:
                            if len(checkBoxes[0].getchildren()) >= 2:
                                if checkBoxes[0].find('.//w:checked', namespace) is not None:
                                    if not checkBoxes[0].find('.//w:checked', namespace).values():
                                        control_origination = p.xpath('.//w:t')[0].text.strip()
                                        if "Corporate" in control_origination:
                                            control_origination = 'SPC'
                                        elif "Specific" in control_origination:
                                            control_origination = 'SPS'
                                        elif "Hybrid" in control_origination:
                                            control_origination = 'SPH'
                                        elif "Configured" in control_origination:
                                            control_origination = 'CBC'
                                        elif "Provided" in control_origination:
                                            control_origination = 'PBC'
                                        elif "Shared" in control_origination:
                                            control_origination = 'SHA'
                                        elif "Inherited" in control_origination:
                                            control_origination = 'INH'
                                        elif "Not" in control_origination:
                                            control_origination = 'NOT'
                                       

                elif "Responsible Role" in table.cell(cell,0).text:
                    responsible_role = table.cell(cell,0).text.split(':')[1].strip()

                elif "Parameter" in table.cell(cell,0).text:
                    control = table.cell(cell,0).text.split('\n')[0].replace('Parameter ', '').replace(':', '').strip().replace('-0', '-')
                    parameter = table.cell(cell,0).text.split(':')[1].strip()
                    parameters[control] = parameter
        
        elif "solution" in table_title:
            
            if len(control_parent) == 5:
                control = control_parent.replace('-0', '-') + "("
                matching_controls = Control.objects.filter(Q(number__contains=control) & ~Q(number__contains=' '))
                if not matching_controls:
                    control = control_parent.replace('-0', '-')
                    matching_controls = Control.objects.filter(number=control)
                for control_object in matching_controls:
                    control_parts = get_control_parts(control_object.number)
                    control_parts = get_control_parts(control_object.number)
                    implementation_details, customer_responsibility = parse_solution_table(table, control_object, control_parts)
                    if control_parts['part_num']:
                        implementation_details = get_part_text(implementation_details, control_parts)
                        # print(control_object.number)
                        # print(implementation_details)
                    try:
                        parameter = parameters[control]
                    except KeyError:
                        parameter = ''
                        pass
                    new_implementation = {
                        'control_object': control_object,
                        'solution': implementation_details,
                        'customer_resp': customer_responsibility,
                        'teams': Team.objects.all(),
                        'control_origination': control_origination,
                        'implementation_status': implementation_status,
                        'parameter': parameter
                    }
                    create_implementation(new_implementation)

            elif len(control_parent) == 4:
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
                    try:
                        parameter = parameters[control]
                    except KeyError:
                        parameter = ''
                        pass
                    new_implementation = {
                        'control_object': control_object,
                        'solution': implementation_details,
                        'customer_resp': customer_responsibility,
                        'teams': Team.objects.all(),
                        'control_origination': control_origination,
                        'implementation_status': implementation_status,
                        'parameter': parameter
                    }
                    create_implementation(new_implementation)


            elif ' ' in control_parent and "Req." not in control_parent:
                control = control_parent.replace('-0', '-')
                matching_controls = Control.objects.filter(number__contains=control)
                for control_object in matching_controls:
                    control_parts = get_control_parts(control_object.number)
                    implementation_details, customer_responsibility = parse_solution_table(table, control_object, control_parts)           
                    if control_parts['part_num']:
                        implementation_details = get_part_text(implementation_details, control_parts)
                    try:
                        parameter = parameters[control]
                    except KeyError:
                        parameter = ''
                        pass
                    new_implementation = {
                        'control_object': control_object,
                        'solution': implementation_details,
                        'customer_resp': customer_responsibility,
                        'teams': Team.objects.all(),
                        'control_origination': control_origination,
                        'implementation_status': implementation_status,
                        'parameter': parameter
                    }
                    create_implementation(new_implementation)
                    
            elif "Req." not in control_parent:
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
                    try:
                        parameter = parameters[control]
                    except KeyError:
                        parameter = ''
                        pass
                    new_implementation = {
                        'control_object': control_object,
                        'solution': implementation_details,
                        'customer_resp': customer_responsibility,
                        'teams': Team.objects.all(),
                        'control_origination': control_origination,
                        'implementation_status': implementation_status,
                        'parameter': parameter
                    }
                    create_implementation(new_implementation)
    
    # Implementation.objects.bulk_create(new_implementations)
    # ThroughModel = Implementation.teams.through
    # teams = Team.objects.all()
    # ThroughModel.objects.bulk_create()

# def create_implementation():
    

                    # control_test = 'AC-02(1)'
                    # # 
                    # control_test_base = control_test[:5]
                    # control_test_enhancement = control_test[5:]
                    # control_test = control_test_base + " " + control_test_enhancement
                    # print(control_test)
                    # control_test = control_test.replace('-0', '-')
                    # print(control_test)
                    # print(Control.objects.filter(number__contains=control_test))



                
                    


