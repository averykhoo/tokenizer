import json
from typing import Dict
from typing import List
from typing import Pattern
from typing import Union

import regex
import unicodedata

_REGEX_GRAPHEME: Pattern = regex.compile(r'\X', flags=regex.UNICODE)  # builtins.re does not support `\X`
_REGEX_WORD_CHAR: Pattern = regex.compile(r'\w', flags=regex.UNICODE)

_ASCII_ALIKE: Dict[str, str] = {
    # todo: missing bold digits e.g. U+1D7CF, see https://www.compart.com/en/unicode/block/U+1D400
    '0': '⁰₀⓪⓿',
    '1': '¹₁①⑴⓵',
    '2': '²₂②⑵⓶',
    '3': '³₃③⑶⓷',
    '4': '⁴₄④⑷⓸',
    '5': '⁵₅⑤⑸⓹',
    '6': '⁶₆⑥⑹⓺',
    '7': '⁷₇⑦⑺⓻',
    '8': '⁸₈⑧⑻⓼',
    '9': '⁹₉⑨⑼⓽',
    'A': 'ÀÁÂÃÄÅĀĂĄǍǞǠǺȀȂȦȺΆΑᴀᴬḀẠẢẤẦẨẪẬẮẰẲẴẶἈἉἊἋἌἍἎἏᾈᾉᾊᾋᾌᾍᾎᾏᾸᾹᾺΆᾼÅ∀ⒶⱯＡ𝐀𝐴𝑨𝒜𝓐𝔄𝔸𝕬𝖠𝗔𝘈𝘼𝙰🄐🄰🅐🅰🇦',
    'B': 'ƁƂɃʙΒᴃᴮᴯḂḄḆℬⒷＢ𝐁𝐵𝑩𝓑𝔅𝔹𝕭𝖡𝗕𝘉𝘽𝙱🄑🄱🅑🅱🇧',
    'C': 'ÇĆĈĊČƇȻʗᴄḈℂℭ∁ⒸＣ𝐂𝐶𝑪𝒞𝓒𝕮𝖢𝗖𝘊𝘾𝙲🄒🄫🄲🅒🅲🇨',
    'D': 'ÐĎĐƉƊƋᴅᴆᴰḊḌḎḐḒⅅⒹＤ𝐃𝐷𝑫𝒟𝓓𝔇𝔻𝕯𝖣𝗗𝘋𝘿𝙳🄓🄳🅓🅳🇩',
    'E': 'ÈÉÊËĒĔĖĘĚƐȄȆȨɆʚΈΕᴇᴱᴲḔḖḘḚḜẸẺẼẾỀỂỄỆἘἙἚἛἜἝῈΈℰ∃ⒺＥ𝐄𝐸𝑬𝓔𝔈𝔼𝕰𝖤𝗘𝘌𝙀𝙴🄔🄴🅔🅴🇪',
    'F': 'ƑḞℱℲⅎⒻＦ𝐅𝐹𝑭𝓕𝔉𝔽𝕱𝖥𝗙𝘍𝙁𝙵🄕🄵🅕🅵🇫',
    'G': 'ĜĞĠĢƓǤǦǴʛᴳḠⒼＧ𝐆𝐺𝑮𝒢𝓖𝔊𝔾𝕲𝖦𝗚𝘎𝙂𝙶🄖🄶🅖🅶🇬',
    'H': 'ĤĦȞʜᴴḢḤḦḨḪℋℌℍⒽⱧＨ𝐇𝐻𝑯𝓗𝕳𝖧𝗛𝘏𝙃𝙷🄗🄷🅗🅷🇭',
    'I': 'ÌÍÎÏĨĪĬĮİƖƗǏȈȊɪΊΐΙΪᴵḬḮỈỊἸἹἺἻἼἽἾἿῘῙῚΊℐℑⒾＩ𝐈𝐼𝑰𝓘𝕀𝕴𝖨𝗜𝘐𝙄𝙸🄘🄸🅘🅸🇮',
    'J': 'ĴɈᴊᴶⒿＪ𝐉𝐽𝑱𝒥𝓙𝔍𝕁𝕵𝖩𝗝𝘑𝙅𝙹🄙🄹🅙🅹🇯',
    'K': 'ĶƘǨΚᴋᴷḰḲḴKⓀⱩＫ𝐊𝐾𝑲𝒦𝓚𝔎𝕂𝕶𝖪𝗞𝘒𝙆𝙺🄚🄺🅚🅺🇰',
    'L': 'ĹĻĽĿŁȽʟᴌᴸḶḸḺḼℒⓁⱠⱢＬ𝐋𝐿𝑳𝓛𝔏𝕃𝕷𝖫𝗟𝘓𝙇𝙻🄛🄻🅛🅻🇱',
    'M': 'ΜᴍᴹḾṀṂℳⓂⱮＭ𝐌𝑀𝑴𝓜𝔐𝕄𝕸𝖬𝗠𝘔𝙈𝙼🄜🄼🅜🅼🇲',
    'N': 'ÑŃŅŇƝǸȠΝᴎᴺᴻṄṆṈṊℕⓃＮ𝐍𝑁𝑵𝒩𝓝𝔑𝕹𝖭𝗡𝘕𝙉𝙽🄝🄽🅝🅽🇳',
    'O': 'ÒÓÔÕÖØŌŎŐƟƠǑǪǬǾȌȎȪȬȮȰΌΟᴏᴑᴓᴼṌṎṐṒỌỎỐỒỔỖỘỚỜỞỠỢὈὉὊὋὌὍῸΌⓄＯ𝐎𝑂𝑶𝒪𝓞𝔒𝕆𝕺𝖮𝗢𝘖𝙊𝙾🄞🄾🅞🅾🇴',
    'P': 'ƤᴘᴾṔṖℙⓅⱣＰ𝐏𝑃𝑷𝒫𝓟𝔓𝕻𝖯𝗣𝘗𝙋𝙿🄟🄿🅟🅿🇵',
    'Q': 'ℚⓆＱ𝐐𝑄𝑸𝒬𝓠𝔔𝕼𝖰𝗤𝘘𝙌𝚀🄠🅀🅠🆀🇶',
    'R': 'ŔŖŘȐȒɌʀʁᴙᴚᴿṘṚṜṞῬℛℜℝⓇⱤＲ𝐑𝑅𝑹𝓡𝕽𝖱𝗥𝘙𝙍𝚁🄡🄬🅁🅡🆁🇷',
    'S': 'ŚŜŞŠȘʃʅʆΣṠṢṤṦṨẛⓈＳ𝐒𝑆𝑺𝒮𝓢𝔖𝕊𝕾𝖲𝗦𝘚𝙎𝚂🄢🄪🅂🅢🆂🇸',
    'T': 'ŢŤŦƬƮȚȾΤᴛᵀṪṬṮṰ⊤⊥ⓉＴ𝐓𝑇𝑻𝒯𝓣𝔗𝕋𝕿𝖳𝗧𝘛𝙏𝚃🄣🅃🅣🆃🇹',
    'U': 'ÙÚÛÜŨŪŬŮŰŲƯǓǕǗǙǛȔȖɄʊᴜᵁṲṴṶṸṺỤỦỨỪỬỮỰⓊＵ𝐔𝑈𝑼𝒰𝓤𝔘𝕌𝖀𝖴𝗨𝘜𝙐𝚄🄤🅄🅤🆄🇺',
    'V': 'ƲˬᴠṼṾ∨ⓋＶ𝐕𝑉𝑽𝒱𝓥𝔙𝕍𝖁𝖵𝗩𝘝𝙑𝚅🄥🅅🅥🆅🇻',
    'W': 'ŴƜɯɰᴡᵂẀẂẄẆẈⓌＷ𝐖𝑊𝑾𝒲𝓦𝔚𝕎𝖂𝖶𝗪𝘞𝙒𝚆🄦🅆🅦🆆🇼',
    'X': 'ẊẌⓍＸ𝐗𝑋𝑿𝒳𝓧𝔛𝕏𝖃𝖷𝗫𝘟𝙓𝚇🄧🅇🅧🆇🇽',
    'Y': 'ÝŶŸƱƳȲɎɥʏẎỲỴỶỸⓎＹ𝐘𝑌𝒀𝒴𝓨𝔜𝕐𝖄𝖸𝗬𝘠𝙔𝚈🄨🅈🅨🆈🇾',
    'Z': 'ŹŻŽƵȤʒʓᴢẐẒẔℤℨⓏⱫＺ𝐙𝑍𝒁𝒵𝓩𝖅𝖹𝗭𝘡𝙕𝚉🄩🅉🅩🆉🇿',
    'a': 'ªàáâãäåāăąǎǟǡǻȁȃȧɐɑɒάαᵃᵄᵅḁẚạảấầẩẫậắằẳẵặἀἁἂἃἄἅἆἇὰάᾀᾁᾂᾃᾄᾅᾆᾇᾰᾱᾲᾳᾴᾶᾷₐ⒜ⓐⱥａ𝐚𝑎𝒂𝒶𝓪𝔞𝕒𝖆𝖺𝗮𝘢𝙖𝚊',
    'b': 'ƀƃɓβϐᵇᵝᵦᵬᶀḃḅḇ⒝ⓑｂ𝐛𝑏𝒃𝒷𝓫𝔟𝕓𝖇𝖻𝗯𝘣𝙗𝚋',
    'c': '©çćĉċčƈȼɕϲḉ⒞ⓒｃ𝐜𝑐𝒄𝒸𝓬𝔠𝕔𝖈𝖼𝗰𝘤𝙘𝚌',
    'd': 'ðďđƌƍȡɖɗδᵈᵟᵭᶁḋḍḏḑḓⅆ⒟ⓓｄ𝐝𝑑𝒅𝒹𝓭𝔡𝕕𝖉𝖽𝗱𝘥𝙙𝚍🆥',
    'e': 'èéêëēĕėęěȅȇȩɇɘɛɜɝɞέεᴈᵉᵋᵌḕḗḙḛḝẹẻẽếềểễệἐἑἒἓἔἕὲέₑ℮ℯⅇ⒠ⓔｅ𝐞𝑒𝒆𝓮𝔢𝕖𝖊𝖾𝗲𝘦𝙚𝚎',
    'f': 'ƒᵮᶂḟ⒡ⓕｆ𝐟𝑓𝒇𝒻𝓯𝔣𝕗𝖋𝖿𝗳𝘧𝙛𝚏',
    'g': 'ĝğġģǥǧǵɠɡɢᵍᵷᶃḡℊ⒢ⓖｇ𝐠𝑔𝒈𝓰𝔤𝕘𝖌𝗀𝗴𝘨𝙜𝚐',
    'h': 'ĥħȟɦɧʮʯʰʱḣḥḧḩḫẖₕℎ⒣ⓗⱨｈ𝐡𝒉𝒽𝓱𝔥𝕙𝖍𝗁𝗵𝘩𝙝𝚑',
    'i': 'ìíîïĩīĭįıǐȉȋɨɩίιϊᴉᵎᵢḭḯỉịἰἱἲἳἴἵἶἷὶίιῐῑῒΐῖῗⁱℹⅈ⒤ⓘｉ𝐢𝑖𝒊𝒾𝓲𝔦𝕚𝖎𝗂𝗶𝘪𝙞𝚒𝚤',
    'j': 'ĵǰȷɉɟʄʝʲϳⅉ⒥ⓙｊ𝐣𝑗𝒋𝒿𝓳𝔧𝕛𝖏𝗃𝗷𝘫𝙟𝚓𝚥',
    'k': 'ķĸƙǩʞκᵏᶄḱḳḵₖ⒦ⓚⱪｋ𝐤𝑘𝒌𝓀𝓴𝔨𝕜𝖐𝗄𝗸𝘬𝙠𝚔',
    'l': 'ĺļľŀłƚƛȴɫɬɭˡᶅḷḹḻḽₗℓ⒧ⓛⱡｌ𝐥𝑙𝒍𝓁𝓵𝔩𝕝𝖑𝗅𝗹𝘭𝙡𝚕',
    'm': 'ɱμᴟᵐᵚᵯᶆḿṁṃₘ⒨ⓜｍ𝐦𝑚𝒎𝓂𝓶𝔪𝕞𝖒𝗆𝗺𝘮𝙢𝚖',
    'n': 'ñńņňƞǹȵɲɳɴνᵰᶇṅṇṉṋⁿₙ⒩ⓝｎ𝐧𝑛𝒏𝓃𝓷𝔫𝕟𝖓𝗇𝗻𝘯𝙣𝚗',
    'o': 'ºòóôõöøōŏőơǒǫǭǿȍȏȫȭȯȱɔɵοόᵒṍṏṑṓọỏốồổỗộớờởỡợὀὁὂὃὄὅὸόₒℴ⒪ⓞｏ𝐨𝑜𝒐𝓸𝔬𝕠𝖔𝗈𝗼𝘰𝙤𝚘',
    'p': 'ƥᵖᵱᵽᶈṕṗₚ℗⒫ⓟｐ𝐩𝑝𝒑𝓅𝓹𝔭𝕡𝖕𝗉𝗽𝘱𝙥𝚙',
    'q': 'Ɋɋʠ⒬ⓠｑ𝐪𝑞𝒒𝓆𝓺𝔮𝕢𝖖𝗊𝗾𝘲𝙦𝚚',
    'r': '®ŕŗřȑȓɍɹɺɻɼɽɾɿʳʴʵʶᵣᵨᵲᵳᶉṙṛṝṟ⒭ⓡｒ𝐫𝑟𝒓𝓇𝓻𝔯𝕣𝖗𝗋𝗿𝘳𝙧𝚛',
    's': 'śŝşšſșȿʂˢςσᵴᶊṡṣṥṧṩₛ⒮ⓢｓ𝐬𝑠𝒔𝓈𝓼𝔰𝕤𝖘𝗌𝘀𝘴𝙨𝚜',
    't': 'ţťŧƫƭțȶʇʈτᵗᵵṫṭṯṱẗₜ⒯ⓣⱦｔ𝐭𝑡𝒕𝓉𝓽𝔱𝕥𝖙𝗍𝘁𝘵𝙩𝚝',
    'u': 'µùúûüũūŭůűųưǔǖǘǚǜȕȗɤʉΰυϋύᴝᴞᵘᵙᵤṳṵṷṹṻụủứừửữựὐὑὒὓὔὕὖὗὺύῠῡῢΰῦῧ⒰ⓤｕ𝐮𝑢𝒖𝓊𝓾𝔲𝕦𝖚𝗎𝘂𝘶𝙪𝚞',
    'v': 'ʋᵛᵥᶌṽṿ⒱ⓥｖ𝐯𝑣𝒗𝓋𝓿𝔳𝕧𝖛𝗏𝘃𝘷𝙫𝚟',
    'w': 'ŵʍʷẁẃẅẇẉẘ⒲ⓦｗ𝐰𝑤𝒘𝓌𝔀𝔴𝕨𝖜𝗐𝘄𝘸𝙬𝚠',
    'x': 'ˣᶍẋẍₓ⒳ⓧｘ𝐱𝑥𝒙𝓍𝔁𝔵𝕩𝖝𝗑𝘅𝘹𝙭𝚡',
    'y': 'ýÿŷƴȳɏʎʸẏẙỳỵỷỹ⒴ⓨｙ𝐲𝑦𝒚𝓎𝔂𝔶𝕪𝖞𝗒𝘆𝘺𝙮𝚢',
    'z': 'źżžƶȥɀʐʑᵶᶎẑẓẕ⒵ⓩⱬｚ𝐳𝑧𝒛𝓏𝔃𝔷𝕫𝖟𝗓𝘇𝘻𝙯𝚣',
}
_ASCII_ALIKE_LOOKUP: Dict[int, str] = {ord(char): alpha for alpha, chars in _ASCII_ALIKE.items() for char in chars}


