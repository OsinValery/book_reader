from book import Book

# настройки приложения и константы с переменными времени выполнения

class AppInfo():
    def __init__(self) -> None:
        self.book = Book()
        self.max_elements_per_page = 10
        self.library = []
        self.book_dir = ''
        self.supported_formats = ['.fb2']