import os
from typing import List
from copy import deepcopy
from .xml_parser import XmlParser
from .html_parser import Html_Parser
from .css_descriptor import CssDescriptor
from localizator import Get_text
from page_elements.bookframe import BookFrame

def resolve_space(text:str):
    if text == None or text == '' or text.isspace():
        text = Get_text('des_unknown')
    return text

def get_any_text_content(tag) -> str:
        if tag.content != []:
            txt= tag.get_text_if_only_plain_text()
            if txt != "":
                return txt
        else:
            if 'opf:file-as' in tag.attr:
                return tag.attr['opf:file-as']
        return ''

class EpubBookParser:
    def __init__(self, root:str) -> None:
        self.root_folder = root

    def get_containers_paths(self) -> List[str]:
        file_path = os.path.join(self.root_folder, "META-INF", "container.xml")
        encoding = XmlParser.determine_xml_encoding(file_path)
        result = []
        with open(file_path, mode = "r", encoding=encoding) as file:
            file_content = file.read()
        pos = file_content.find("<rootfiles")
        pos = file_content.find(">", pos)
        close = file_content.find(XmlParser.get_close_tag("rootfiles"), pos)

        if (pos == -1 | close == -1) :
            return result
        while ((pos < close) and pos > 0):
            pos = file_content.find("<rootfile", pos)
            if pos != -1:
                pos_close = file_content.find(">", pos)
                _, args = XmlParser().get_tag_arguments(file_content[pos:pos_close-1])
                pos = pos_close
                result.append(args['full-path'])
        return result
    
    def produce_description(self, metadata) -> List[BookFrame]:
        result = [
            BookFrame(Get_text('des_description'), 'title', {}),
            BookFrame(None, 'empty', {})
        ]
        entities = {
            "authors": [],
            "name": None,
            "book_id": None,
            "rights": None,
            "description": None,
            "publisher": None,
            "participants": [],
            "language": None,
            "source": None,
            "relation": None,
            "date": None,
            'subjects': [],
            "format": None,
        }
        for child in metadata.content:
            if child.tag == "dc:title":
                entities['name'] = get_any_text_content(child)
            elif child.tag == 'dc:creator':
                entities['authors'].append(get_any_text_content(child))
            elif child.tag == 'dc:language':
                entities['language'] = get_any_text_content(child)
            elif child.tag == 'dc:subject':
                entities['subjects'].append(get_any_text_content(child))
            elif child.tag == 'dc:date':
                entities['date'] = get_any_text_content(child)
            elif child.tag == 'dc:description':
                entities['description'] = get_any_text_content(child)
            elif child.tag == 'dc:identifier':
                entities['book_id'] = get_any_text_content(child)
            elif child.tag == 'dc:rights':
                entities['rights'] = get_any_text_content(child)
            elif child.tag == 'dc:contributor':
                person = [get_any_text_content(child), ""]
                if "opf:role" in child.attrs:
                    person[1] = child.attrs['opf:role']
                entities['participants'] = person
            elif child.tag == 'dc:publisher':
                entities['publisher'] = get_any_text_content(child)
            elif child.tag == 'dc:source':
                entities['source'] = get_any_text_content(child)
            elif child.tag == 'dc:relation':
                entities['relation'] = get_any_text_content(child)
            elif child.tag == 'dc:':
                entities[''] = get_any_text_content(child)
            elif child.tag == 'dc:format':
                entities['format'] = get_any_text_content(child)
            elif child.tag == 'meta':
                print('found meta in book description!')
            else:
                result.append(BookFrame(child.text, child.tag, child.attr))

        content = resolve_space(entities['name'])
        result.append(BookFrame(Get_text('des_name') + content, 'text', {}))

        if entities['authors'] == []:
            result.append(BookFrame(Get_text('des_author') + Get_text('des_unknown'), 'text', {}))
        elif len(entities['authors']) == 1:
            result.append(BookFrame(Get_text('des_author') + resolve_space(entities['authors'][0]), 'text', {}))
        else:
            authors_list = ",".join(entities['authors'])
            result.append(BookFrame(Get_text('des_authors') + resolve_space(authors_list), 'text', {}))
        
        content = resolve_space(entities['date'])
        result.append(BookFrame(Get_text('des_date') + content, 'text', {}))
        content = resolve_space(entities['language'])
        result.append(BookFrame(Get_text('des_lang') + content, 'text', {}))
        if len(entities['subjects']) != 0:
            text = Get_text('des_ganres') + " "
            text += ', '.join(entities['subjects'])
            result.append(BookFrame(text,'text', {}))

        if entities['book_id']:
            content = resolve_space(entities['book_id'])
            result.append(BookFrame("id:  " + content, 'text', {}))
        if entities['format']:
            content = resolve_space(entities['format'])
            result.append(BookFrame(Get_text('des_format') + content, 'text', {}))

        content = resolve_space(entities['publisher'])
        result.append(BookFrame(Get_text('des_publisher') + content, 'text', {}))

        if entities['source']:
            content = resolve_space(entities['source'])
            result.append(BookFrame(Get_text('des_source') + content, 'text', {}))
        if entities['relation']:
            content = resolve_space(entities['relation'])
            result.append(BookFrame(Get_text('des_relation') + content, 'text', {}))

        content = resolve_space(entities['description'])
        if len(content) > 15:
            result.append(BookFrame(Get_text('des_annotation'), 'text',{}))
            result.append(BookFrame(content, 'text', {}))
        else:
            text = Get_text('des_annotation') + '\n' + content
            result.append(BookFrame(text, 'text', {}))
        
        if entities['rights']:
            content = resolve_space(entities['rights'])
            result.append(BookFrame(Get_text('des_author_rights') + content, 'text', {}))

        if entities['participants'] != []:
            result.append(BookFrame("[b]" + Get_text('des_contributors') + "[/b]", 'p', {}))

        return result

    def get_book_content(self, rootfile):
        root_file_path = os.path.join(self.root_folder, rootfile)
        xml_parser = XmlParser()
        opf_file_content = xml_parser.parce_xml_file(root_file_path)
        metadata = opf_file_content.find_tag_in_tree("metadata")
        manifest = opf_file_content.find_tag_in_tree("manifest")
        spine = opf_file_content.find_tag_in_tree('spine')
        guide = opf_file_content.find_tag_in_tree("guide")
        root_folder = os.path.dirname(root_file_path)
        pages = []
        notes = {}
        page_num = 2

        if metadata != None:
            pages.append(self.produce_description(metadata))
        files = {}
        for tag in manifest.content:
            id_ = tag.attr['id']
            path = tag.attr['href']
            files[id_] = path
        css_files = [files[id_] for id_ in files if files[id_][-4:] == '.css']
        styles = {}
        for style in css_files:
            descriptor = CssDescriptor()
            descriptor.update_from_file(os.path.join(root_folder, style))
            styles[style] = descriptor

        html_parser = Html_Parser()
        for element in spine.content:
            style_descriptor = CssDescriptor()

            page_id = element.attr['idref']
            file_path = files[page_id]
            html_document_path = os.path.join(root_folder, file_path)
            html_document_folder = os.path.dirname(html_document_path)
            html_document_name = os.path.basename(html_document_path)
            
            html_tag = html_parser.parce_xml_file(html_document_path)
            style_tag = html_tag.find_tag_in_tree('style')
            if style_tag != None:
                style_descriptor.update_from_string(style_tag.text)
            header = html_tag.find_tag_in_tree('head')
            included_files = header.find_all_tags_in_tree("link")
            for included_file in included_files:
                if 'href' in included_file.attr:
                    if '.css' in included_file.attr['href']:
                        file = included_file.attr['href']
                        right_path = file
                        if not file in styles:
                            folder = os.path.dirname(file_path)
                            right_path = os.path.join(folder, file)
                        if right_path in styles:
                            style_descriptor.update_from_descriptor(styles[right_path])
                        else:
                            print('can\'t find src for file', file, 'for entity', file_path)
            style_descriptor.register_new_font(root_folder)
            body_tag = html_tag.find_tag_in_tree('body')
            if body_tag != None:
                page_content = body_tag.work(style_descriptor, html_document_folder)
                pages.append(page_content)

            notes[html_document_name] = page_num
            page_num += 1

        return pages, notes







