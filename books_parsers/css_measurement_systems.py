from copy import deepcopy
from typing import List

sims = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '.', '-']
default_font_size = '18sp'

def clear_css_value(value: str):
    if value == "": return ""
    return value.split()[0]

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

def work_measurement_systems_for_inheritance(value: str, parent_value: str, default_value: str) -> str:
    if 'inherit' in value:
        return parent_value
    elif 'initial' in value:
        return default_value
    elif 'unset' in value:
        return default_value
    try:
        float(value)
        return value
    except:
        pass
    # here value have measurement points excectly
    if value in font_size_words: value = font_size_words[value]
    if parent_value in font_size_words: parent_value = font_size_words[parent_value]
    num_value, points = split_value_and_points(value)
    parent_num_value, parent_points = split_value_and_points(parent_value)
    if points == '%':
        proportion = get_in_percents(num_value)
        if proportion == None: return parent_value
        return str(proportion * float(parent_num_value)) + parent_points
    elif points in ['sp', 'mm', 'cm', 'in', 'pt', 'px', 'ex', 'ch', 'vw', 'vh', 'vmin', 'vmax']:
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
    return default_font_size



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
    elif points in ['sp', 'mm', 'cm', 'in', 'pt', 'px']:
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

def get_color_from_code(value: str):
    value = value.strip()
    digits = []
    for el in value.split(","):
        d_el = el.strip()
        if '%' in d_el:
            d_el.replace('%', '')
            try:
                digits.append(float(d_el) / 100 * 255)
            except:
                pass
        else:
            try:
                digits.append(float(d_el))
            except:
                pass
    
    if len(digits) in [3,4]:
        colors = []
        for d in digits:
            if d > 1:
                colors.append(d / 255)
            else:
                colors.append(d)
        return colors

def decrease_font_size_by_one(value: str):
    return decrease_font_size_by_value(value, 1)

def decrease_font_size_by_value(value: str, dec: float):
    if 'inherit' in value:
        return value
    elif 'initial' in value:
        print('found initial')
    elif 'unset' in value:
        print('found unset')

    if value in font_size_words:
        value = font_size_words[value]

    return safe_decrease_font_size_by_value(value, dec)

def safe_decrease_font_size_by_value(value:str, dec:float):
    try:
        float(value)
        return str(max(float(value) - dec), 0)
    except:
        pass
    
    val, ms = split_value_and_points(value)
    return str(max(float(val) - dec, 0)) + ms


font_size_words = {
    'medium': default_font_size,
    'small': safe_decrease_font_size_by_value(default_font_size, 2),
    'large': safe_decrease_font_size_by_value(default_font_size, -2),
    'x-large': safe_decrease_font_size_by_value(default_font_size, -8),
    'xx-large': safe_decrease_font_size_by_value(default_font_size, -12),
    'x-small': safe_decrease_font_size_by_value(default_font_size, 8),
    'xx-small': safe_decrease_font_size_by_value(default_font_size, 12),
}

