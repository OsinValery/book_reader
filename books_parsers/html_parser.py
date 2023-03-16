
from .html_Tag import Html_Tag
from .xml_parser import XmlParser
from typing import Tuple, Union

class Html_Parser(XmlParser):
    ignore_tags = ["style", 'strong', 'script']

    def is_self_closed(self, tag: str) -> bool:
        if tag == '': return False
        if 'meta' in tag[:5]: return True
        pos = -1
        while (tag[pos].isspace()) and (pos > -len(tag)):
            pos -= 1
        if pos == -len(tag): return False
        return tag[-1] == '/'
    
    def taste_another_seqs(self, text, pos) -> Union[None, Tuple[str, str]]:
        end = text.find(';', pos)
        if end == -1:
            return None
        code = text[pos+1:end]
        if code in unicodeSimbolsEscapes:
            return (code, unicodeSimbolsEscapes[code])
        return None

    def parce_string(self, string:str, pos:int) -> Tuple[Html_Tag, int]:
        root = Html_Tag()
        if string[pos] != '<':
            pos = self.find_simbols_outside_comments(['<'], string, pos)
        close = self.find_simbols_outside_comments(['>'], string, pos)
        tag_txt = string[pos+1:close]
        self_closed = self.is_self_closed(tag_txt)
        # divide tag and xml arguments here!!
        root.tag, root.attr = self.get_tag_arguments(tag_txt)

        if self_closed or root.tag == 'br':
            return root, close + 1
        pos = close + 1
        # ignore parsing content of tags with text content
        # this code only takes text with styles markup
        if root.tag in self.ignore_tags:
            close_tag_text = self.get_close_tag(root.tag)
            close_tag_pos = string.find(close_tag_text, pos)
            if close_tag_pos == -1:
                close_tag_pos = len(string)
            root.text = self.decode_unicode_simbols(string[pos:close_tag_pos])
            return root, close_tag_pos + len(close_tag_text)
        closed = False
        while (not closed) and (pos < len(string)):
            content_start = pos
            pos = self.find_simbols_outside_comments(['<'], string, content_start)
            if (pos >= len(string)): return root, pos
            plain_text = string[content_start:pos]
            if plain_text != '' and not plain_text.isspace():
                plain_tag = Html_Tag()
                plain_tag.tag = "plain_text"
                plain_text = self.remove_comments_from_string(plain_text)
                plain_tag.text = self.decode_unicode_simbols(plain_text).strip()
                root.append(plain_tag)
            # work '<'
            if pos + 1 == len(string):
                closed = True
            if string[pos+1] == '/':
                closed = True
                close_pos = self.find_simbols_outside_comments(['>'], string, pos+1)
                pos = max(close_pos + 1, pos + 1)
            
            if root.tag == 'li':
                if string[pos+1:pos+3] == 'li':
                    closed = True
            
            #it is internal tag
            if not closed:
                if self.is_comment_start(string, pos):
                    pos = self.find_comment_end_position(string, pos)
                else:
                    sub_tag, pos = self.parce_string(string, pos)
                    root.append(sub_tag)
        return root, pos


