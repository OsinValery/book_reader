import os
from typing import List
from .xml_parser import XmlParser
from .html_parser import Html_Parser
from .css_descriptor import CssDescriptor
from localizator import Get_text
from bookframe import BookFrame

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
                _, args = XmlParser.get_tag_arguments(file_content[pos:pos_close-1])
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
        }
        for child in metadata.content:
            if child.tag == "dc:title":
                entities['name'] = get_any_text_content(child)
            elif child.tag == 'dc:creator':
                entities['authors'].append(get_any_text_content(child))
            elif child.tag == 'dc:language':
                entities['language'] = get_any_text_content(child)
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

        if entities['book_id']:
            content = resolve_space(entities['book_id'])
            result.append(BookFrame("id:  " + content, 'text', {}))

        content = resolve_space(entities['publisher'])
        result.append(BookFrame(Get_text('des_publisher') + content, 'text', {}))

        if entities['source']:
            content = resolve_space(entities['source'])
            result.append(BookFrame(Get_text('des_source') + content, 'text', {}))
        if entities['relation']:
            content = resolve_space(entities['relation'])
            result.append(BookFrame(Get_text('des_relation') + content, 'text', {}))

        content = resolve_space(entities['description'])
        result.append(BookFrame(Get_text('des_annotation') + content, 'text', {}))
        
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
        pages = []
        notes = {}

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
            descriptor.update_from_file(os.path.join(self.root_folder, style))
            styles[style] = descriptor

        html_parser = Html_Parser()
        for element in spine.content:
            page_id = element.attr['idref']
            file_path = files[page_id]
            style_descriptor = CssDescriptor()
            html_tag = html_parser.parce_xml_file(os.path.join(self.root_folder, file_path))
            style_tag = html_tag.find_tag_in_tree('style')
            if style_tag != None:
                print(style_tag.tag)
                print(style_tag.text)
                print(style_tag.attr)
            header = html_tag.find_tag_in_tree('head')
            included_files = header.find_all_tags_in_tree("link")
            body_tag = html_tag.find_tag_in_tree('body')
            if body_tag != None:
                page_content = body_tag.work(style_descriptor, self.root_folder)
                pages.append(page_content)
                

        return pages, notes