text_color = 'black'
default_css_properties = {
    'body': {
        'font-size': default_font_size,
        'color': text_color,
        'background-color': 'rgba(0,0,0,0)',
        'text-align': 'left',
        'font-weight': 'normal',
        'font-family': 'arial',
        'font-style': 'normal',
    },
    'p': {
        'font-size': default_font_size,
        'color': text_color,
        'background-color': 'rgba(0,0,0,0)',
        'text-align': 'left',
        'font-weight': 'normal',
        'font-family': 'arial',
        'font-style': 'normal',
    },
    'text': {
        'font-size': default_font_size,
        'color': text_color,
        'background-color': 'rgba(0,0,0,0)',
        'text-align': 'left',
        'font-weight': 'normal',
        'font-family': 'arial',
        'font-style': 'normal',
    },
    'b': {
        'font-size': default_font_size,
        'color': text_color,
        'background-color': 'rgba(0,0,0,0)',
        'text-align': 'left',
        'font-weight': 'normal',
        'font-family': 'arial',
        'font-style': 'normal',
    },

    'plain_text': {
        'font-size': default_font_size,
        'color': text_color,
        'background-color': 'rgba(0,0,0,0)',
        'text-align': 'left',
        'font-weight': 'normal',
        'font-family': 'arial',
        'font-style': 'normal',
    },
    'h1': {
        'font-size': default_font_size,
        'color': text_color,
        'background-color': 'rgba(0,0,0,0)',
        'text-align': 'left',
        'font-weight': 'normal',
        'font-family': 'arial',
        'font-style': 'normal',
    },
    'h2': {
        'font-size': default_font_size,
        'color': text_color,
        'background-color': 'rgba(0,0,0,0)',
        'text-align': 'left',
        'font-weight': 'normal',
        'font-family': 'arial',
        'font-style': 'normal',
    },
    'h3': {
        'font-size': default_font_size,
        'color': text_color,
        'background-color': 'rgba(0,0,0,0)',
        'text-align': 'left',
        'font-weight': 'normal',
        'font-family': 'arial',
        'font-style': 'normal',
    },
    'h4': {
        'font-size': default_font_size,
        'color': text_color,
        'background-color': 'rgba(0,0,0,0)',
        'text-align': 'left',
        'font-weight': 'normal',
        'font-family': 'arial',
        'font-style': 'normal',
    },
    'h5': {
        'font-size': default_font_size,
        'color': text_color,
        'background-color': 'rgba(0,0,0,0)',
        'text-align': 'left',
        'font-weight': 'normal',
        'font-family': 'arial',
        'font-style': 'normal',
    },
    'h6': {
        'font-size': default_font_size,
        'color': text_color,
        'background-color': 'rgba(0,0,0,0)',
        'text-align': 'left',
        'font-weight': 'normal',
        'font-family': 'arial',
        'font-style': 'normal',
    },
    'div': {
        'font-size': default_font_size,
        'color': text_color,
        'background-color': 'rgba(0,0,0,0)',
        'text-align': 'left',
        'font-weight': 'normal',
        'font-family': 'arial',
        'font-style': 'normal',
    },
    'span': {
        'font-size': default_font_size,
        'color': text_color,
        'background-color': 'rgba(0,0,0,0)',
        'text-align': 'left',
        'font-weight': 'normal',
        'font-family': 'arial',
        'font-style': 'normal',
    },
    'blockquote': {
        'font-size': default_font_size,
        'color': text_color,
        'background-color': 'rgba(0,0,0,0)',
        'text-align': 'left',
        'font-weight': 'normal',
        'font-family': 'arial',
        'font-style': 'normal',
    },
    'section': {
        'font-size': default_font_size,
        'color': text_color,
        'background-color': 'rgba(0,0,0,0)',
        'text-align': 'left',
        'font-weight': 'normal',
        'font-family': 'arial',
        'font-style': 'normal',
    },

}

default_css_properties['b'] = deepcopy(default_css_properties['p'])
default_css_properties['i'] = deepcopy(default_css_properties['p'])
default_css_properties['strong'] = deepcopy(default_css_properties['p'])
default_css_properties['em'] = deepcopy(default_css_properties['p'])
default_css_properties['sub'] = deepcopy(default_css_properties['p'])
default_css_properties['sup'] = deepcopy(default_css_properties['p'])
default_css_properties['small'] = deepcopy(default_css_properties['p'])

