import kivy.metrics as metrics
from typing import List

sims = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '.']

def split_value_and_points(value: str):
    pos = 0
    while (pos < len(value)) and value[pos] in sims:
        pos += 1
    return value[:pos], value[pos:].split()[0].strip()

def get_in_percents(value):
    try:
        value = value.replace('%', '')
        return float(value) / 100
    except:
        return None

def work_measurement_systems_for_inheritance(value: str, parent_value: str) -> str:
    if 'inherit' in value:
        return parent_value
    elif 'initial' in value:
        print('found initial')
    elif 'unset' in value:
        print('found unset')
    try:
        float(value)
        return value
    except:
        pass
    # here value have measurement points excectly
    num_value, points = split_value_and_points(value)
    parent_num_value, parent_points = split_value_and_points(parent_value)
    if points == '%':
        proportion = get_in_percents(num_value)
        if proportion == None: return parent_value
        return str(proportion * float(parent_num_value)) + parent_points
    elif points in ['mm', 'cm', 'in', 'pt', 'px', 'ex', 'ch', 'vw', 'vh', 'vmin', 'vmax']:
        return value
    elif points.upper() == 'Q':
        return str(1/40 * float(num_value)) + 'cm'
    elif points == 'pc':
        return str(1/6 * float(num_value)) + 'in'
    elif points == 'rem':
        return str(16 * float(num_value)) + 'px'
    elif points == 'em':
        return str(float(num_value) * float(parent_num_value)) + parent_points
    print('unknown measurement system!', value)
    return '16px'



def get_size_for_performance(value: str, default: int, window_size: List[float], viewPort:List[float], is_textual = False) -> str:
    '''returns value with <digits>, px or in'''
    default_ms = 'px'
    if is_textual:
        default_ms = 'sp'
    if 'inherit' in value:
        return str(default) + default_ms
    elif 'initial' in value:
        print('found initial')
    elif 'unset' in value:
        print('found unset')
    try:
        float(value)
        return value
    except:
        pass
    num_value, points = split_value_and_points(value)

    if points == '%':
        proportion = get_in_percents(num_value)
        if proportion == None: return default
        return str(proportion * default) + 'px'
    elif points in ['mm', 'cm', 'in', 'pt', 'px']:
        return value
    elif points.upper() == 'Q':
        return str(1/40 * float(num_value)) + 'cm'
    elif points == 'pc':
        return str(1/6 * float(num_value)) + 'in'
    elif points == 'rem':
        return str(16 * float(num_value)) + default_ms
    elif points == 'em':
        result = str(float(num_value) * default) + default_ms
        return result
    print('unknown measurement system!', value)
    'ex', 'ch', 'vw', 'vh', 'vmin', 'vmax'
    return '16px'