unicodeSimbolsEscapes = {'Tab': '\t', 'excl': '!', 'quot': '"', 'QUOT': '"', 'num': '#', 'dollar': '$', 'percnt': '%', 'rpar': ')', 'ast': '*', 'midast': '*', 'plus': '+', 'comma': ',', 'period': '.', 'sol': '/', 'colon': ':', 'semi': ';', 'lt': '<', 'LT': '<', 'equals': '=', 'gt': '>', 'GT': '>', 'quest': '?', 'commat': '@', 'lsqb': '[', 'lbrack': '[', 'bsol': '\\', 'rsqb': ']', 'rbrack': ']', 'Hat': '^', 'lowbar': '_', 'UnderBar': '_', 'grave': '`', 'DiacriticalGrave': '`', 'lcub': '{', 'lbrace': '{', 'verbar': '|', 'vert': '|', 'VerticalLine': '|', 'rcub': '}', 'rbrace': '}', 'nbsp': '\xa0', 'NonBreakingSpace': '\xa0', 'iexcl': '¡', 'cent': '¢', 'pound': '£', 'curren': '¤', 'yen': '¥', 'brvbar': '¦', 'sect': '§', 'Dot': '¨', 'die': '¨', 'DoubleDot': '¨', 'uml': '¨', 'copy': '©', 'COPY': '©', 'ordf': 'ª', 'laquo': '«', 'not': '¬', 'shy': '\xad', 'reg': '®', 'circledR': '®', 'REG': '®', 'macr': '¯', 'strns': '¯', 'deg': '°', 'plusmn': '±', 'pm': '±', 'PlusMinus': '±', 'sup2': '²', 'sup3': '³', 'acute': '´', 'DiacriticalAcute': '´', 'micro': 'µ', 'para': '¶', 'middot': '·', 'centerdot': '·', 'CenterDot': '·', 'cedil': '¸', 'Cedilla': '¸', 'sup1': '¹', 'ordm': 'º', 'raquo': '»', 'frac14': '¼', 'frac12': '½', 'half': '½', 'frac34': '¾', 'iquest': '¿', 'Agrave': 'À', 'Aacute': 'Á', 'Acirc': 'Â', 'Atilde': 'Ã', 'Auml': 'Ä', 'Aring': 'Å', 'angst': 'Å', 'AElig': 'Æ', 'Ccedil': 'Ç', 'Egrave': 'È', 'Eacute': 'É', 'Ecirc': 'Ê', 'Euml': 'Ë', 'Igrave': 'Ì', 'Iacute': 'Í', 'Icirc': 'Î', 'Iuml': 'Ï', 'ETH': 'Ð', 'Ntilde': 'Ñ', 'Ograve': 'Ò', 'Oacute': 'Ó', 'Ocirc': 'Ô', 'Otilde': 'Õ', 'Ouml': 'Ö', 'times': '×', 'Oslash': 'Ø', 'Ugrave': 'Ù', 'Uacute': 'Ú', 'Ucirc': 'Û', 'Uuml': 'Ü', 'Yacute': 'Ý', 'THORN': 'Þ', 'szlig': 'ß', 'agrave': 'à', 'aacute': 'á', 'acirc': 'â', 'atilde': 'ã', 'auml': 'ä', 'aring': 'å', 'aelig': 'æ', 'ccedil': 'ç', 'egrave': 'è', 'eacute': 'é', 'ecirc': 'ê', 'euml': 'ë', 'igrave': 'ì', 'iacute': 'í', 'icirc': 'î', 'iuml': 'ï', 'eth': 'ð', 'ntilde': 'ñ', 'ograve': 'ò', 'oacute': 'ó', 'ocirc': 'ô', 'otilde': 'õ', 'ouml': 'ö', 'divide': '÷', 'div': '÷', 'oslash': 'ø', 'ugrave': 'ù', 'uacute': 'ú', 'ucirc': 'û', 'uuml': 'ü', 'yacute': 'ý', 'thorn': 'þ', 'yuml': 'ÿ', 'Amacr': 'Ā', 'amacr': 'ā', 'Abreve': 'Ă', 'abreve': 'ă', 'Aogon': 'Ą', 'aogon': 'ą', 'Cacute': 'Ć', 'cacute': 'ć', 'Ccirc': 'Ĉ', 'ccirc': 'ĉ', 'Cdot': 'Ċ', 'cdot': 'ċ', 'Ccaron': 'Č', 'ccaron': 'č', 'Dcaron': 'Ď', 'dcaron': 'ď', 'Dstrok': 'Đ', 'dstrok': 'đ', 'Emacr': 'Ē', 'emacr': 'ē', 'Edot': 'Ė', 'edot': 'ė', 'Eogon': 'Ę', 'eogon': 'ę', 'Ecaron': 'Ě', 'ecaron': 'ě', 'Gcirc': 'Ĝ', 'gcirc': 'ĝ', 'Gbreve': 'Ğ', 'gbreve': 'ğ', 'Gdot': 'Ġ', 'gdot': 'ġ', 'Gcedil': 'Ģ', 'Hcirc': 'Ĥ', 'hcirc': 'ĥ', 'Hstrok': 'Ħ', 'hstrok': 'ħ', 'Itilde': 'Ĩ', 'itilde': 'ĩ', 'Imacr': 'Ī', 'imacr': 'ī', 'Iogon': 'Į', 'iogon': 'į', 'Idot': 'İ', 'imath': 'ı', 'inodot': 'ı', 'IJlig': 'Ĳ', 'ijlig': 'ĳ', 'Jcirc': 'Ĵ', 'jcirc': 'ĵ', 'Kcedil': 'Ķ', 'kcedil': 'ķ', 'kgreen': 'ĸ', 'Lacute': 'Ĺ', 'lacute': 'ĺ', 'Lcedil': 'Ļ', 'lcedil': 'ļ', 'Lcaron': 'Ľ', 'lcaron': 'ľ', 'Lmidot': 'Ŀ', 'lmidot': 'ŀ', 'Lstrok': 'Ł', 'lstrok': 'ł', 'Nacute': 'Ń', 'nacute': 'ń', 'Ncedil': 'Ņ', 'ncedil': 'ņ', 'Ncaron': 'Ň', 'ncaron': 'ň', 'napos': 'ŉ', 'ENG': 'Ŋ', 'eng': 'ŋ', 'Omacr': 'Ō', 'omacr': 'ō', 'Odblac': 'Ő', 'odblac': 'ő', 'OElig': 'Œ', 'oelig': 'œ', 'Racute': 'Ŕ', 'racute': 'ŕ', 'Rcedil': 'Ŗ', 'rcedil': 'ŗ', 'Rcaron': 'Ř', 'rcaron': 'ř', 'Sacute': 'Ś', 'sacute': 'ś', 'Scirc': 'Ŝ', 'scirc': 'ŝ', 'Scedil': 'Ş', 'scedil': 'ş', 'Scaron': 'Š', 'scaron': 'š', 'Tcedil': 'Ţ', 'tcedil': 'ţ', 'Tcaron': 'Ť', 'tcaron': 'ť', 'Tstrok': 'Ŧ', 'tstrok': 'ŧ', 'Utilde': 'Ũ', 'utilde': 'ũ', 'Umacr': 'Ū', 'umacr': 'ū', 'Ubreve': 'Ŭ', 'ubreve': 'ŭ', 'Uring': 'Ů', 'uring': 'ů', 'Udblac': 'Ű', 'udblac': 'ű', 'Uogon': 'Ų', 'uogon': 'ų', 'Wcirc': 'Ŵ', 'wcirc': 'ŵ', 'Ycirc': 'Ŷ', 'ycirc': 'ŷ', 'Yuml': 'Ÿ', 'Zacute': 'Ź', 'zacute': 'ź', 'Zdot': 'Ż', 'zdot': 'ż', 'Zcaron': 'Ž', 'zcaron': 'ž', 'fnof': 'ƒ', 'imped': 'Ƶ', 'gacute': 'ǵ', 'jmath': 'ȷ', 'circ': 'ˆ', 'caron': 'ˇ', 'Hacek': 'ˇ', 'breve': '˘', 'Breve': '˘', 'dot': '˙', 'DiacriticalDot': '˙', 'ring': '˚', 'ogon': '˛', 'tilde': '˜', 'DiacriticalTilde': '˜', 'dblac': '˝', 'DiacriticalDoubleAcute': '˝', 'DownBreve': '̑', 'Alpha': 'Α', 'Beta': 'Β', 'Gamma': 'Γ', 'Delta': 'Δ', 'Epsilon': 'Ε', 'Zeta': 'Ζ', 'Eta': 'Η', 'Theta': 'Θ', 'Iota': 'Ι', 'Kappa': 'Κ', 'Lambda': 'Λ', 'Mu': 'Μ', 'Nu': 'Ν', 'Xi': 'Ξ', 'Omicron': 'Ο', 'Pi': 'Π', 'Rho': 'Ρ', 'Sigma': 'Σ', 'Tau': 'Τ', 'Upsilon': 'Υ', 'Phi': 'Φ', 'Chi': 'Χ', 'Psi': 'Ψ', 'Omega': 'Ω', 'ohm': 'Ω', 'alpha': 'α', 'beta': 'β', 'gamma': 'γ', 'delta': 'δ', 'epsi': 'ε', 'epsilon': 'ε', 'zeta': 'ζ', 'eta': 'η', 'theta': 'θ', 'iota': 'ι', 'kappa': 'κ', 'lambda': 'λ', 'mu': 'μ', 'nu': 'ν', 'xi': 'ξ', 'omicron': 'ο', 'pi': 'π', 'rho': 'ρ', 'sigmav': 'ς', 'varsigma': 'ς', 'sigmaf': 'ς', 'sigma': 'σ', 'tau': 'τ', 'upsi': 'υ', 'upsilon': 'υ', 'phi': 'φ', 'chi': 'χ', 'psi': 'ψ', 'omega': 'ω', 'thetav': 'ϑ', 'vartheta': 'ϑ', 'thetasym': 'ϑ', 'Upsi': 'ϒ', 'upsih': 'ϒ', 'straightphi': 'ϕ', 'phiv': 'ϕ', 'varphi': 'ϕ', 'piv': 'ϖ', 'varpi': 'ϖ', 'Gammad': 'Ϝ', 'gammad': 'ϝ', 'digamma': 'ϝ', 'kappav': 'ϰ', 'varkappa': 'ϰ', 'rhov': 'ϱ', 'varrho': 'ϱ', 'epsiv': 'ϵ', 'varepsilon': 'ϵ', 'straightepsilon': 'ϵ', 'bepsi': '϶', 'backepsilon': '϶', 'IOcy': 'Ё', 'DJcy': 'Ђ', 'GJcy': 'Ѓ', 'Jukcy': 'Є', 'DScy': 'Ѕ', 'Iukcy': 'І', 'YIcy': 'Ї', 'Jsercy': 'Ј', 'LJcy': 'Љ', 'NJcy': 'Њ', 'TSHcy': 'Ћ', 'KJcy': 'Ќ', 'Ubrcy': 'Ў', 'DZcy': 'Џ', 'Acy': 'А', 'Bcy': 'Б', 'Vcy': 'В', 'Gcy': 'Г', 'Dcy': 'Д', 'IEcy': 'Е', 'ZHcy': 'Ж', 'Zcy': 'З', 'Icy': 'И', 'Jcy': 'Й', 'Kcy': 'К', 'Lcy': 'Л', 'Mcy': 'М', 'Ncy': 'Н', 'Ocy': 'О', 'Pcy': 'П', 'Rcy': 'Р', 'Scy': 'С', 'Tcy': 'Т', 'Ucy': 'У', 'Fcy': 'Ф', 'KHcy': 'Х', 'TScy': 'Ц', 'CHcy': 'Ч', 'SHcy': 'Ш', 'SHCHcy': 'Щ', 'HARDcy': 'Ъ', 'Ycy': 'Ы', 'SOFTcy': 'Ь', 'Ecy': 'Э', 'YUcy': 'Ю', 'YAcy': 'Я', 'acy': 'а', 'bcy': 'б', 'vcy': 'в', 'gcy': 'г', 'dcy': 'д', 'iecy': 'е', 'zhcy': 'ж', 'zcy': 'з', 'icy': 'и', 'jcy': 'й', 'kcy': 'к', 'lcy': 'л', 'mcy': 'м', 'ncy': 'н', 'ocy': 'о', 'pcy': 'п', 'rcy': 'р', 'scy': 'с', 'tcy': 'т', 'ucy': 'у', 'fcy': 'ф', 'khcy': 'х', 'tscy': 'ц', 'chcy': 'ч', 'shcy': 'ш', 'shchcy': 'щ', 'hardcy': 'ъ', 'ycy': 'ы', 'softcy': 'ь', 'ecy': 'э', 'yucy': 'ю', 'yacy': 'я', 'iocy': 'ё', 'djcy': 'ђ', 'gjcy': 'ѓ', 'jukcy': 'є', 'dscy': 'ѕ', 'iukcy': 'і', 'yicy': 'ї', 'jsercy': 'ј', 'ljcy': 'љ', 'njcy': 'њ', 'tshcy': 'ћ', 'kjcy': 'ќ', 'ubrcy': 'ў', 'dzcy': 'џ', 'ensp': '\u2002', 'emsp': '\u2003', 'emsp13': '\u2004', 'emsp14': '\u2005', 'numsp': '\u2007', 'puncsp': '\u2008', 'thinsp': '\u2009', 'ThinSpace': '\u2009', 'hairsp': '\u200a', 'VeryThinSpace': '\u200a', 'ZeroWidthSpace': '\u200b', 'NegativeVeryThinSpace': '\u200b', 'NegativeThinSpace': '\u200b', 'NegativeMediumSpace': '\u200b', 'NegativeThickSpace': '\u200b', 'zwnj': '\u200c', 'zwj': '\u200d', 'lrm': '\u200e', 'rlm': '\u200f', 'hyphen': '‐', 'dash': '‐', 'ndash': '–', 'mdash': '—', 'horbar': '―', 'Verbar': '‖', 'Vert': '‖', 'lsquo': '‘', 'OpenCurlyQuote': '‘', 'rsquo': '’', 'rsquor': '’', 'CloseCurlyQuote': '’', 'sbquo': '‚', 'lsquor': '‚', 'ldquo': '“', 'OpenCurlyDoubleQuote': '“', 'rdquo': '”', 'rdquor': '”', 'CloseCurlyDoubleQuote': '”', 'bdquo': '„', 'ldquor': '„', 'dagger': '†', 'Dagger': '‡', 'ddagger': '‡', 'bull': '•', 'bullet': '•', 'nldr': '‥', 'hellip': '…', 'mldr': '…', 'permil': '‰', 'pertenk': '‱', 'prime': '′', 'Prime': '″', 'tprime': '‴', 'bprime': '‵', 'backprime': '‵', 'lsaquo': '‹', 'rsaquo': '›', 'oline': '‾', 'OverBar': '‾', 'caret': '⁁', 'hybull': '⁃', 'frasl': '⁄', 'bsemi': '⁏', 'qprime': '⁗', 'MediumSpace': '\u205f', 'NoBreak': '\u2060', 'ApplyFunction': '\u2061', 'af': '\u2061', 'InvisibleTimes': '\u2062', 'it': '\u2062', 'InvisibleComma': '\u2063', 'ic': '\u2063', 'euro': '€', 'tdot': '⃛', 'TripleDot': '⃛', 'DotDot': '⃜', 'Copf': 'ℂ', 'complexes': 'ℂ', 'incare': '℅', 'gscr': 'ℊ', 'hamilt': 'ℋ', 'HilbertSpace': 'ℋ', 'Hscr': 'ℋ', 'Hfr': 'ℌ', 'Poincareplane': 'ℌ', 'quaternions': 'ℍ', 'Hopf': 'ℍ', 'planckh': 'ℎ', 'planck': 'ℏ', 'hbar': 'ℏ', 'plankv': 'ℏ', 'hslash': 'ℏ', 'Iscr': 'ℐ', 'imagline': 'ℐ', 'image': 'ℑ', 'Im': 'ℑ', 'imagpart': 'ℑ', 'Ifr': 'ℑ', 'Lscr': 'ℒ', 'lagran': 'ℒ', 'Laplacetrf': 'ℒ', 'ell': 'ℓ', 'Nopf': 'ℕ', 'naturals': 'ℕ', 'numero': '№', 'copysr': '℗', 'weierp': '℘', 'wp': '℘', 'Popf': 'ℙ', 'primes': 'ℙ', 'rationals': 'ℚ', 'Qopf': 'ℚ', 'Rscr': 'ℛ', 'realine': 'ℛ', 'real': 'ℜ', 'Re': 'ℜ', 'realpart': 'ℜ', 'Rfr': 'ℜ', 'reals': 'ℝ', 'Ropf': 'ℝ', 'rx': '℞', 'trade': '™', 'TRADE': '™', 'integers': 'ℤ', 'Zopf': 'ℤ', 'mho': '℧', 'Zfr': 'ℨ', 'zeetrf': 'ℨ', 'iiota': '℩', 'bernou': 'ℬ', 'Bernoullis': 'ℬ', 'Bscr': 'ℬ', 'Cfr': 'ℭ', 'Cayleys': 'ℭ', 'escr': 'ℯ', 'Escr': 'ℰ', 'expectation': 'ℰ', 'Fscr': 'ℱ', 'Fouriertrf': 'ℱ', 'phmmat': 'ℳ', 'Mellintrf': 'ℳ', 'Mscr': 'ℳ', 'order': 'ℴ', 'orderof': 'ℴ', 'oscr': 'ℴ', 'alefsym': 'ℵ', 'aleph': 'ℵ', 'beth': 'ℶ', 'gimel': 'ℷ', 'daleth': 'ℸ', 'CapitalDifferentialD': 'ⅅ', 'DD': 'ⅅ', 'DifferentialD': 'ⅆ', 'dd': 'ⅆ', 'ExponentialE': 'ⅇ', 'exponentiale': 'ⅇ', 'ee': 'ⅇ', 'ImaginaryI': 'ⅈ', 'ii': 'ⅈ', 'frac13': '⅓', 'frac23': '⅔', 'frac15': '⅕', 'frac25': '⅖', 'frac35': '⅗', 'frac45': '⅘', 'frac16': '⅙', 'frac56': '⅚', 'frac18': '⅛', 'frac38': '⅜', 'frac58': '⅝', 'frac78': '⅞', 'larr': '←', 'leftarrow': '←', 'LeftArrow': '←', 'slarr': '←', 'ShortLeftArrow': '←', 'uarr': '↑', 'uparrow': '↑', 'UpArrow': '↑', 'ShortUpArrow': '↑', 'rarr': '→', 'rightarrow': '→', 'RightArrow': '→', 'srarr': '→', 'ShortRightArrow': '→', 'darr': '↓', 'downarrow': '↓', 'DownArrow': '↓', 'ShortDownArrow': '↓', 'harr': '↔', 'leftrightarrow': '↔', 'LeftRightArrow': '↔', 'varr': '↕', 'updownarrow': '↕', 'UpDownArrow': '↕', 'nwarr': '↖', 'UpperLeftArrow': '↖', 'nwarrow': '↖', 'nearr': '↗', 'UpperRightArrow': '↗', 'nearrow': '↗', 'searr': '↘', 'searrow': '↘', 'LowerRightArrow': '↘', 'swarr': '↙', 'swarrow': '↙', 'LowerLeftArrow': '↙', 'nlarr': '↚', 'nleftarrow': '↚', 'nrarr': '↛', 'nrightarrow': '↛', 'rarrw': '↝', 'rightsquigarrow': '↝', 'Larr': '↞', 'twoheadleftarrow': '↞', 'Uarr': '↟', 'Rarr': '↠', 'twoheadrightarrow': '↠', 'Darr': '↡', 'larrtl': '↢', 'leftarrowtail': '↢', 'rarrtl': '↣', 'rightarrowtail': '↣', 'LeftTeeArrow': '↤', 'mapstoleft': '↤', 'UpTeeArrow': '↥', 'mapstoup': '↥', 'map': '↦', 'RightTeeArrow': '↦', 'mapsto': '↦', 'DownTeeArrow': '↧', 'mapstodown': '↧', 'larrhk': '↩', 'hookleftarrow': '↩', 'rarrhk': '↪', 'hookrightarrow': '↪', 'larrlp': '↫', 'looparrowleft': '↫', 'rarrlp': '↬', 'looparrowright': '↬', 'harrw': '↭', 'leftrightsquigarrow': '↭', 'nharr': '↮', 'nleftrightarrow': '↮', 'lsh': '↰', 'Lsh': '↰', 'rsh': '↱', 'Rsh': '↱', 'ldsh': '↲', 'rdsh': '↳', 'crarr': '↵', 'cularr': '↶', 'curvearrowleft': '↶', 'curarr': '↷', 'curvearrowright': '↷', 'olarr': '↺', 'circlearrowleft': '↺', 'orarr': '↻', 'circlearrowright': '↻', 'lharu': '↼', 'LeftVector': '↼', 'leftharpoonup': '↼', 'lhard': '↽', 'leftharpoondown': '↽', 'DownLeftVector': '↽', 'uharr': '↾', 'upharpoonright': '↾', 'RightUpVector': '↾', 'uharl': '↿', 'upharpoonleft': '↿', 'LeftUpVector': '↿', 'rharu': '⇀', 'RightVector': '⇀', 'rightharpoonup': '⇀', 'rhard': '⇁', 'rightharpoondown': '⇁', 'DownRightVector': '⇁', 'dharr': '⇂', 'RightDownVector': '⇂', 'downharpoonright': '⇂', 'dharl': '⇃', 'LeftDownVector': '⇃', 'downharpoonleft': '⇃', 'rlarr': '⇄', 'rightleftarrows': '⇄', 'RightArrowLeftArrow': '⇄', 'udarr': '⇅', 'UpArrowDownArrow': '⇅', 'lrarr': '⇆', 'leftrightarrows': '⇆', 'LeftArrowRightArrow': '⇆', 'llarr': '⇇', 'leftleftarrows': '⇇', 'uuarr': '⇈', 'upuparrows': '⇈', 'rrarr': '⇉', 'rightrightarrows': '⇉', 'ddarr': '⇊', 'downdownarrows': '⇊', 'lrhar': '⇋', 'ReverseEquilibrium': '⇋', 'leftrightharpoons': '⇋', 'rlhar': '⇌', 'rightleftharpoons': '⇌', 'Equilibrium': '⇌', 'nlArr': '⇍', 'nLeftarrow': '⇍', 'nhArr': '⇎', 'nLeftrightarrow': '⇎', 'nrArr': '⇏', 'nRightarrow': '⇏', 'lArr': '⇐', 'Leftarrow': '⇐', 'DoubleLeftArrow': '⇐', 'uArr': '⇑', 'Uparrow': '⇑', 'DoubleUpArrow': '⇑', 'rArr': '⇒', 'Rightarrow': '⇒', 'Implies': '⇒', 'DoubleRightArrow': '⇒', 'dArr': '⇓', 'Downarrow': '⇓', 'DoubleDownArrow': '⇓', 'hArr': '⇔', 'Leftrightarrow': '⇔', 'DoubleLeftRightArrow': '⇔', 'iff': '⇔', 'vArr': '⇕', 'Updownarrow': '⇕', 'DoubleUpDownArrow': '⇕', 'nwArr': '⇖', 'neArr': '⇗', 'seArr': '⇘', 'swArr': '⇙', 'lAarr': '⇚', 'Lleftarrow': '⇚', 'rAarr': '⇛', 'Rrightarrow': '⇛', 'zigrarr': '⇝', 'larrb': '⇤', 'LeftArrowBar': '⇤', 'rarrb': '⇥', 'RightArrowBar': '⇥', 'duarr': '⇵', 'DownArrowUpArrow': '⇵', 'loarr': '⇽', 'roarr': '⇾', 'hoarr': '⇿', 'forall': '∀', 'ForAll': '∀', 'comp': '∁', 'complement': '∁', 'part': '∂', 'PartialD': '∂', 'exist': '∃', 'Exists': '∃', 'nexist': '∄', 'NotExists': '∄', 'nexists': '∄', 'empty': '∅', 'emptyset': '∅', 'emptyv': '∅', 'varnothing': '∅', 'nabla': '∇', 'Del': '∇', 'isin': '∈', 'isinv': '∈', 'Element': '∈', 'in': '∈', 'notin': '∉', 'NotElement': '∉', 'notinva': '∉', 'niv': '∋', 'ReverseElement': '∋', 'ni': '∋', 'SuchThat': '∋', 'notni': '∌', 'notniva': '∌', 'NotReverseElement': '∌', 'prod': '∏', 'Product': '∏', 'coprod': '∐', 'Coproduct': '∐', 'sum': '∑', 'Sum': '∑', 'minus': '−', 'mnplus': '∓', 'mp': '∓', 'MinusPlus': '∓', 'plusdo': '∔', 'dotplus': '∔', 'setmn': '∖', 'setminus': '∖', 'Backslash': '∖', 'ssetmn': '∖', 'smallsetminus': '∖', 'lowast': '∗', 'compfn': '∘', 'SmallCircle': '∘', 'radic': '√', 'Sqrt': '√', 'prop': '∝', 'propto': '∝', 'Proportional': '∝', 'vprop': '∝', 'varpropto': '∝', 'infin': '∞', 'angrt': '∟', 'ang': '∠', 'angle': '∠', 'angmsd': '∡', 'measuredangle': '∡', 'angsph': '∢', 'mid': '∣', 'VerticalBar': '∣', 'smid': '∣', 'shortmid': '∣', 'nmid': '∤', 'NotVerticalBar': '∤', 'nsmid': '∤', 'nshortmid': '∤', 'par': '∥', 'parallel': '∥', 'DoubleVerticalBar': '∥', 'spar': '∥', 'shortparallel': '∥', 'npar': '∦', 'nparallel': '∦', 'NotDoubleVerticalBar': '∦', 'nspar': '∦', 'nshortparallel': '∦', 'and': '∧', 'wedge': '∧', 'or': '∨', 'vee': '∨', 'cap': '∩', 'cup': '∪', 'int': '∫', 'Integral': '∫', 'Int': '∬', 'tint': '∭', 'iiint': '∭', 'conint': '∮', 'oint': '∮', 'ContourIntegral': '∮', 'Conint': '∯', 'DoubleContourIntegral': '∯', 'Cconint': '∰', 'cwint': '∱', 'cwconint': '∲', 'ClockwiseContourIntegral': '∲', 'awconint': '∳', 'CounterClockwiseContourIntegral': '∳', 'there4': '∴', 'therefore': '∴', 'Therefore': '∴', 'becaus': '∵', 'because': '∵', 'Because': '∵', 'ratio': '∶', 'Colon': '∷', 'Proportion': '∷', 'minusd': '∸', 'dotminus': '∸', 'mDDot': '∺', 'homtht': '∻', 'sim': '∼', 'Tilde': '∼', 'thksim': '∼', 'thicksim': '∼', 'bsim': '∽', 'backsim': '∽', 'ac': '∾', 'mstpos': '∾', 'acd': '∿', 'wreath': '≀', 'VerticalTilde': '≀', 'wr': '≀', 'nsim': '≁', 'NotTilde': '≁', 'esim': '≂', 'EqualTilde': '≂', 'eqsim': '≂', 'sime': '≃', 'TildeEqual': '≃', 'simeq': '≃', 'nsime': '≄', 'nsimeq': '≄', 'NotTildeEqual': '≄', 'cong': '≅', 'TildeFullEqual': '≅', 'simne': '≆', 'ncong': '≇', 'NotTildeFullEqual': '≇', 'asymp': '≈', 'ap': '≈', 'TildeTilde': '≈', 'approx': '≈', 'thkap': '≈', 'thickapprox': '≈', 'nap': '≉', 'NotTildeTilde': '≉', 'napprox': '≉', 'ape': '≊', 'approxeq': '≊', 'apid': '≋', 'bcong': '≌', 'backcong': '≌', 'asympeq': '≍', 'CupCap': '≍', 'bump': '≎', 'HumpDownHump': '≎', 'Bumpeq': '≎', 'bumpe': '≏', 'HumpEqual': '≏', 'bumpeq': '≏', 'esdot': '≐', 'DotEqual': '≐', 'doteq': '≐', 'eDot': '≑', 'doteqdot': '≑', 'efDot': '≒', 'fallingdotseq': '≒', 'erDot': '≓', 'risingdotseq': '≓', 'colone': '≔', 'coloneq': '≔', 'Assign': '≔', 'ecolon': '≕', 'eqcolon': '≕', 'ecir': '≖', 'eqcirc': '≖', 'cire': '≗', 'circeq': '≗', 'wedgeq': '≙', 'veeeq': '≚', 'trie': '≜', 'triangleq': '≜', 'equest': '≟', 'questeq': '≟', 'ne': '≠', 'NotEqual': '≠', 'equiv': '≡', 'Congruent': '≡', 'nequiv': '≢', 'NotCongruent': '≢', 'le': '≤', 'leq': '≤', 'ge': '≥', 'GreaterEqual': '≥', 'geq': '≥', 'lE': '≦', 'LessFullEqual': '≦', 'leqq': '≦', 'gE': '≧', 'GreaterFullEqual': '≧', 'geqq': '≧', 'lnE': '≨', 'lneqq': '≨', 'gnE': '≩', 'gneqq': '≩', 'Lt': '≪', 'NestedLessLess': '≪', 'll': '≪', 'Gt': '≫', 'NestedGreaterGreater': '≫', 'gg': '≫', 'twixt': '≬', 'between': '≬', 'NotCupCap': '≭', 'nlt': '≮', 'NotLess': '≮', 'nless': '≮', 'ngt': '≯', 'NotGreater': '≯', 'ngtr': '≯', 'nle': '≰', 'NotLessEqual': '≰', 'nleq': '≰', 'nge': '≱', 'NotGreaterEqual': '≱', 'ngeq': '≱', 'lsim': '≲', 'LessTilde': '≲', 'lesssim': '≲', 'gsim': '≳', 'gtrsim': '≳', 'GreaterTilde': '≳', 'nlsim': '≴', 'NotLessTilde': '≴', 'ngsim': '≵', 'NotGreaterTilde': '≵', 'lg': '≶', 'lessgtr': '≶', 'LessGreater': '≶', 'gl': '≷', 'gtrless': '≷', 'GreaterLess': '≷', 'ntlg': '≸', 'NotLessGreater': '≸', 'ntgl': '≹', 'NotGreaterLess': '≹', 'pr': '≺', 'Precedes': '≺', 'prec': '≺', 'sc': '≻', 'Succeeds': '≻', 'succ': '≻', 'prcue': '≼', 'PrecedesSlantEqual': '≼', 'preccurlyeq': '≼', 'sccue': '≽', 'SucceedsSlantEqual': '≽', 'succcurlyeq': '≽', 'prsim': '≾', 'precsim': '≾', 'PrecedesTilde': '≾', 'scsim': '≿', 'succsim': '≿', 'SucceedsTilde': '≿', 'npr': '⊀', 'nprec': '⊀', 'NotPrecedes': '⊀', 'nsc': '⊁', 'nsucc': '⊁', 'NotSucceeds': '⊁', 'sub': '⊂', 'subset': '⊂', 'sup': '⊃', 'supset': '⊃', 'Superset': '⊃', 'nsub': '⊄', 'nsup': '⊅', 'sube': '⊆', 'SubsetEqual': '⊆', 'subseteq': '⊆', 'supe': '⊇', 'supseteq': '⊇', 'SupersetEqual': '⊇', 'nsube': '⊈', 'nsubseteq': '⊈', 'NotSubsetEqual': '⊈', 'nsupe': '⊉', 'nsupseteq': '⊉', 'NotSupersetEqual': '⊉', 'subne': '⊊', 'subsetneq': '⊊', 'supne': '⊋', 'supsetneq': '⊋', 'cupdot': '⊍', 'uplus': '⊎', 'UnionPlus': '⊎', 'sqsub': '⊏', 'SquareSubset': '⊏', 'sqsubset': '⊏', 'sqsup': '⊐', 'SquareSuperset': '⊐', 'sqsupset': '⊐', 'sqsube': '⊑', 'SquareSubsetEqual': '⊑', 'sqsubseteq': '⊑', 'sqsupe': '⊒', 'SquareSupersetEqual': '⊒', 'sqsupseteq': '⊒', 'sqcap': '⊓', 'SquareIntersection': '⊓', 'sqcup': '⊔', 'SquareUnion': '⊔', 'oplus': '⊕', 'CirclePlus': '⊕', 'ominus': '⊖', 'CircleMinus': '⊖', 'otimes': '⊗', 'CircleTimes': '⊗', 'osol': '⊘', 'odot': '⊙', 'CircleDot': '⊙', 'ocir': '⊚', 'circledcirc': '⊚', 'oast': '⊛', 'circledast': '⊛', 'odash': '⊝', 'circleddash': '⊝', 'plusb': '⊞', 'boxplus': '⊞', 'minusb': '⊟', 'boxminus': '⊟', 'timesb': '⊠', 'boxtimes': '⊠', 'sdotb': '⊡', 'dotsquare': '⊡', 'vdash': '⊢', 'RightTee': '⊢', 'dashv': '⊣', 'LeftTee': '⊣', 'top': '⊤', 'DownTee': '⊤', 'bottom': '⊥', 'bot': '⊥', 'perp': '⊥', 'UpTee': '⊥', 'models': '⊧', 'vDash': '⊨', 'DoubleRightTee': '⊨', 'Vdash': '⊩', 'Vvdash': '⊪', 'VDash': '⊫', 'nvdash': '⊬', 'nvDash': '⊭', 'nVdash': '⊮', 'nVDash': '⊯', 'prurel': '⊰', 'vltri': '⊲', 'vartriangleleft': '⊲', 'LeftTriangle': '⊲', 'vrtri': '⊳', 'vartriangleright': '⊳', 'RightTriangle': '⊳', 'ltrie': '⊴', 'trianglelefteq': '⊴', 'LeftTriangleEqual': '⊴', 'rtrie': '⊵', 'trianglerighteq': '⊵', 'RightTriangleEqual': '⊵', 'origof': '⊶', 'imof': '⊷', 'mumap': '⊸', 'multimap': '⊸', 'hercon': '⊹', 'intcal': '⊺', 'intercal': '⊺', 'veebar': '⊻', 'barvee': '⊽', 'angrtvb': '⊾', 'lrtri': '⊿', 'xwedge': '⋀', 'Wedge': '⋀', 'bigwedge': '⋀', 'xvee': '⋁', 'Vee': '⋁', 'bigvee': '⋁', 'xcap': '⋂', 'Intersection': '⋂', 'bigcap': '⋂', 'xcup': '⋃', 'Union': '⋃', 'bigcup': '⋃', 'diam': '⋄', 'diamond': '⋄', 'Diamond': '⋄', 'sdot': '⋅', 'sstarf': '⋆', 'Star': '⋆', 'divonx': '⋇', 'divideontimes': '⋇', 'bowtie': '⋈', 'ltimes': '⋉', 'rtimes': '⋊', 'lthree': '⋋', 'leftthreetimes': '⋋', 'rthree': '⋌', 'rightthreetimes': '⋌', 'bsime': '⋍', 'backsimeq': '⋍', 'cuvee': '⋎', 'curlyvee': '⋎', 'cuwed': '⋏', 'curlywedge': '⋏', 'Sub': '⋐', 'Subset': '⋐', 'Sup': '⋑', 'Supset': '⋑', 'Cap': '⋒', 'Cup': '⋓', 'fork': '⋔', 'pitchfork': '⋔', 'epar': '⋕', 'ltdot': '⋖', 'lessdot': '⋖', 'gtdot': '⋗', 'gtrdot': '⋗', 'Ll': '⋘', 'Gg': '⋙', 'ggg': '⋙', 'leg': '⋚', 'LessEqualGreater': '⋚', 'lesseqgtr': '⋚', 'gel': '⋛', 'gtreqless': '⋛', 'GreaterEqualLess': '⋛', 'cuepr': '⋞', 'curlyeqprec': '⋞', 'cuesc': '⋟', 'curlyeqsucc': '⋟', 'nprcue': '⋠', 'NotPrecedesSlantEqual': '⋠', 'nsccue': '⋡', 'NotSucceedsSlantEqual': '⋡', 'nsqsube': '⋢', 'NotSquareSubsetEqual': '⋢', 'nsqsupe': '⋣', 'NotSquareSupersetEqual': '⋣', 'lnsim': '⋦', 'gnsim': '⋧', 'prnsim': '⋨', 'precnsim': '⋨', 'scnsim': '⋩', 'succnsim': '⋩', 'nltri': '⋪', 'ntriangleleft': '⋪', 'NotLeftTriangle': '⋪', 'nrtri': '⋫', 'ntriangleright': '⋫', 'NotRightTriangle': '⋫', 'nltrie': '⋬', 'ntrianglelefteq': '⋬', 'NotLeftTriangleEqual': '⋬', 'nrtrie': '⋭', 'ntrianglerighteq': '⋭', 'NotRightTriangleEqual': '⋭', 'vellip': '⋮', 'ctdot': '⋯', 'utdot': '⋰', 'dtdot': '⋱', 'disin': '⋲', 'isinsv': '⋳', 'isins': '⋴', 'isindot': '⋵', 'notinvc': '⋶', 'notinvb': '⋷', 'isinE': '⋹', 'nisd': '⋺', 'xnis': '⋻', 'nis': '⋼', 'notnivc': '⋽', 'notnivb': '⋾', 'barwed': '⌅', 'barwedge': '⌅', 'Barwed': '⌆', 'doublebarwedge': '⌆', 'lceil': '⌈', 'LeftCeiling': '⌈', 'rceil': '⌉', 'RightCeiling': '⌉', 'lfloor': '⌊', 'LeftFloor': '⌊', 'rfloor': '⌋', 'RightFloor': '⌋', 'drcrop': '⌌', 'dlcrop': '⌍', 'urcrop': '⌎', 'ulcrop': '⌏', 'bnot': '⌐', 'profline': '⌒', 'profsurf': '⌓', 'telrec': '⌕', 'target': '⌖', 'ulcorn': '⌜', 'ulcorner': '⌜', 'urcorn': '⌝', 'urcorner': '⌝', 'dlcorn': '⌞', 'llcorner': '⌞', 'drcorn': '⌟', 'lrcorner': '⌟', 'frown': '⌢', 'sfrown': '⌢', 'smile': '⌣', 'ssmile': '⌣', 'cylcty': '⌭', 'profalar': '⌮', 'topbot': '⌶', 'ovbar': '⌽', 'solbar': '⌿', 'angzarr': '⍼', 'lmoust': '⎰', 'lmoustache': '⎰', 'rmoust': '⎱', 'rmoustache': '⎱', 'tbrk': '⎴', 'OverBracket': '⎴', 'bbrk': '⎵', 'UnderBracket': '⎵', 'bbrktbrk': '⎶', 'OverParenthesis': '⏜', 'UnderParenthesis': '⏝', 'OverBrace': '⏞', 'UnderBrace': '⏟', 'trpezium': '⏢', 'elinters': '⏧', 'blank': '␣', 'oS': 'Ⓢ', 'circledS': 'Ⓢ', 'boxh': '─', 'HorizontalLine': '─', 'boxv': '│', 'boxdr': '┌', 'boxdl': '┐', 'boxur': '└', 'boxul': '┘', 'boxvr': '├', 'boxvl': '┤', 'boxhd': '┬', 'boxhu': '┴', 'boxvh': '┼', 'boxH': '═', 'boxV': '║', 'boxdR': '╒', 'boxDr': '╓', 'boxDR': '╔', 'boxdL': '╕', 'boxDl': '╖', 'boxDL': '╗', 'boxuR': '╘', 'boxUr': '╙', 'boxUR': '╚', 'boxuL': '╛', 'boxUl': '╜', 'boxUL': '╝', 'boxvR': '╞', 'boxVr': '╟', 'boxVR': '╠', 'boxvL': '╡', 'boxVl': '╢', 'boxVL': '╣', 'boxHd': '╤', 'boxhD': '╥', 'boxHD': '╦', 'boxHu': '╧', 'boxhU': '╨', 'boxHU': '╩', 'boxvH': '╪', 'boxVh': '╫', 'boxVH': '╬', 'uhblk': '▀', 'lhblk': '▄', 'block': '█', 'blk14': '░', 'blk12': '▒', 'blk34': '▓', 'squ': '□', 'square': '□', 'Square': '□', 'squf': '▪', 'squarf': '▪', 'blacksquare': '▪', 'FilledVerySmallSquare': '▪', 'EmptyVerySmallSquare': '▫', 'rect': '▭', 'marker': '▮', 'fltns': '▱', 'xutri': '△', 'bigtriangleup': '△', 'utrif': '▴', 'blacktriangle': '▴', 'utri': '▵', 'triangle': '▵', 'rtrif': '▸', 'blacktriangleright': '▸', 'rtri': '▹', 'triangleright': '▹', 'xdtri': '▽', 'bigtriangledown': '▽', 'dtrif': '▾', 'blacktriangledown': '▾', 'dtri': '▿', 'triangledown': '▿', 'ltrif': '◂', 'blacktriangleleft': '◂', 'ltri': '◃', 'triangleleft': '◃', 'loz': '◊', 'lozenge': '◊', 'cir': '○', 'tridot': '◬', 'xcirc': '◯', 'bigcirc': '◯', 'ultri': '◸', 'urtri': '◹', 'lltri': '◺', 'EmptySmallSquare': '◻', 'FilledSmallSquare': '◼', 'starf': '★', 'bigstar': '★', 'star': '☆', 'phone': '☎', 'female': '♀', 'male': '♂', 'spades': '♠', 'spadesuit': '♠', 'clubs': '♣', 'clubsuit': '♣', 'hearts': '♥', 'heartsuit': '♥', 'diams': '♦', 'diamondsuit': '♦', 'sung': '♪', 'flat': '♭', 'natur': '♮', 'natural': '♮', 'sharp': '♯', 'check': '✓', 'checkmark': '✓', 'cross': '✗', 'malt': '✠', 'maltese': '✠', 'sext': '✶', 'VerticalSeparator': '❘', 'lbbrk': '❲', 'rbbrk': '❳', 'bsolhsub': '⟈', 'suphsol': '⟉', 'lobrk': '⟦', 'LeftDoubleBracket': '⟦', 'robrk': '⟧', 'RightDoubleBracket': '⟧', 'lang': '⟨', 'LeftAngleBracket': '〈', 'langle': '〈', 'rang': '⟩', 'RightAngleBracket': '〉', 'rangle': '〉', 'Lang': '⟪', 'Rang': '⟫', 'loang': '⟬', 'roang': '⟭', 'xlarr': '⟵', 'longleftarrow': '⟵', 'LongLeftArrow': '⟵', 'xrarr': '⟶', 'longrightarrow': '⟶', 'LongRightArrow': '⟶', 'xharr': '⟷', 'longleftrightarrow': '⟷', 'LongLeftRightArrow': '⟷', 'xlArr': '⟸', 'Longleftarrow': '⟸', 'DoubleLongLeftArrow': '⟸', 'xrArr': '⟹', 'Longrightarrow': '⟹', 'DoubleLongRightArrow': '⟹', 'xhArr': '⟺', 'Longleftrightarrow': '⟺', 'DoubleLongLeftRightArrow': '⟺', 'xmap': '⟼', 'longmapsto': '⟼', 'dzigrarr': '⟿', 'nvlArr': '⤂', 'nvrArr': '⤃', 'nvHarr': '⤄', 'Map': '⤅', 'lbarr': '⤌', 'rbarr': '⤍', 'bkarow': '⤍', 'lBarr': '⤎', 'rBarr': '⤏', 'dbkarow': '⤏', 'RBarr': '⤐', 'drbkarow': '⤐', 'DDotrahd': '⤑', 'UpArrowBar': '⤒', 'DownArrowBar': '⤓', 'Rarrtl': '⤖', 'latail': '⤙', 'ratail': '⤚', 'lAtail': '⤛', 'rAtail': '⤜', 'larrfs': '⤝', 'rarrfs': '⤞', 'larrbfs': '⤟', 'rarrbfs': '⤠', 'nwarhk': '⤣', 'nearhk': '⤤', 'searhk': '⤥', 'hksearow': '⤥', 'swarhk': '⤦', 'hkswarow': '⤦', 'nwnear': '⤧', 'nesear': '⤨', 'toea': '⤨', 'seswar': '⤩', 'tosa': '⤩', 'swnwar': '⤪', 'rarrc': '⤳', 'cudarrr': '⤵', 'ldca': '⤶', 'rdca': '⤷', 'cudarrl': '⤸', 'larrpl': '⤹', 'curarrm': '⤼', 'cularrp': '⤽', 'rarrpl': '⥅', 'harrcir': '⥈', 'Uarrocir': '⥉', 'lurdshar': '⥊', 'ldrushar': '⥋', 'LeftRightVector': '⥎', 'RightUpDownVector': '⥏', 'DownLeftRightVector': '⥐', 'LeftUpDownVector': '⥑', 'LeftVectorBar': '⥒', 'RightVectorBar': '⥓', 'RightUpVectorBar': '⥔', 'RightDownVectorBar': '⥕', 'DownLeftVectorBar': '⥖', 'DownRightVectorBar': '⥗', 'LeftUpVectorBar': '⥘', 'LeftDownVectorBar': '⥙', 'LeftTeeVector': '⥚', 'RightTeeVector': '⥛', 'RightUpTeeVector': '⥜', 'RightDownTeeVector': '⥝', 'DownLeftTeeVector': '⥞', 'DownRightTeeVector': '⥟', 'LeftUpTeeVector': '⥠', 'LeftDownTeeVector': '⥡', 'lHar': '⥢', 'uHar': '⥣', 'rHar': '⥤', 'dHar': '⥥', 'luruhar': '⥦', 'ldrdhar': '⥧', 'ruluhar': '⥨', 'rdldhar': '⥩', 'lharul': '⥪', 'llhard': '⥫', 'rharul': '⥬', 'lrhard': '⥭', 'udhar': '⥮', 'UpEquilibrium': '⥮', 'duhar': '⥯', 'ReverseUpEquilibrium': '⥯', 'RoundImplies': '⥰', 'erarr': '⥱', 'simrarr': '⥲', 'larrsim': '⥳', 'rarrsim': '⥴', 'rarrap': '⥵', 'ltlarr': '⥶', 'gtrarr': '⥸', 'subrarr': '⥹', 'suplarr': '⥻', 'lfisht': '⥼', 'rfisht': '⥽', 'ufisht': '⥾', 'dfisht': '⥿', 'lopar': '⦅', 'ropar': '⦆', 'lbrke': '⦋', 'rbrke': '⦌', 'lbrkslu': '⦍', 'rbrksld': '⦎', 'lbrksld': '⦏', 'rbrkslu': '⦐', 'langd': '⦑', 'rangd': '⦒', 'lparlt': '⦓', 'rpargt': '⦔', 'gtlPar': '⦕', 'ltrPar': '⦖', 'vzigzag': '⦚', 'vangrt': '⦜', 'angrtvbd': '⦝', 'ange': '⦤', 'range': '⦥', 'dwangle': '⦦', 'uwangle': '⦧', 'angmsdaa': '⦨', 'angmsdab': '⦩', 'angmsdac': '⦪', 'angmsdad': '⦫', 'angmsdae': '⦬', 'angmsdaf': '⦭', 'angmsdag': '⦮', 'angmsdah': '⦯', 'bemptyv': '⦰', 'demptyv': '⦱', 'cemptyv': '⦲', 'raemptyv': '⦳', 'laemptyv': '⦴', 'ohbar': '⦵', 'omid': '⦶', 'opar': '⦷', 'operp': '⦹', 'olcross': '⦻', 'odsold': '⦼', 'olcir': '⦾', 'ofcir': '⦿', 'olt': '⧀', 'ogt': '⧁', 'cirscir': '⧂', 'cirE': '⧃', 'solb': '⧄', 'bsolb': '⧅', 'boxbox': '⧉', 'trisb': '⧍', 'rtriltri': '⧎', 'LeftTriangleBar': '⧏', 'RightTriangleBar': '⧐', 'iinfin': '⧜', 'infintie': '⧝', 'nvinfin': '⧞', 'eparsl': '⧣', 'smeparsl': '⧤', 'eqvparsl': '⧥', 'lozf': '⧫', 'blacklozenge': '⧫', 'RuleDelayed': '⧴', 'dsol': '⧶', 'xodot': '⨀', 'bigodot': '⨀', 'xoplus': '⨁', 'bigoplus': '⨁', 'xotime': '⨂', 'bigotimes': '⨂', 'xuplus': '⨄', 'biguplus': '⨄', 'xsqcup': '⨆', 'bigsqcup': '⨆', 'qint': '⨌', 'iiiint': '⨌', 'fpartint': '⨍', 'cirfnint': '⨐', 'awint': '⨑', 'rppolint': '⨒', 'scpolint': '⨓', 'npolint': '⨔', 'pointint': '⨕', 'quatint': '⨖', 'intlarhk': '⨗', 'pluscir': '⨢', 'plusacir': '⨣', 'simplus': '⨤', 'plusdu': '⨥', 'plussim': '⨦', 'plustwo': '⨧', 'mcomma': '⨩', 'minusdu': '⨪', 'loplus': '⨭', 'roplus': '⨮', 'Cross': '⨯', 'timesd': '⨰', 'timesbar': '⨱', 'smashp': '⨳', 'lotimes': '⨴', 'rotimes': '⨵', 'otimesas': '⨶', 'Otimes': '⨷', 'odiv': '⨸', 'triplus': '⨹', 'triminus': '⨺', 'tritime': '⨻', 'iprod': '⨼', 'intprod': '⨼', 'amalg': '⨿', 'capdot': '⩀', 'ncup': '⩂', 'ncap': '⩃', 'capand': '⩄', 'cupor': '⩅', 'cupcap': '⩆', 'capcup': '⩇', 'cupbrcap': '⩈', 'capbrcup': '⩉', 'cupcup': '⩊', 'capcap': '⩋', 'ccups': '⩌', 'ccaps': '⩍', 'ccupssm': '⩐', 'And': '⩓', 'Or': '⩔', 'andand': '⩕', 'oror': '⩖', 'orslope': '⩗', 'andslope': '⩘', 'andv': '⩚', 'orv': '⩛', 'andd': '⩜', 'ord': '⩝', 'wedbar': '⩟', 'sdote': '⩦', 'simdot': '⩪', 'congdot': '⩭', 'easter': '⩮', 'apacir': '⩯', 'apE': '⩰', 'eplus': '⩱', 'pluse': '⩲', 'Esim': '⩳', 'Colone': '⩴', 'Equal': '⩵', 'eDDot': '⩷', 'ddotseq': '⩷', 'equivDD': '⩸', 'ltcir': '⩹', 'gtcir': '⩺', 'ltquest': '⩻', 'gtquest': '⩼', 'les': '⩽', 'LessSlantEqual': '⩽', 'leqslant': '⩽', 'ges': '⩾', 'GreaterSlantEqual': '⩾', 'geqslant': '⩾', 'lesdot': '⩿', 'gesdot': '⪀', 'lesdoto': '⪁', 'gesdoto': '⪂', 'lesdotor': '⪃', 'gesdotol': '⪄', 'lap': '⪅', 'lessapprox': '⪅', 'gap': '⪆', 'gtrapprox': '⪆', 'lne': '⪇', 'lneq': '⪇', 'gne': '⪈', 'gneq': '⪈', 'lnap': '⪉', 'lnapprox': '⪉', 'gnap': '⪊', 'gnapprox': '⪊', 'lEg': '⪋', 'lesseqqgtr': '⪋', 'gEl': '⪌', 'gtreqqless': '⪌', 'lsime': '⪍', 'gsime': '⪎', 'lsimg': '⪏', 'gsiml': '⪐', 'lgE': '⪑', 'glE': '⪒', 'lesges': '⪓', 'gesles': '⪔', 'els': '⪕', 'eqslantless': '⪕', 'egs': '⪖', 'eqslantgtr': '⪖', 'elsdot': '⪗', 'egsdot': '⪘', 'el': '⪙', 'eg': '⪚', 'siml': '⪝', 'simg': '⪞', 'simlE': '⪟', 'simgE': '⪠', 'LessLess': '⪡', 'GreaterGreater': '⪢', 'glj': '⪤', 'gla': '⪥', 'ltcc': '⪦', 'gtcc': '⪧', 'lescc': '⪨', 'gescc': '⪩', 'smt': '⪪', 'lat': '⪫', 'smte': '⪬', 'late': '⪭', 'bumpE': '⪮', 'pre': '⪯', 'preceq': '⪯', 'PrecedesEqual': '⪯', 'sce': '⪰', 'succeq': '⪰', 'SucceedsEqual': '⪰', 'prE': '⪳', 'scE': '⪴', 'prnE': '⪵', 'precneqq': '⪵', 'scnE': '⪶', 'succneqq': '⪶', 'prap': '⪷', 'precapprox': '⪷', 'scap': '⪸', 'succapprox': '⪸', 'prnap': '⪹', 'precnapprox': '⪹', 'scnap': '⪺', 'succnapprox': '⪺', 'Pr': '⪻', 'Sc': '⪼', 'subdot': '⪽', 'supdot': '⪾', 'subplus': '⪿', 'supplus': '⫀', 'submult': '⫁', 'supmult': '⫂', 'subedot': '⫃', 'supedot': '⫄', 'subE': '⫅', 'subseteqq': '⫅', 'supE': '⫆', 'supseteqq': '⫆', 'subsim': '⫇', 'supsim': '⫈', 'subnE': '⫋', 'subsetneqq': '⫋', 'supnE': '⫌', 'supsetneqq': '⫌', 'csub': '⫏', 'csup': '⫐', 'csube': '⫑', 'csupe': '⫒', 'subsup': '⫓', 'supsub': '⫔', 'subsub': '⫕', 'supsup': '⫖', 'suphsub': '⫗', 'supdsub': '⫘', 'forkv': '⫙', 'topfork': '⫚', 'mlcp': '⫛', 'Dashv': '⫤', 'DoubleLeftTee': '⫤', 'Vdashl': '⫦', 'Barv': '⫧', 'vBar': '⫨', 'vBarv': '⫩', 'Vbar': '⫫', 'Not': '⫬', 'bNot': '⫭', 'rnmid': '⫮', 'cirmid': '⫯', 'midcir': '⫰', 'topcir': '⫱', 'nhpar': '⫲', 'parsim': '⫳', 'parsl': '⫽', 'fflig': 'ﬀ', 'filig': 'ﬁ', 'fllig': 'ﬂ', 'ffilig': 'ﬃ', 'ffllig': 'ﬄ', 'Ascr': '𝒜', 'Cscr': '𝒞', 'Dscr': '𝒟', 'Gscr': '𝒢', 'Jscr': '𝒥', 'Kscr': '𝒦', 'Nscr': '𝒩', 'Oscr': '𝒪', 'Pscr': '𝒫', 'Qscr': '𝒬', 'Sscr': '𝒮', 'Tscr': '𝒯', 'Uscr': '𝒰', 'Vscr': '𝒱', 'Wscr': '𝒲', 'Xscr': '𝒳', 'Yscr': '𝒴', 'Zscr': '𝒵', 'ascr': '𝒶', 'bscr': '𝒷', 'cscr': '𝒸', 'dscr': '𝒹', 'fscr': '𝒻', 'hscr': '𝒽', 'iscr': '𝒾', 'jscr': '𝒿', 'kscr': '𝓀', 'lscr': '𝓁', 'mscr': '𝓂', 'nscr': '𝓃', 'pscr': '𝓅', 'qscr': '𝓆', 'rscr': '𝓇', 'sscr': '𝓈', 'tscr': '𝓉', 'uscr': '𝓊', 'vscr': '𝓋', 'wscr': '𝓌', 'xscr': '𝓍', 'yscr': '𝓎', 'zscr': '𝓏', 'Afr': '𝔄', 'Bfr': '𝔅', 'Dfr': '𝔇', 'Efr': '𝔈', 'Ffr': '𝔉', 'Gfr': '𝔊', 'Jfr': '𝔍', 'Kfr': '𝔎', 'Lfr': '𝔏', 'Mfr': '𝔐', 'Nfr': '𝔑', 'Ofr': '𝔒', 'Pfr': '𝔓', 'Qfr': '𝔔', 'Sfr': '𝔖', 'Tfr': '𝔗', 'Ufr': '𝔘', 'Vfr': '𝔙', 'Wfr': '𝔚', 'Xfr': '𝔛', 'Yfr': '𝔜', 'afr': '𝔞', 'bfr': '𝔟', 'cfr': '𝔠', 'dfr': '𝔡', 'efr': '𝔢', 'ffr': '𝔣', 'gfr': '𝔤', 'hfr': '𝔥', 'ifr': '𝔦', 'jfr': '𝔧', 'kfr': '𝔨', 'lfr': '𝔩', 'mfr': '𝔪', 'nfr': '𝔫', 'ofr': '𝔬', 'pfr': '𝔭', 'qfr': '𝔮', 'rfr': '𝔯', 'sfr': '𝔰', 'tfr': '𝔱', 'ufr': '𝔲', 'vfr': '𝔳', 'wfr': '𝔴', 'xfr': '𝔵', 'yfr': '𝔶', 'zfr': '𝔷', 'Aopf': '𝔸', 'Bopf': '𝔹', 'Dopf': '𝔻', 'Eopf': '𝔼', 'Fopf': '𝔽', 'Gopf': '𝔾', 'Iopf': '𝕀', 'Jopf': '𝕁', 'Kopf': '𝕂', 'Lopf': '𝕃', 'Mopf': '𝕄', 'Oopf': '𝕆', 'Sopf': '𝕊', 'Topf': '𝕋', 'Uopf': '𝕌', 'Vopf': '𝕍', 'Wopf': '𝕎', 'Xopf': '𝕏', 'Yopf': '𝕐', 'aopf': '𝕒', 'bopf': '𝕓', 'copf': '𝕔', 'dopf': '𝕕', 'eopf': '𝕖', 'fopf': '𝕗', 'gopf': '𝕘', 'hopf': '𝕙', 'iopf': '𝕚', 'jopf': '𝕛', 'kopf': '𝕜', 'lopf': '𝕝', 'mopf': '𝕞', 'nopf': '𝕟', 'oopf': '𝕠', 'popf': '𝕡', 'qopf': '𝕢', 'ropf': '𝕣', 'sopf': '𝕤', 'topf': '𝕥', 'uopf': '𝕦', 'vopf': '𝕧', 'wopf': '𝕨', 'xopf': '𝕩', 'yopf': '𝕪', 'zopf': '𝕫', 'nvlt': '<', 'bne': '=', 'nvgt': '>', 'fjlig': 'f', 'ThickSpace': '\u205f', 'nrarrw': '↝', 'npart': '∂', 'nang': '∠', 'caps': '∩', 'cups': '∪', 'nvsim': '∼', 'race': '∽', 'acE': '∾', 'nesim': '≂', 'NotEqualTilde': '≂', 'napid': '≋', 'nvap': '≍', 'nbump': '≎', 'NotHumpDownHump': '≎', 'nbumpe': '≏', 'NotHumpEqual': '≏', 'nedot': '≐', 'bnequiv': '≡', 'nvle': '≤', 'nvge': '≥', 'nlE': '≦', 'nleqq': '≦', 'ngE': '≧', 'ngeqq': '≧', 'NotGreaterFullEqual': '≧', 'lvertneqq': '≨', 'lvnE': '≨', 'gvertneqq': '≩', 'gvnE': '≩', 'nLtv': '≪', 'NotLessLess': '≪', 'nLt': '≪', 'nGtv': '≫', 'NotGreaterGreater': '≫', 'nGt': '≫', 'NotSucceedsTilde': '≿', 'NotSubset': '⊂', 'nsubset': '⊂', 'vnsub': '⊂', 'NotSuperset': '⊃', 'nsupset': '⊃', 'vnsup': '⊃', 'varsubsetneq': '⊊', 'vsubne': '⊊', 'varsupsetneq': '⊋', 'vsupne': '⊋', 'NotSquareSubset': '⊏', 'NotSquareSuperset': '⊐', 'sqcaps': '⊓', 'sqcups': '⊔', 'nvltrie': '⊴', 'nvrtrie': '⊵', 'nLl': '⋘', 'nGg': '⋙', 'lesg': '⋚', 'gesl': '⋛', 'notindot': '⋵', 'notinE': '⋹', 'nrarrc': '⤳', 'NotLeftTriangleBar': '⧏', 'NotRightTriangleBar': '⧐', 'ncongdot': '⩭', 'napE': '⩰', 'nleqslant': '⩽', 'nles': '⩽', 'NotLessSlantEqual': '⩽', 'ngeqslant': '⩾', 'nges': '⩾', 'NotGreaterSlantEqual': '⩾', 'NotNestedLessLess': '⪡', 'NotNestedGreaterGreater': '⪢', 'smtes': '⪬', 'lates': '⪭', 'NotPrecedesEqual': '⪯', 'npre': '⪯', 'npreceq': '⪯', 'NotSucceedsEqual': '⪰', 'nsce': '⪰', 'nsucceq': '⪰', 'nsubE': '⫅', 'nsubseteqq': '⫅', 'nsupE': '⫆', 'nsupseteqq': '⫆', 'varsubsetneqq': '⫋', 'vsubnE': '⫋', 'varsupsetneqq': '⫌', 'vsupnE': '⫌', 'nparsl': '⫽', 'lpar': '(', 'AMP': '&', 'NewLine': '\n'}





