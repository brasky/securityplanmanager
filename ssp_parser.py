from docx import *
from .models import Control, Implementation
from django.db.models import Q

IMPLEMENTATION_STATUS_CHOICES = (
    ('Implemented', 'IM'),
    ('Partially Implemented', 'PI'),
    ('Planned', 'PL'),
    ('Alternative Implementation', 'AI'),
    ('Not Applicable', 'NA'),
)
CONTROL_ORIGINATION_CHOICES = (
    ('Service Provider Corporate', 'SPC'),
    ('Service Provider System Specific', 'SPS'),
    ('Service Provider Hybrid (Corporate and System Specific)', 'SPH'),
    ('Configured by Customer (Customer System Specific)', 'CBC'),
    ('Provided by Customer (Customer System Specific)', 'PBC'),
    ('Shared (Service Provider and Customer Responsibility)', 'SHA'),
    ('Inherited from pre-existing Provisional Authority to Operate (P-ATO)', 'INH'),
    ('Not Applicable', 'NOT'),
)	


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
                                        print(control_parent)
                                        print(implementation_status)
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
            



            if len(control_parent) == 5:
                # print('first if')
                control = control_parent.replace('-0', '-') + "("
                matching_controls = Control.objects.filter(Q(number__contains=control) & ~Q(number__contains=' '))
                if not matching_controls:
                    control = control_parent.replace('-0', '-')
                    matching_controls = Control.objects.filter(number=control)
                print(matching_controls)
                for control_object in matching_controls:
                    print(control_object.number)
                    print(implementation_status)
                    i = Implementation(control = control_object, parameter = parameters[control_object.number], implementation_status=implementation_status, control_origination=control_origination, customer_responsibility='', solution='')
                    i.save()
                    break
                    
                break
            elif len(control_parent) == 4:
                pass
                # break
            elif ' ' in control_parent and "Req." not in control_parent:
                # print('second if')
                control = control_parent.replace('-0', '-')
                # print(control)
                matching_controls = Control.objects.filter(number__contains=control)
                # print(matching_controls)
            elif "Req." not in control_parent:
                # print('else')
                control_base = control_parent[:5]
                control_enhancement = control_parent[5:]
                control = control_base + ' ' + control_enhancement
                control = control.replace('-0', '-')
                print(control)
                matching_controls = Control.objects.filter(number__contains=control)
                print(matching_controls)
  
                # control_test = 'AC-02(1)'
                # # 
                # control_test_base = control_test[:5]
                # control_test_enhancement = control_test[5:]
                # control_test = control_test_base + " " + control_test_enhancement
                # print(control_test)
                # control_test = control_test.replace('-0', '-')
                # print(control_test)
                # print(Control.objects.filter(number__contains=control_test))



                
                    
        # elif "solution" in table_title:

