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
        print('pyobjus not imported')

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
    return 'unknown type of message: ' + text

def lang_code_text(code):
    if code == 'ru': return 'Русский'
    if code == 'en': return 'English'
    return 'unknown code: ' + code

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



def template(text, lang):
    if text == '':
        if lang == 'ru':
            return ''
        elif lang == 'en':
            return ''