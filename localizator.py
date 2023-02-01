

from kivy.utils import platform
import app_values

if platform == 'android':
    from jnius import autoclass
elif platform =='ios':
    from pyobjus import autoclass
if platform == 'macosx':
    try:
        from pyobjus import autoclass
    except:
        print('pyobjus was not imported')

def get_lang():
    # try detect device system language
    system_lang = ''
    try:
        if platform == 'android':
            lang = autoclass('java.util.Locale').getDefault().language
            if lang in app_values.app_info.supported_interface_languages:
                system_lang = lang
        elif platform == 'ios':
            NSLocal = autoclass("NSLocale")
            lang = NSLocal.preferredLocale().languageCode().cString().decode("utf-8")
            if lang in app_values.app_info.supported_interface_languages:
                system_lang = lang
        if platform == 'macosx':
            try:
                NSLocal = autoclass("NSLocale")
                lang = NSLocal.preferredLocale().languageCode().cString().decode("utf-8")
                if lang in app_values.app_info.supported_interface_languages:
                    system_lang = lang
            except:
                print('language not established')
    except:
        pass
    
    if system_lang == '':
        return 'ru'
    return system_lang


def Get_text(text, lang = None, details = None):
    if lang == None or lang not in app_values.app_info.supported_interface_languages:
        if app_values.app_info.interface_language == '':
            lang = get_lang()
        else:
            lang = app_values.app_info.interface_language 
    
    if text[:5] == 'info_':
        return infotext(text[5:], lang, details)
    elif text[:6] == 'error_':
        return error_message(text[6:], lang, details)
    elif text[:5] == 'lang_':
        return lang_code_text(text[5:])
    elif text[:6] == 'theme_':
        return theme_texts(text[6:], lang=lang)
    elif text[:4] == 'des_':
        return description_text(text[4:], lang, details)
    return 'unknown type of message: ' + text

def lang_code_text(code):
    if code == 'ru': return 'Русский'
    if code == 'en': return 'English'
    return 'unknown code: ' + code

def theme_texts(text, lang):
    if text == 'Light':
        if lang == 'ru':
            return 'Светлая'
        elif lang == 'en':
            return 'Light'
    if text == 'Dark':
        if lang == 'ru':
            return 'Тёмная'
        elif lang == 'en':
            return 'Dark'
    return 'unknown text or color'

