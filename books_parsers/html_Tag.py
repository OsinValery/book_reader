import os
from .xml_tag import Xml_Tag
from typing import List, Dict
from bookframe import BookFrame
from .css_descriptor import CssDescriptor
from .css_measurement_systems import work_measurement_systems_for_inheritance

class Html_Tag(Xml_Tag):
    def apply_style(self, styles: CssDescriptor):
        css = {}
        if self.tag in styles.content:
            css.update(styles.content[self.tag])
        if 'class' in self.attr:
            class_ = self.attr['class']
            subclasses: str = class_.split()
            for subclass in subclasses:
                if self.tag + "." + subclass in styles.content:
                    css.update(styles.content[self.tag + "." + subclass])
                elif "." + subclass in styles.content:
                    css.update(styles.content["." + subclass])
        if 'style' in self.attr:
            small_descriptor = CssDescriptor()
            small_descriptor.update_from_string(self.tag + ' {' + self.attr['style'] + '}')
            css.update(small_descriptor.content[self.tag])
        if not 'another' in self.attr:
            self.attr['another'] = css
        else:
            self.apply_my_css_properties_from_dict(css)
    
    def apply_my_css_properties_from_dict(self, properties: Dict[str, object]):
        numeric_properties = [
            'font-size', 'border-spacing', 'letter-spacing', 'line-height',
            'pitch-range', 'pitch', 'richness', 'text-indent', 'word-spacing'
        ]
        for property_ in properties:
            if (property_ in self.attr['another']) and ('important' in self.attr['another'][property_]):
                print('found important for tag', self.tag)
            else:
                parent_value = '16px'
                if property_ in self.attr['another']:
                    parent_value = self.attr['another'][property_]
                if property_ in numeric_properties:
                    self.attr['another'][property_] = \
                    new_value = work_measurement_systems_for_inheritance(properties[property_], parent_value)
                    self.attr['another'][property_] = new_value
                else:
                    self.attr['another'][property_] = properties[property_]
                # TODO do transormations of measurements systems

    def cunstruct_text(self, styles: CssDescriptor) -> str:
        text = ""
        for child in self.content:
            if child.tag == "plain_text":
                text += child.text
            elif child.tag == "strong":
                text += '<strong>' + child.construct_text(styles) + "</strong>"
            elif child.tag == 'br':
                text += '\n'
            elif child.tag == 'p':
                text += child.cunstruct_text(styles)
            elif child.tag == 'i':
                text += ' <emphasis> ' + child.cunstruct_text(styles) + ' </emphasis> '
            elif child.tag == 'a':
                print(child.print())
                print(child.attr)
            else:
                print("unknown element:", child.tag)
                print('in Html_Tag.cunstruct_text')
        return text
    
    def share_css_property_with_child(self, child:'Html_Tag', css: str, is_numeric = False):
        if not 'another' in child.attr:
            child.add_attribute('another', {})
        if css in child.attr['another']:
            if 'important' not in child.attributs['another'][css]:
                child.attr['another'][css] = self.attr['another'][css]
            # TODO if numeric or % then should find total value
        else:
            child.attr['another'][css] = self.attr['another'][css]

    def share_css_properties_with_child(self, child: 'Html_Tag'):
        numeric_properties = [
            'font-size', 'border-spacing', 'letter-spacing', 'line-height',
            'pitch-range', 'pitch', 'richness', 'text-indent', 'word-spacing'
        ]
        string_properties = [
            'color', 'border-collapse', 'caption-side', 'direction', 
            'list-style-image', 'list-style-position', 'list-style-type',
            'list-style', 'qotes', 'text-align', 'visibility', 'text-transform'
        ]
        for css_property in self.attr['another']:
            if css_property in string_properties:
                self.share_css_property_with_child(child, css_property, False)
            elif css_property in numeric_properties:
                self.share_css_property_with_child(child, css_property, True)
            elif css_property == 'orphans':
                # TODO add suport
                pass
            elif css_property == 'widows':
                pass

    def work(self, styles = CssDescriptor(), root_path = "") -> List[BookFrame]:
        self.apply_style(styles)
        for child in self.content:
            self.share_css_properties_with_child(child)
        if (self.tag == "p"):
            text = self.cunstruct_text(styles)
            return [BookFrame(text, 'html_p', self.attr)]
        if self.tag == 'h1':
            text = self.cunstruct_text(styles)
            return [BookFrame(text, 'title', self.attr)]
        if self.tag in ['h2', "h3", 'h4', 'h5', 'h6']:
            text = self.cunstruct_text(styles)
            attr = self.attr
            attr['lavel'] = self.tag
            return [BookFrame(text, 'subtitle', self.attr)]

        if self.tag == 'img':
            if 'src' in self.attr:
                full_path = os.path.join(root_path, self.attr['src'])
                self.attr['path'] = full_path
                return [BookFrame(None, "file_image", self.attr)]
            elif 'alt' in self.attr:
                return [BookFrame(self.attr['alt'],'subtitle', {})]
            else:
                return [BookFrame("broken image",'subtitle', {})]

        if self.tag == 'image':
            if 'xlink:href' in self.attr:
                full_path = os.path.join(root_path, self.attr['xlink:href'])
                self.attr['path'] = full_path
                if 'height' in self.attr:
                    self.attr['another']['height'] = self.attr['height']
                if 'width' in self.attr:
                    self.attr['another']['width'] = self.attr['width']
                return [BookFrame(None, "file_image", self.attr)]
            else:
                return [BookFrame("broken image",'subtitle', {})]
        
        if self.tag == 'script' or self.tag == 'br':
            return []
        
        if self.tag == 'blockquote':
            children = []
            for el in self.content:
                new_children = el.work(styles, root_path)
                for new_child in new_children:
                    new_child.add_attribute('cite', True)
                    children.append(new_child)
            return children

        if self.tag in ['body', 'div', "section", 'span', 'svg']:
            result = []
            child: Html_Tag = None
            for child in self.content:
                result += child.work(styles, root_path)
            return result
        print('unknown tag: ', self.tag)
        print('content:')
        print(self.attr)
        print(self.text)
        print(self.content)
        return [BookFrame(self.text, self.tag, self.attr)]