def _preprocess(text: str,
                nfkd: bool = False,
                casefold: bool = False,
                replace_ascii: bool = False,
                ) -> str:
    # sanity check
    if not isinstance(text, str):
        raise TypeError(f'expected <str>, got <{type(text)}>')

    # step 1: unicode decomposition
    if nfkd:
        text = unicodedata.normalize("NFKD", text)

    # step 2: casefold (or lowercase if we're converting to ascii later)
    if casefold:
        text = text.lower() if replace_ascii else text.casefold()

    # step 3: replace ascii-like chars
    if replace_ascii:
        text = text.translate(_ASCII_ALIKE_LOOKUP)

    return text


def word_tokenize(text: str,
                  nfkd: bool = False,
                  casefold: bool = False,
                  replace_ascii: bool = False,
                  strip_diacritics: bool = False,
                  accept_apostrophe: Union[bool, int] = False,
                  include_non_word_chars: bool = False,
                  ) -> List[str]:
    """
    tokenize text into words
    * enable `nfkd` if you want to do string matching
    * enable `casefold` if you want case-insensitivity
    * enable `replace_ascii` if you want to match ascii strings against ascii-alike text
    * enable `strip_diacritics` if you want to fix zalgo text or want to ignore accents
    * enable `accept_apostrophe` if you want to allow an apostrophe in your word (not recommended)

    warning: if any flags are enabled, the output words may not be substrings of the input text

    :param text: to extract words from
    :param nfkd: unicode normal form compatibility decomposition
    :param casefold: lowercase but better
    :param replace_ascii: make ascii-like where possible
    :param strip_diacritics: unwrap graphemes, keeping only initial codepoint
    :param accept_apostrophe: allow an apostrophe, or an integer number of apostrophes
    :param include_non_word_chars: include non-word (e.g. whitespace) chars in the output token list
    :return: list of words
    """
    # sanity check
    assert isinstance(accept_apostrophe, (bool, int)) and accept_apostrophe >= 0

    # pre-process (and sanity check)
    text = _preprocess(text, nfkd=nfkd, casefold=casefold, replace_ascii=replace_ascii)

    # get all word tokens
    words = []
    word_buffer = []
    apostrophe_locations = []
    for match in _REGEX_GRAPHEME.finditer(f'\2{text}\3'):  # ensure first and last iterations are not graphemes
        grapheme = match.group(0)
        char = grapheme[0]

        # get all word-like graphemes
        # in my opinion, underscore is not word-like (despite what the unicode standard says)
        if _REGEX_WORD_CHAR.match(char):
            if char not in {'_'}:
                word_buffer.append(char if strip_diacritics else grapheme)
                continue

        # allow adding any number of apostrophes to words
        apostrophe_chars = set("'\u2019\uFF07")
        # we'll filter out words with too many apostrophes later
        if char in apostrophe_chars:
            apostrophe_locations.append(len(word_buffer))
            word_buffer.append(char if strip_diacritics else grapheme)
            continue

        # not a word-like grapheme, so clear word buffer
        if word_buffer:

            # if we have an acceptable number (possibly zero) of apostrophes
            if len(apostrophe_locations) <= accept_apostrophe:
                words.append(''.join(word_buffer))

            # otherwise split at the known apostrophe locations
            else:
                current_idx = 0
                for next_idx in apostrophe_locations:
                    if next_idx > current_idx:
                        words.append(''.join(word_buffer[current_idx:next_idx]))
                    current_idx = next_idx + 1
                if current_idx < len(word_buffer):  # don't forget to add the last bit, if any
                    words.append(''.join(word_buffer[current_idx:len(word_buffer)]))

            # clear buffers and keep looking for more words
            word_buffer.clear()
            apostrophe_locations.clear()

        if include_non_word_chars:
            words.append(char)

    # don't return the \2 and \3
    return words[1:-1] if include_non_word_chars else words