def infotext(text, lang, details):
    if text == 'copy':
        if lang == 'ru':
            return 'Копировать'
        elif lang == 'en':
            return 'Copy'

    if text == 'cancel':
        if lang == 'ru':
            return 'Отмена'
        elif lang == 'en':
            return 'Cancel'

    if text == 'translate':
        if lang == 'ru':
            return 'Перевод'
        elif lang == 'en':
            return 'Translate'

    if text == 'text_copied':
        if lang == 'ru':
            return 'Текст скопирован буфер обмена'
        elif lang == 'en':
            return 'Text copied to clipboard'
    
    if text == 'unknown_note':
        if lang == 'ru':
            return 'Примечание не найдено!'
        elif lang == 'en':
            return 'This note don\'t found!'

    if text == 'click_text':
        if lang == 'ru':
            return 'click on the words in the text'
        elif lang == 'en':
            return 'Нажимайте на слова в тексте'

    if text == 'translated_text':
        if lang == 'ru':
            return 'Тут вы увидите перевод'
        elif lang == 'en':
            return 'Here you may see translated text'

    if text == 'again':
        if lang == 'ru':
            return 'Повторить'
        elif lang == 'en':
            return 'Again'

    if text == 'reader':
        if lang == 'ru':
            return 'Читалка'
        elif lang == 'en':
            return 'Reader'

    if text == 'page':
        if lang == 'ru':
            return 'Страница'
        elif lang == 'en':
            return 'Page'

    if text == 'library':
        if lang == 'ru':
            return 'Библиотека'
        elif lang == 'en':
            return 'Library'

    if text == 'settings':
        if lang == 'ru':
            return 'Настройки'
        elif lang == 'en':
            return 'Settings'

    if text == 'language':
        if lang == 'ru':
            return 'Язык'
        elif lang == 'en':
            return 'Language'

    if text == 'translater':
        if lang == 'ru':
            return 'Переводчик'
        elif lang == 'en':
            return 'Translater'

    if text == 'select_book':
        if lang == 'ru':
            return 'Выбрать книгу'
        elif lang == 'en':
            return 'Choose book'

    if text == 'book_start':
        if lang == 'ru':
            return 'Начало книги'
        elif lang == 'en':
            return 'Start'

    if text == 'book_end':
        if lang == 'ru':
            return 'Конец'
        elif lang == 'en':
            return 'End'

    if text == 'turn':
        if lang == 'ru':
            return 'Пролистать'
        elif lang == 'en':
            return 'flip through'

    if text == 'ok':
        if lang == 'ru':
            return 'Ок'
        elif lang == 'en':
            return 'Ok'

    if text == 'no':
        if lang == 'ru':
            return 'Нет'
        elif lang == 'en':
            return 'No'

    if text == 'translate_from':
        if lang == 'ru':
            return 'Перевести с '
        elif lang == 'en':
            return 'Translate from'

    if text == 'translate_to':
        if lang == 'ru':
            return 'Перевести на'
        elif lang == 'en':
            return 'Translate to'

    if text == 'translate_text':
        if lang == 'ru':
            return 'Переводить текст\nпо клику'
        elif lang == 'en':
            return 'Translate text\nby click'

    if text == 'select_text':
        if lang == 'ru':
            return 'Выделять текст'
        elif lang == 'en':
            return 'Select text'

    if text == 'change_theme':
        if lang == 'ru':
            return 'Тема'
        elif lang == 'en':
            return 'App theme'

    if text == '':
        if lang == 'ru':
            return ''
        elif lang == 'en':
            return ''

    return 'Unknown text: ' + text

def error_message(text, lang, details):
    if text == 'network_connection':
        if lang == 'ru':
            return 'Network exception. Please, check internet connection and try again.'
        elif lang == 'en':
            return 'Проблема с сетью. Пожалуйста, проверьте подключение к интернету и повторите попытку'
    if text == 'no_permission':
        if lang == 'ru':
            return 'У приложения нет разрешения на чтение файлов устройства. Вы можете разрешить это в настройках телефона или попробовать снова и разрешить чтение файлов.'
        elif lang == 'en':
            return 'This app have not permission to read files in internal storage of this device.You can repeat and allow read files or grant it in phone settings.'
    if text == 'error':
        if lang == 'ru':
            return 'Ошибка!'
        elif lang == 'en':
            return 'Error!'
    if text == 'already_exists':
        if lang == 'ru':
            return 'Книга {0} уже существует. Заменить?'
        elif lang == 'en':
            return 'Book {0} already exists. Replace?'
    if text == '':
        if lang == 'ru':
            return ''
        elif lang == 'en':
            return ''

    return 'unknown text: ' + text

