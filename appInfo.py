import os
from kivy.app import App

# настройки приложения и константы с переменными времени выполнения

class AppInfo():
    def __init__(self) -> None:
        self.book = None
        self.max_elements_per_page = 10
        self.library = []
        self.book_dir = ''
        self.supported_formats = ['.fb2']
        self.supported_interface_languages = ['ru', 'en']
        self.interface_language = ''
    
    def read_settings(self):
        dir = App.get_running_app().user_data_dir 
        filename = os.path.join(dir, 'settings.txt')
        if not os.path.exists(filename):
            return False
        try:
            with open(filename) as file:
                data = file.readlines()
                self.interface_language = data[0]
        except Exception as e:
            print(e)
            return False
        return True
    
    def write_settings(self):
        dir = App.get_running_app().user_data_dir 
        dir = os.path.join(dir, 'settings.txt')
        try:
            with open(dir, mode='w') as file:
                file.write(self.interface_language)
        except Exception as e:
            print('can\'t write settings')
            print(e)

    def set_language(self, new_lang):
        self.interface_language = new_lang
        self.write_settings()
    
    def remember_page(self, page):
        dir = App.get_running_app().user_data_dir 
        filename = 'page.txt'
        page_str = str(page)
        book_file = self.book.file_path
        book_name = os.path.split(book_file)[-1]
        with open(os.path.join(dir, filename), mode='w') as file:
            file.write(book_name + '\n' + page_str)
    
    def get_last_page(self):
        """returns list of bookname, page  or None if no last book"""
        dir = App.get_running_app().user_data_dir 
        filename = 'page.txt'
        full_path = os.path.join(dir, filename)
        if not os.path.exists(full_path):
            return None
        with open(full_path, mode='r') as file:
            data = file.read()
        book, page = data.split('\n')
        
        return book, int(page)
        

        