colors_words = {
    "aliceblue": "#F0F8FF",
    "antiquewhite": "#FAEBD7",
    "aqua":	"#00FFFF",
    "aquamarine": "#7FFFD4",
    "azure": "#F0FFFF",
    "beige": "#F5F5DC",
    "bisque": "#FFE4C4",
    "black": "#000000",
    "blanchedalmond": "#FFEBCD",
    "blue": "#0000FF",
    "blueviolet": "#8A2BE2",
    "brown": "#A52A2A",
    "burlywood": "#DEB887",
    "cadetblue": "#5F9EA0",
    "chartreuse": "#7FFF00",
    "chocolate": "#D2691E",
    "coral": "#FF7F50",
    "cornflowerblue": "#6495ED",
    "cornsilk": "#FFF8DC",
    "crimson": "#DC143C",
    "cyan": "#00FFFF",
    "darkblue": "#00008B",
    "darkcyan": "#008B8B",
    "darkgoldenrod": "#B8860B",
    "darkgray": "#A9A9A9",
    "darkgreen": "#006400",
    "darkgrey": "#A9A9A9",
    "darkkhaki": "#BDB76B",
    "darkmagenta": "#8B008B",
    "darkolivegreen": "#556B2F",
    "darkorange": "#FF8C00",
    "darkorchid": "#9932CC",
    "darkred": "#8B0000",
    "darksalmon": "#E9967A",
    "darkseagreen": "#8FBC8F",
    "darkslateblue": "#483D8B",
    "darkslategray": "#2F4F4F",
    "darkslategrey": "#2F4F4F",
    "darkturquoise": "#00CED1",
    "darkviolet": "#9400D3",
    "deeppink": "#FF1493",
    "deepskyblue": "#00BFFF",
    "dimgray": "#696969",
    "dimgrey": "#696969",
    "dodgerblue": "#1E90FF",
    "firebrick": "#B22222",
    "floralwhite": "#FFFAF0",
    "forestgreen": "#228B22",
    "fuchsia": "#FF00FF",
    "gainsboro": "#DCDCDC",
    "ghostwhite": "#F8F8FF",
    "gold": "#FFD700",
    "goldenrod": "#DAA520",
    "gray": "#808080",
    "green": "#008000",
    "greenyellow": "#ADFF2F",
    "grey": "#808080",
    "honeydew": "#F0FFF0",
    "hotpink": "#FF69B4",
    "indianred": "#CD5C5C",
    "indigo": "#4B0082",
    "ivory": "#FFFFF0",
    "khaki": "#F0E68C",
    "lavender": "#E6E6FA",
    "lavenderblush": "#FFF0F5",
    "lawngreen": "#7CFC00",
    "lemonchiffon": "#FFFACD",
    "lightblue": "#ADD8E6",
    "lightcoral": "#F08080",
    "lightcyan": "#E0FFFF",
    "lightgoldenrodyellow": "#FAFAD2",
    "lightgray": "#D3D3D3",
    "lightgreen": "#90EE90",
    "lightgrey": "#D3D3D3",
    "lightpink": "#FFB6C1",
    "lightsalmon": "#FFA07A",
    "lightseagreen": "#20B2AA",
    "lightskyblue": "#87CEFA",
    "lightslategray": "#778899",
    "lightslategrey": "#778899",
    "lightsteelblue": "#B0C4DE",
    "lightyellow": "#FFFFE0",
    "lime": "#00FF00",
    "limegreen": "#32CD32",
    "linen": "#FAF0E6",
    "magenta": "#FF00FF",
    "maroon": "#800000",
    "mediumaquamarine": "#66CDAA",
    "mediumblue": "#0000CD",
    "mediumorchid": "#BA55D3",
    "mediumpurple": "#9370DB",
    "mediumseagreen": "#3CB371",
    "mediumslateblue": "#7B68EE",
    "mediumspringgreen": "#00FA9A",
    "mediumturquoise": "#48D1CC",
    "mediumvioletred": "#C71585",
    "midnightblue": "#191970",
    "mintcream": "#F5FFFA",
    "mistyrose": "#FFE4E1",
    "moccasin": "#FFE4B5",
    "navajowhite": "#FFDEAD",
    "navy": "#000080",
    "oldlace": "#FDF5E6",
    "olive": "#808000",
    "olivedrab": "#6B8E23",
    "orange": "#FFA500",
    "orangered": "#FF4500",
    "orchid": "#DA70D6",
    "palegoldenrod": "#EEE8AA",
    "palegreen": "#98FB98",
    "paleturquoise": "#AFEEEE",
    "palevioletred": "#DB7093",
    "papayawhip": "#FFEFD5",
    "peachpuff": "#FFDAB9",
    "peru": "#CD853F",
    "pink": "#FFC0CB",
    "plum": "#DDA0DD",
    "powderblue": "#B0E0E6",
    "purple": "#800080",
    "red": "#FF0000",
    "rosybrown": "#BC8F8F",
    "royalblue": "#4169E1",
    "saddlebrown": "#8B4513",
    "salmon": "#FA8072",
    "sandybrown": "#F4A460",
    "seagreen": "#2E8B57",
    "seashell": "#FFF5EE",
    "sienna": "#A0522D",
    "silver": "#C0C0C0",
    "skyblue": "#87CEEB",
    "slateblue": "#6A5ACD",
    "slategray": "#708090",
    "slategrey": "#708090",
    "snow": "#FFFAFA",
    "springgreen": "#00FF7F",
    "steelblue": "#4682B4",
    "tan": "#D2B48C",
    "teal": "#008080",
    "thistle": "#D8BFD8",
    "tomato": "#FF6347",
    "turquoise": "#40E0D0",
    "violet": "#EE82EE",
    "wheat": "#F5DEB3",
    "white": "#FFFFFF",
    "whitesmoke": "#F5F5F5",
    "yellow": "#FFFF00",
    "yellowgreen": "#9ACD32"

}