def description_text(text, lang, details=None):
    if text == 'description':
        if lang == 'ru':
            return 'Описание книги'
        elif lang == 'en':
            return 'Book description'
    if text == 'name':
        if lang == 'ru':
            return 'Название: '
        elif lang == 'en':
            return 'Title: '
    if text == 'unknown':
        if lang == 'ru':
            return 'Неизвестно'
        elif lang == 'en':
            return 'Unknown'
    if text == 'author':
        if lang == 'ru':
            return 'Автор: '
        elif lang == 'en':
            return 'Author: '
    if text == 'authors':
        if lang == 'ru':
            return 'Авторы: '
        elif lang == 'en':
            return 'Authors: '
    if text == 'empty_person':
        if lang == 'ru':
            return 'Нет информации об этом человеке'
        elif lang == 'en':
            return 'No info about this person'
    if text == 'fio':
        if lang == 'ru':
            return 'ФИО: '
        elif lang == 'en':
            return 'Full name: '

    if text == 'nick':
        if lang == 'ru':
            return 'Ник: '
        elif lang == 'en':
            return 'Nickname: '
    if text == 'cites':
        if lang == 'ru':
            return 'Странички: '
        elif lang == 'en':
            return 'Cites: '
    if text == 'date':
        if lang == 'ru':
            return 'Дата написания: '
        elif lang == 'en':
            return 'Written at: '
    if text == 'lang':
        if lang == 'ru':
            return 'Язык: '
        elif lang == 'en':
            return 'Language: '
    if text == 'src-lang':
        if lang == 'ru':
            return 'Язык оригинала: '
        elif lang == 'en':
            return 'Original language: '
    if text == 'ganres':
        if lang == 'ru':
            return 'Жанры: '
        elif lang == 'en':
            return 'Genres: '
    if text == 'annotation':
        if lang == 'ru':
            return 'Аннотация: '
        elif lang == 'en':
            return 'Annotation: '
    if text == 'keywords':
        if lang == 'ru':
            return 'Ключевые слова: '
        elif lang == 'en':
            return 'Keywords: '
    if text == 'seq':
        if lang == 'ru':
            return 'Цикл: '
        elif lang == 'en':
            return 'Sequence: '
    if text == 'part':
        if lang == 'ru':
            return 'Часть '
        elif lang == 'en':
            return 'Part '
    if text == 'translator':
        if lang == 'ru':
            return 'Переводчик: '
        elif lang == 'en':
            return 'Translator: '
    if text == 'translators':
        if lang == 'ru':
            return 'Переводчики: '
        elif lang == 'en':
            return 'Translators: '
    if text == 'foreign':
        if lang == 'ru':
            return 'Оригинальная книга'
        elif lang == 'en':
            return 'Original book'
    if text == 'original_note':
        if lang == 'ru':
            return 'Некоторые поля в данном разделе могут быть незаполнены. Возможно, часть из них есть в первом разделе. '
        elif lang == 'en':
            return 'Some fields in this section may be left blank. Perhaps some of them are in the first section.'
    if text == 'publication':
        if lang == 'ru':
            return 'Публикация'
        elif lang == 'en':
            return 'Publication info'
    if text == 'custom':
        if lang == 'ru':
            return 'Дополнительная информация'
        elif lang == 'en':
            return 'Additional information'
    if text == 'type':
        if lang == 'ru':
            return 'Тип: '
        elif lang == 'en':
            return 'Type: '
    if text == 'info':
        if lang == 'ru':
            return 'Содержимое: '
        elif lang == 'en':
            return 'Content: '
    if text == 'document':
        if lang == 'ru':
            return 'О документе'
        elif lang == 'en':
            return 'About document'
    if text == 'publisher':
        if lang == 'ru':
            return 'Издатель: '
        elif lang == 'en':
            return 'Publisher: '
    if text == 'city':
        if lang == 'ru':
            return 'Город: '
        elif lang == 'en':
            return 'City: '
    if text == 'time':
        if lang == 'ru':
            return 'Дата: '
        elif lang == 'en':
            return 'Date: '
    if text == 'program':
        if lang == 'ru':
            return 'Создано программой: '
        elif lang == 'en':
            return 'Program used: '
    if text == 'program_id':
        if lang == 'ru':
            return 'Id программы: '
        elif lang == 'en':
            return 'Program id: '
    if text == 'scanner':
        if lang == 'ru':
            return 'Кто сканировал(для бумажного носителя): '
        elif lang == 'en':
            return 'Who scanned (for paper): '

    if text == 'doc_authors':
        if lang == 'ru':
            return 'Авторы документа: '
        elif lang == 'en':
            return 'Document\'s authors: '
    if text == 'source':
        if lang == 'ru':
            return 'Источник (ссылка): '
        elif lang == 'en':
            return 'Source (link): '
    if text == 'owner':
        if lang == 'ru':
            return 'Владельцы: '
        elif lang == 'en':
            return 'Owners: '
    if text == 'version':
        if lang == 'ru':
            return 'Версия: '
        elif lang == 'en':
            return 'Version: '
    if text == 'history':
        if lang == 'ru':
            return 'История: '
        elif lang == 'en':
            return 'History: '
    if text == 'id_note':
        if lang == 'ru':
            return 'Если где-то указано id, имеется ввиду внутренний id библиотеки, откуда скачан документ.'
        elif lang == 'en':
            return 'If an id is specified somewhere, it means the internal id of the library from where the document was downloaded.'

