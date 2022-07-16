import os
from kivy.app import App
from book import Book

# настройки приложения и константы с переменными времени выполнения

class AppInfo():
    def __init__(self) -> None:
        self.book = Book()
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
        