if __name__ == '__main__':
    print(json.dumps(word_tokenize('hello')))
    print(json.dumps(word_tokenize('hello world')))
    print(json.dumps(word_tokenize('𝐇𝐞𝐥𝐥𝐨 𝐖𝐨𝐫𝐥𝐝', nfkd=True)))
    print(json.dumps(word_tokenize('𝗛𝗲𝗹𝗹𝗼 𝗪𝗼𝗿𝗹𝗱', nfkd=True)))
    print(json.dumps(word_tokenize('𝐻𝑒𝑙𝑙𝑜 𝑊𝑜𝑟𝑙𝑑', nfkd=True)))
    print(json.dumps(word_tokenize('𝘏𝘦𝘭𝘭𝘰 𝘞𝘰𝘳𝘭𝘥', nfkd=True)))
    print(json.dumps(word_tokenize('𝑯𝒆𝒍𝒍𝒐 𝑾𝒐𝒓𝒍𝒅', nfkd=True)))
    print(json.dumps(word_tokenize('𝙃𝙚𝙡𝙡𝙤 𝙒𝙤𝙧𝙡𝙙', nfkd=True)))
    print(json.dumps(word_tokenize('Ｕｎｉｃｏｄｅ!', replace_ascii=True)))
    print(json.dumps(word_tokenize('🅤🅝🅘🅒🅞🅓🅔‽', replace_ascii=True)))
    print(json.dumps(word_tokenize('🇺‌🇳‌🇮‌🇨‌🇴‌🇩‌🇪!', replace_ascii=True, strip_diacritics=True)))
    print(json.dumps(word_tokenize("   'a   a'a   a'   "
                                   "   ''a   'a'a   'a'   a'a'a   a'a'   a''   "
                                   "   '''a ''a'a 'a''a 'a'a'a a'a'a'a 'a'a' a'a'a' a''a' a'a'' a'''   ",
                                   accept_apostrophe=2)))