def get_genre(genre, lang = None):
    if lang == None or lang not in app_values.app_info.supported_interface_languages:
        if app_values.app_info.interface_language == '':
            lang = get_lang()
        else:
            lang = app_values.app_info.interface_language 
    
    genres = {
        'sf_history': {
            'ru': "Альтернативная история",
            'en': "Alternative history",
        },
        "sf_litrpg": {
            'ru': "Лит РПГ",
            'en': "Lit RTG",
        },
        'sf_action': {
            'ru': "Боевая фантастика",
            'en': "Combat fiction",
        },
        'sf_epic': {
            'ru': "Эпическая фантастика",
            'en': "Epic fiction",
        },
        'sf_heroic': {
            'ru': "Героическая фантастика",
            'en': "Heroic fiction",
        },
        'sf_detective': {
            'ru': "Детективная фантастика",
            'en': "Detective fiction",
        },
        'sf_cyberpunk': {
            'ru': "Киберпанк",
            'en': "Cyberpunk",
        },
        'sf_space': {
            'ru': "Космическая фантастика",
            'en': "Space fiction",
        },
        'sf_social': {
            'ru': "Социально-психологическая фантастика",
            'en': "Socio-psychological fiction",
        },
        'sf_horror': {
            'ru': "Ужасы и Мистика",
            'en': "Horror and Mysticism",
        },
        'sf_humor': {
            'ru': "Юмористическая фантастика",
            'en': "Humorous fiction",
        },
        'sf_fantasy': {
            'ru': "Фэнтези",
            'en': "Fantasy",
        },
        'sf': {
            'ru': "Научная Фантастика",
            'en': "Science fiction",
        },
        'det_classic': {
            'ru': "Классический детектив",
            'en': "Classic detective",
        },
        'det_police': {
            'ru': "Полицейский детектив",
            'en': "Police Detective",
        },
        'det_action': {
            'ru': "Боевик",
            'en': "Action",
        },
        'det_irony': {
            'ru': "Иронический детектив",
            'en': "Ironic Detective",
        },
        'det_history': {
            'ru': "Исторический детектив",
            'en': "Historical Detective",
        },
        'det_espionage': {
            'ru': "Шпионский детектив",
            'en': "Spy Detective",
        },
        'det_crime': {
            'ru': "Криминальный детектив",
            'en': "Criminal Detective",
        },
        'det_political': {
            'ru': "Политический детектив",
            'en': "Political Detective",
        },
        'det_maniac': {
            'ru': "Маньяки",
            'en': "Maniacs",
        },
        'det_hard': {
            'ru': "Крутой детектив",
            'en': "Cool detective",
        },
        'thriller': {
            'ru': "Триллер",
            'en': "Thriller",
        },
        'detective': {
            'ru': "Детектив",
            'en': "Detective",
        },
        'prose_classic': {
            'ru': "Классическая проза",
            'en': "Classical prose",
        },
        'prose_history': {
            'ru': "Историческая проза",
            'en': "Historical prose",
        },
        'prose_contemporary': {
            'ru': "Современная проза",
            'en': "Contemporary prose",
        },
        'prose_counter': {
            'ru': "Контркультура",
            'en': "Counterculture",
        },
        'prose_rus_classic': {
            'ru': "Русская классическая проза",
            'en': "Russian classical prose",
        },
        'prose_su_classics': {
            'ru': "Советская классическая проза",
            'en': "Soviet classical prose",
        },
        'love_contemporary': {
            'ru': "Современные любовные романы",
            'en': "Contemporary romance novels",
        },
        'love_history': {
            'ru': "Исторические любовные романы",
            'en': "Historical romance novels",
        },
        'love_detective': {
            'ru': "Остросюжетные любовные романы",
            'en': "Action-packed romance novels",
        },
        'love_short': {
            'ru': "Короткие любовные романы",
            'en': "Short romance novels",
        },
        'love_erotica': {
            'ru': "Эротика",
            'en': "Erotica",
        },
        'adv_western': {
            'ru': "Вестерн",
            'en': "Western",
        },
        'adv_history': {
            'ru': "Исторические приключения",
            'en': "Historical adventures",
        },
        'adv_indian': {
            'ru': "Приключения про индейцев",
            'en': "Adventures about Indians",
        },
        'adv_maritime': {
            'ru': "Морские приключения",
            'en': "Sea adventures",
        },
        'adv_geo': {
            'ru': "Путешествия и география",
            'en': "Travel and geography",
        },
        'adv_animal': {
            'ru': "Природа и животные",
            'en': "Nature and animals",
        },
        'adventure': {
            'ru': "Приключения",
            'en': "Adventure",
        },
        'child_tale': {
            'ru': "Сказка",
            'en': "fairy tale",
        },
        'child_verse': {
            'ru': "Детские стихи",
            'en': "Children's poems",
        },
        'child_prose': {
            'ru': "Детскиая проза",
            'en': "Children's prose",
        },
        'child_sf': {
            'ru': "Детская фантастика",
            'en': "Children's fiction",
        },
        'child_det': {
            'ru': "Детские остросюжетные",
            'en': "Children's action - packed",
        },
        'child_adv': {
            'ru': "Детские приключения",
            'en': "Children's adventures",
        },
        'child_education': {
            'ru': "Детская образовательная литература",
            'en': "Children's educational literature",
        },
        'children': {
            'ru': "Детская литература",
            'en': "children's literature",
        },
        'poetry': {
            'ru': "Поэзия",
            'en': "Poetry",
        },
        'dramaturgy': {
            'ru': "Драматургия",
            'en': "Dramaturgy",
        },
        'antique_ant': {
            'ru': "Античная литература",
            'en': "Ancient literature",
        },
        'antique_european': {
            'ru': "Европейская старинная литература",
            'en': "European ancient literature",
        },
        'antique_russian': {
            'ru': "Древнерусская литература",
            'en': "Ancient Russian literature",
        },
        'antique_east': {
            'ru': "Древневосточная литература",
            'en': "Ancient Eastern literature",
        },
        'antique_myths': {
            'ru': "Мифы. Легенды. Эпос",
            'en': "Myths. Legends. Epic",
        },
        'antique': {
            'ru': "Cтаринная литература",
            'en': "Ancient literature",
        },
        'sci_history': {
            'ru': "История",
            'en': "History",
        },
        'sci_psychology': {
            'ru': "Психология",
            'en': "Psychology",
        },
        'sci_culture': {
            'ru': "Культурология",
            'en': "Cultural studies",
        },
        'sci_religion': {
            'ru': "Религиоведение",
            'en': "Religious studies",
        },
        'sci_philosophy': {
            'ru': "Философия",
            'en': "Philosophy",
        },
        'sci_politics': {
            'ru': "Политика",
            'en': "Politics",
        },
        'sci_business': {
            'ru': "Деловая литература",
            'en': "Business literature",
        },
        'sci_juris': {
            'ru': "Юриспруденция",
            'en': "Jurisprudence",
        },
        'sci_linguistic': {
            'ru': "Языкознание",
            'en': "Linguistics",
        },
        'sci_medicine': {
            'ru': "Медицина",
            'en': "Medicine",
        },
        'sci_phys': {
            'ru': "Физика",
            'en': "Physics",
        },
        'sci_math': {
            'ru': "Математика",
            'en': "Math",
        },
        'sci_chem': {
            'ru': "Химия",
            'en': "Chemistry",
        },
        'sci_biology': {
            'ru': "Биология",
            'en': "Biology",
        },
        'sci_tech': {
            'ru': "Технические науки",
            'en': "Technical sciences",
        },
        'science': {
            'ru': "Научная литература",
            'en': "Scientific literature",
        },
        'comp_www': {
            'ru': "Интернет",
            'en': "Internet",
        },
        'comp_programming': {
            'ru': "Программирование",
            'en': "Programming",
        },
        'comp_hard': {
            'ru': "Компьютерное \"железо\" (аппаратное обеспечение)",
            'en': "Computer hardware (hardware)",
        },
        'comp_soft': {
            'ru': "Программы",
            'en': "Programs",
        },
        'comp_db': {
            'ru': "Базы данных",
            'en': "Databases",
        },
        'comp_osnet': {
            'ru': "ОС и Сети",
            'en': "OS and Networks",
        },
        'computers': {
            'ru': "Околокомпьтерная литература",
            'en': "Computer literature",
        },
        'ref_encyc': {
            'ru': "Энциклопедии",
            'en': "Encyclopedias",
        },
        'ref_dict': {
            'ru': "Словари",
            'en': "Dictionaries",
        },
        'ref_ref': {
            'ru': "Справочники",
            'en': "References",
        },
        'ref_guide': {
            'ru': "Руководства",
            'en': "Manuals",
        },
        'reference': {
            'ru': "Справочная литература",
            'en': "Reference literature",
        },
        'nonf_biography': {
            'ru': "Биографии и Мемуары",
            'en': "Biographies and Memoirs",
        },
        'nonf_publicism': {
            'ru': "Публицистика",
            'en': "Publicism",
        },
        'nonf_criticism': {
            'ru': "Публицистика",
            'en': "Cricitism",
        },
        'design': {
            'ru': "Искусство и Дизайн",
            'en': "Art and Design",
        },
        'nonfiction': {
            'ru': "Документальная литература ",
            'en': "Nonfiction",
        },
        'religion_rel': {
            'ru': "Религия",
            'en': "Religion",
        },
        'religion_esoterics': {
            'ru': "Эзотерика",
            'en': "Esotericism",
        },
        'religion_self': {
            'ru': "Самосовершенствование",
            'en': "Self-improvement",
        },
        'religion': {
            'ru': "Духовная литература",
            'en': "Spiritual literature",
        },
        'humor_anecdote': {
            'ru': "Анекдоты",
            'en': "funny stories",
        },
        'humor_prose': {
            'ru': "Юмористическая проза",
            'en': "Humorous prose",
        },
        'humor_verse': {
            'ru': "Юмористические стихи",
            'en': "Humorous poems",
        },
        'humor': {
            'ru': "Юмор",
            'en': "Humor",
        },
        'home_cooking': {
            'ru': "Кулинария",
            'en': "Cooking",
        },
        'home_pets': {
            'ru': "Домашние животные",
            'en': "Pets",
        },
        'home_crafts': {
            'ru': "Хобби и ремесла",
            'en': "Hobbies and crafts",
        },
        'home_entertain': {
            'ru': "Развлечения",
            'en': "Entertainments",
        },
        'home_health': {
            'ru': "Здоровье",
            'en': "Health",
        },
        'home_garden': {
            'ru': "Сад и огород",
            'en': "Garden and vegetable garden",
        },
        'home_diy': {
            'ru': "Сделай сам",
            'en': "Do it yourself",
        },
        'home_sport': {
            'ru': "Спорт",
            'en': "Sport",
        },
        'home_sex': {
            'ru': "Эротика, Секс",
            'en': "Erotica, Sex",
        },
        'home': {
            'ru': "Прочиее домоводство",
            'en': "Home economics",
        },
    }

    if genre in genres:
        return genres[genre][lang]
    return genre


def template(text, lang):
    if text == '':
        if lang == 'ru':
            return ''
        elif lang == 'en':
            return ''