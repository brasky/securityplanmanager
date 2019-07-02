import re

def is_enhancement(control):
    r = r'[A-Z]*-[0-9]*\([0-9].*'
    r = re.compile(r)
    if r.search(control):
        return True
    return False
  
def remove_zero(control):
    return control.replace('-0', '-')

def add_space_to_extension(control):
    regex = r'(\w\w-\d*)(.*)'
    control = re.sub(regex, r'\1 \2', control)
    return control

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