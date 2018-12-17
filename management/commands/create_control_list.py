import xmltodict
from re import sub
import re, csv


control_catalog = {}
guidance_catalog = {}

def convert_control_number(control_number):
    parens = ['(', ')']
    if ")" in control_number or "(" in control_number:
        return control_number
    if '.' not in control_number:
        return control_number
    
    if control_number.count('.') == 1:
        # PM-4b.
        # PM-10a.
        letter = re.search('[a-z]', control_number).group()
        control_number = control_number.replace(letter, '(' + letter + ')')
        control_number = control_number.strip('.')
        return control_number

    elif control_number.count('.') == 2:
        control_number = control_number.replace('.','')
        letter = re.search('[a-z]', control_number).group()
        control_number = control_number.replace(letter, '(' + letter + ')')
        control_number = control_number[:-1] + '(' + control_number[-1] + ')'
        return control_number
        # PM-1a.1.
        # PM-14a.1.
    else:
        print('Missing case: ' + control_number)

# PM-5
# PM-12
# SI-1 (2)
# SI-10 (2)
# SI-1 (1)(a)
# SI-10 (1)(a)
# MA-5 (1)(a)(1)
# MA-15 (1)(a)(1)
# print('testing converter')
# test_controls = ['PM-4b.', 'PM-10a.', 'PM-1a.1.', 'PM-14a.1.', 'MA-15 (1)(a)(1)', 'MA-5 (1)(a)(1)', 'SI-10 (2)', 'PM-12', 'PM-5']
# for control in test_controls:
#     print(control)
#     print(convert_control_number(control))
#     print('-----------')

# print('done converter tests')

def add_main_controls_to_catalog(control):
    first_statement = control.get('statement')
    supplemental_guidance = ""
    if control.get('supplemental-guidance'):
        if control.get('supplemental-guidance').get('description'):
            supplemental_guidance = control.get('supplemental-guidance').get('description')
        
    if first_statement.get('statement'):
        second_statement = first_statement.get('statement')
        for statement in second_statement:
            if statement.get('statement'):
                for final_statement_dict in statement.get('statement'):
                    control_number = convert_control_number(final_statement_dict.get('number'))
                    statements = (first_statement, statement, final_statement_dict)
                    description = ' '.join(list(map(get_description, statements)))
                    control_catalog[control_number] = description
                    if supplemental_guidance:
                        guidance_catalog[control_number] = supplemental_guidance
            else:
                control_number = convert_control_number(statement.get('number'))
                statements = (first_statement, statement)
                description = ' '.join(list(map(get_description, statements)))
                control_catalog[control_number] = description
                if supplemental_guidance:
                    guidance_catalog[control_number] = supplemental_guidance

    else:
        control_number = convert_control_number(control.get('number'))
        description = get_description(first_statement)
        control_catalog[control_number] = description
        if supplemental_guidance:
            guidance_catalog[control_number] = supplemental_guidance


def get_description(statement):
    return statement.get('description')


def add_enhancements_to_catalog(control):
    if control.get('control-enhancements'):
        if isinstance(control.get('control-enhancements').get('control-enhancement'), list):
            for enhancement in control.get('control-enhancements').get('control-enhancement'):
                supplemental_guidance = ''
                try:
                    
                    if enhancement.get('supplemental-guidance'):
                        if enhancement.get('supplemental-guidance').get('description'):
                            supplemental_guidance = enhancement.get('supplemental-guidance').get('description')
                    first_statement = enhancement.get('statement')
                    if first_statement.get('statement'):
                        for second_statement in first_statement.get('statement'):
                            if second_statement.get('statement'):
                                for final_statement_dict in second_statement.get('statement'):
                                    statements = (first_statement, second_statement, final_statement_dict )
                                    control_number = convert_control_number(final_statement_dict.get('number'))
                                    description = ' '.join(list(map(get_description, statements)))
                                    control_catalog[control_number] = description
                                    if supplemental_guidance:
                                        guidance_catalog[control_number] = supplemental_guidance
                            else:
                                control_number = convert_control_number(second_statement.get('number'))
                                statements = (first_statement, second_statement)
                                description = ' '.join(list(map(get_description, statements)))
                                control_catalog[control_number] = description
                                if supplemental_guidance:
                                    guidance_catalog[control_number] = supplemental_guidance
                    else:
                        control_number = convert_control_number(enhancement.get('number'))
                        description = get_description(first_statement)
                        control_catalog[control_number] = description
                        if supplemental_guidance:
                            guidance_catalog[control_number] = supplemental_guidance
                except:
                    control_number = convert_control_number(control.get('control-enhancements').get('control-enhancement').get('number'))
                    description = get_description(control.get('control-enhancements').get('control-enhancement').get('statement'))
                    control_catalog[control_number] = description
                    if supplemental_guidance:
                        guidance_catalog[control_number] = supplemental_guidance
        else:
            supplemental_guidance = ''
            if control.get('control-enhancements').get('control-enhancement').get('supplemental-guidance'):
                if control.get('control-enhancements').get('control-enhancement').get('supplemental-guidance').get('description'):
                    supplemental_guidance = control.get('control-enhancements').get('control-enhancement').get('supplemental-guidance').get('description')
            if control.get('control-enhancements').get('control-enhancement').get('statement').get('statement'):
                first_statement = control.get('control-enhancements').get('control-enhancement').get('statement')
                for statement in first_statement.get('statement'):
                    statements = (first_statement, statement)
                    control_number = convert_control_number(statement.get('number'))
                    description = ' '.join(list(map(get_description, statements)))
                    control_catalog[control_number] = description
                    if supplemental_guidance:
                        guidance_catalog[control_number] = supplemental_guidance
            else:
                control_number = convert_control_number(control.get('control-enhancements').get('control-enhancement').get('number'))
                description = get_description(control.get('control-enhancements').get('control-enhancement').get('statement'))
                control_catalog[control_number] = description
with open('800-53-controls.xml') as controls_xml:
    control_dict = xmltodict.parse(controls_xml.read())
    # print("")
    for control in control_dict['controls:controls']['controls:control']:
        add_main_controls_to_catalog(control)
        add_enhancements_to_catalog(control)
        
print(len(control_catalog))
for control, description in control_catalog.items():
    # print(control)
    if control == None:
        print("Control value is none for this description: " + description)

    if description == None:
        print("Control description blank: " + control)
    
with open('control-list.csv','w', newline='') as f:
    w = csv.writer(f)
    w.writerows(control_catalog.items())

with open('control_guidance_list.csv', 'w', newline='') as f:
    w = csv.writer(f)
    w.writerows(guidance_catalog.items())
print("Done")









# PM-5
# PM-12
# SI-1 (2)
# SI-10 (2)
# SI-1 (1)(a)
# SI-10 (1)(a)
# MA-5 (1)(a)(1)
# MA-15 (1)(a)(1)





# PM-4b.
# PM-5
# PM-6
# PM-7
# PM-8
# PM-9a.
# PM-9b.
# PM-9c.
# PM-10a.
# PM-10b.
# PM-10c.
# PM-11a.
# PM-11b.
# PM-12
# PM-13
# PM-14a.1.
# PM-14a.2.
# PM-14b.
# PM-15a.
# PM-15b.
# PM-15c.
# SI-10 (1)(a)
# SI-10 (1)(b)
# SI-10 (1)(c)
# SI-10 (2)
# SI-10 (3)
# SI-10 (4)
# SI-10 (5)
# SI-11a.
# SI-11b.
# SI-12
# SI-13a.
# SI-13b.
# SI-13 (1)
# SI-13 (2)
# SI-13 (3)
# SI-13 (4)(a)
# SI-13 (4)(b)
# SI-13 (5)
# SI-14
