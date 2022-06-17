import json
from typing import List

import regex
import unicodedata

_REGEX_GRAPHEME = regex.compile(r'\X', flags=regex.UNICODE)
_REGEX_WORD_CHAR = regex.compile(r'\w', flags=regex.UNICODE)

#
_ASCII_ALIKE = {'A': 'ÀÁÂÃÄÅĀĂĄǍǞǠǺȀȂȦȺΆΑᴀᴬḀẠẢẤẦẨẪẬẮẰẲẴẶἈἉἊἋἌἍἎἏᾈᾉᾊᾋᾌᾍᾎᾏᾸᾹᾺΆᾼⱯＡ𝐀𝐴𝑨𝒜𝓐𝔄𝔸𝕬𝖠𝗔𝘈𝘼𝙰',
                'B': 'ƁƂɃʙΒᴃᴮᴯḂḄḆℬＢ𝐁𝐵𝑩𝓑𝔅𝔹𝕭𝖡𝗕𝘉𝘽𝙱',
                'C': 'ÇĆĈĊČƇȻʗᴄḈℂℭＣ𝐂𝐶𝑪𝒞𝓒𝕮𝖢𝗖𝘊𝘾𝙲',
                'D': 'ÐĎĐƉƊƋΔᴅᴆᴰḊḌḎḐḒⅅＤ𝐃𝐷𝑫𝒟𝓓𝔇𝔻𝕯𝖣𝗗𝘋𝘿𝙳',
                'E': 'ÈÉÊËĒĔĖĘĚƐȄȆȨɆʚΈΉΕΗᴇᴱᴲḔḖḘḚḜẸẺẼẾỀỂỄỆἘἙἚἛἜἝἨἩἪἫἬἭἮἯᾘᾙᾚᾛᾜᾝᾞᾟῈΈῊΉῌℰＥ𝐄𝐸𝑬𝓔𝔈𝔼𝕰𝖤𝗘𝘌𝙀𝙴',
                'F': 'ƑɸḞℱＦ𝐅𝐹𝑭𝓕𝔉𝔽𝕱𝖥𝗙𝘍𝙁𝙵',
                'G': 'ĜĞĠĢƓƔǤǦǴʛˠΓᴳḠＧ𝐆𝐺𝑮𝒢𝓖𝔊𝔾𝕲𝖦𝗚𝘎𝙂𝙶',
                'H': 'ĤĦȞʜᴴḢḤḦḨḪℋℌℍⱧＨ𝐇𝐻𝑯𝓗𝕳𝖧𝗛𝘏𝙃𝙷',
                'I': 'ÌÍÎÏĨĪĬĮİƖƗǏȈȊɪΊΐΙΪᴵḬḮỈỊἸἹἺἻἼἽἾἿῘῙῚΊℐℑＩ𝐈𝐼𝑰𝓘𝕀𝕴𝖨𝗜𝘐𝙄𝙸',
                'J': 'ĴɈᴊᴶＪ𝐉𝐽𝑱𝒥𝓙𝔍𝕁𝕵𝖩𝗝𝘑𝙅𝙹',
                'K': 'ĶƘǨΚᴋᴷḰḲḴⱩＫ𝐊𝐾𝑲𝒦𝓚𝔎𝕂𝕶𝖪𝗞𝘒𝙆𝙺',
                'L': 'ĹĻĽĿŁȽʟΛᴌᴸḶḸḺḼℒⱠⱢＬ𝐋𝐿𝑳𝓛𝔏𝕃𝕷𝖫𝗟𝘓𝙇𝙻',
                'M': 'ΜᴍᴹḾṀṂℳⱮＭ𝐌𝑀𝑴𝓜𝔐𝕄𝕸𝖬𝗠𝘔𝙈𝙼',
                'N': 'ÑŃŅŇƝǸȠΝᴎᴺᴻṄṆṈṊℕＮ𝐍𝑁𝑵𝒩𝓝𝔑𝕹𝖭𝗡𝘕𝙉𝙽',
                'O': 'ÒÓÔÕÖØŌŎŐƆƟƠǑǪǬǾȌȎȪȬȮȰɷΌΏΟΩᴏᴑᴓᴼṌṎṐṒỌỎỐỒỔỖỘỚỜỞỠỢὈὉὊὋὌὍὨὩὪὫὬὭὮὯᾨᾩᾪᾫᾬᾭᾮᾯῸΌῺΏῼＯ𝐎𝑂𝑶𝒪𝓞𝔒𝕆𝕺𝖮𝗢𝘖𝙊𝙾',
                'P': 'ƤΠᴘᴾṔṖℙⱣＰ𝐏𝑃𝑷𝒫𝓟𝔓𝕻𝖯𝗣𝘗𝙋𝙿',
                'Q': 'ϞℚＱ𝐐𝑄𝑸𝒬𝓠𝔔𝕼𝖰𝗤𝘘𝙌𝚀',
                'R': 'ŔŖŘȐȒɌʀʁΡᴙᴚᴿṘṚṜṞῤῥῬℛℜℝⱤＲ𝐑𝑅𝑹𝓡𝕽𝖱𝗥𝘙𝙍𝚁',
                'S': 'ŚŜŞŠȘʃʅʆΣṠṢṤṦṨẛＳ𝐒𝑆𝑺𝒮𝓢𝔖𝕊𝕾𝖲𝗦𝘚𝙎𝚂',
                'T': 'ŢŤŦƬƮȚȾΤᴛᵀṪṬṮṰＴ𝐓𝑇𝑻𝒯𝓣𝔗𝕋𝕿𝖳𝗧𝘛𝙏𝚃',
                'U': 'ÙÚÛÜŨŪŬŮŰŲƯǓǕǗǙǛȔȖɄʊΎΥΫϒϓϔᴜᵁṲṴṶṸṺỤỦỨỪỬỮỰὙὛὝὟῨῩῪΎＵ𝐔𝑈𝑼𝒰𝓤𝔘𝕌𝖀𝖴𝗨𝘜𝙐𝚄',
                'V': 'ƲˬᴠṼṾＶ𝐕𝑉𝑽𝒱𝓥𝔙𝕍𝖁𝖵𝗩𝘝𝙑𝚅',
                'W': 'ŴƜǷɯɰϜᴡᵂẀẂẄẆẈＷ𝐖𝑊𝑾𝒲𝓦𝔚𝕎𝖂𝖶𝗪𝘞𝙒𝚆',
                'X': 'ẊẌＸ𝐗𝑋𝑿𝒳𝓧𝔛𝕏𝖃𝖷𝗫𝘟𝙓𝚇',
                'Y': 'ÝŶŸƱƳȜȲɎɥʏẎỲỴỶỸＹ𝐘𝑌𝒀𝒴𝓨𝔜𝕐𝖄𝖸𝗬𝘠𝙔𝚈',
                'Z': 'ŹŻŽƵȤʒʓΖᴢẐẒẔℤℨⱫＺ𝐙𝑍𝒁𝒵𝓩𝖅𝖹𝗭𝘡𝙕𝚉',
                'a': 'àáâãäåāăąǎǟǡǻȁȃȧɐɑɒάαᵃᵄᵅḁẚạảấầẩẫậắằẳẵặἀἁἂἃἄἅἆἇὰάᾀᾁᾂᾃᾄᾅᾆᾇᾰᾱᾲᾳᾴᾶᾷₐⱥａ𝐚𝑎𝒂𝒶𝓪𝔞𝕒𝖆𝖺𝗮𝘢𝙖𝚊',
                'b': 'ƀƃɓβϐᵇᵝᵦᵬᶀḃḅḇｂ𝐛𝑏𝒃𝒷𝓫𝔟𝕓𝖇𝖻𝗯𝘣𝙗𝚋',
                'c': 'çćĉċčƈȼɕϲḉｃ𝐜𝑐𝒄𝒸𝓬𝔠𝕔𝖈𝖼𝗰𝘤𝙘𝚌',
                'd': 'ðďđƌƍȡɖɗδᵈᵟᵭᶁḋḍḏḑḓⅆｄ𝐝𝑑𝒅𝒹𝓭𝔡𝕕𝖉𝖽𝗱𝘥𝙙𝚍',
                'e': 'èéêëēĕėęěȅȇȩɇɘɛɜɝɞέήεηᴈᵉᵋᵌḕḗḙḛḝẹẻẽếềểễệἐἑἒἓἔἕἠἡἢἣἤἥἦἧὲέὴήᾐᾑᾒᾓᾔᾕᾖᾗῂῃῄῆῇₑℯⅇｅ𝐞𝑒𝒆𝓮𝔢𝕖𝖊𝖾𝗲𝘦𝙚𝚎',
                'f': 'ƒᵠᵩᵮᶂḟｆ𝐟𝑓𝒇𝒻𝓯𝔣𝕗𝖋𝖿𝗳𝘧𝙛𝚏',
                'g': 'ĝğġģǥǧǵɠɡɢɣγᵍᵞᵧᵷᶃḡℊｇ𝐠𝑔𝒈𝓰𝔤𝕘𝖌𝗀𝗴𝘨𝙜𝚐',
                'h': 'ĥħȟɦɧʮʯʰʱḣḥḧḩḫẖₕⱨｈ𝐡𝒉𝒽𝓱𝔥𝕙𝖍𝗁𝗵𝘩𝙝𝚑',
                'i': 'ìíîïĩīĭįıǐȉȋɨɩίιϊᴉᵎᵢḭḯỉịἰἱἲἳἴἵἶἷὶίιῐῑῒΐῖῗⁱⅈｉ𝐢𝑖𝒊𝒾𝓲𝔦𝕚𝖎𝗂𝗶𝘪𝙞𝚒𝚤',
                'j': 'ĵǰȷɉɟʄʝʲϳⅉｊ𝐣𝑗𝒋𝒿𝓳𝔧𝕛𝖏𝗃𝗷𝘫𝙟𝚓𝚥',
                'k': 'ķĸƙǩʞκϰᵏᶄḱḳḵₖⱪｋ𝐤𝑘𝒌𝓀𝓴𝔨𝕜𝖐𝗄𝗸𝘬𝙠𝚔',
                'l': 'ĺļľŀłƚƛȴɫɬɭˡλᶅḷḹḻḽₗℓⱡｌ𝐥𝑙𝒍𝓁𝓵𝔩𝕝𝖑𝗅𝗹𝘭𝙡𝚕',
                'm': 'ɱμᴟᵐᵚᵯᶆḿṁṃₘｍ𝐦𝑚𝒎𝓂𝓶𝔪𝕞𝖒𝗆𝗺𝘮𝙢𝚖',
                'n': 'ñńņňƞǹȵɲɳɴνᵰᶇṅṇṉṋⁿₙｎ𝐧𝑛𝒏𝓃𝓷𝔫𝕟𝖓𝗇𝗻𝘯𝙣𝚗',
                'o': 'òóôõöøōŏőơǒǫǭǿȍȏȫȭȯȱɔɵοωόώᵒṍṏṑṓọỏốồổỗộớờởỡợὀὁὂὃὄὅὠὡὢὣὤὥὦὧὸόὼώᾠᾡᾢᾣᾤᾥᾦᾧῲῳῴῶῷₒℴｏ𝐨𝑜𝒐𝓸𝔬𝕠𝖔𝗈𝗼𝘰𝙤𝚘',
                'p': 'ƥπϖᵖᵱᵽᶈṕṗₚｐ𝐩𝑝𝒑𝓅𝓹𝔭𝕡𝖕𝗉𝗽𝘱𝙥𝚙',
                'q': 'Ɋɋʠϟｑ𝐪𝑞𝒒𝓆𝓺𝔮𝕢𝖖𝗊𝗾𝘲𝙦𝚚',
                'r': 'ŕŗřȑȓɍɹɺɻɼɽɾɿʳʴʵʶρϱᵣᵨᵲᵳᶉṙṛṝṟｒ𝐫𝑟𝒓𝓇𝓻𝔯𝕣𝖗𝗋𝗿𝘳𝙧𝚛',
                's': 'śŝşšſșȿʂˢςσᵴᶊṡṣṥṧṩₛｓ𝐬𝑠𝒔𝓈𝓼𝔰𝕤𝖘𝗌𝘀𝘴𝙨𝚜',
                't': 'ţťŧƫƭțȶʇʈτᵗᵵṫṭṯṱẗₜⱦｔ𝐭𝑡𝒕𝓉𝓽𝔱𝕥𝖙𝗍𝘁𝘵𝙩𝚝',
                'u': 'ùúûüũūŭůűųưǔǖǘǚǜȕȗɤʉΰυϋύᴝᴞᵘᵙᵤṳṵṷṹṻụủứừửữựὐὑὒὓὔὕὖὗὺύῠῡῢΰῦῧｕ𝐮𝑢𝒖𝓊𝓾𝔲𝕦𝖚𝗎𝘂𝘶𝙪𝚞',
                'v': 'ʋᵛᵥᶌṽṿｖ𝐯𝑣𝒗𝓋𝓿𝔳𝕧𝖛𝗏𝘃𝘷𝙫𝚟',
                'w': 'ŵƿʍʷϝẁẃẅẇẉẘｗ𝐰𝑤𝒘𝓌𝔀𝔴𝕨𝖜𝗐𝘄𝘸𝙬𝚠',
                'x': 'ˣξᶍẋẍₓｘ𝐱𝑥𝒙𝓍𝔁𝔵𝕩𝖝𝗑𝘅𝘹𝙭𝚡',
                'y': 'ýÿŷƴȝȳɏʎʸẏẙỳỵỷỹｙ𝐲𝑦𝒚𝓎𝔂𝔶𝕪𝖞𝗒𝘆𝘺𝙮𝚢',
                'z': 'źżžƶȥɀʐʑζᵶᶎẑẓẕⱬｚ𝐳𝑧𝒛𝓏𝔃𝔷𝕫𝖟𝗓𝘇𝘻𝙯𝚣',
                }
_ASCII_TRANLATION_LOOKUP = {ord(char): alpha for alpha, chars in _ASCII_ALIKE.items() for char in chars}


def _preprocess(text: str,
                nfkd: bool = False,
                casefold: bool = False,
                replace_ascii: bool = False,
                ) -> str:
    # sanity check
    if not isinstance(text, str):
        raise TypeError(f'expected <str>, got <{type(text)}>')

    # pre-process step 1: unicode decomposition
    if nfkd:
        text = f'{unicodedata.normalize("NFKD", text)}\0'
    else:
        text += '\0'

    # pre-process step 2: casefold
    if casefold:
        text = text.casefold()

    # pre-process step 3: replace ascii-like chars
    if replace_ascii:
        text = text.translate(_ASCII_TRANLATION_LOOKUP)

    return text


def tokenize(text: str,
             nfkd: bool = False,
             casefold: bool = False,
             replace_ascii: bool = False,
             strip_diacritics: bool = False,
             ) -> List[str]:
    """
    tokenize text into words
    * enable `nfkd` if you want to do string matching
    * enable `casefold` if you want case-insensitivity
    * enable `replace_ascii` if you want to match ascii strings against ascii-alike text
    * enable `strip_diacritics` if you want to fix zalgo text or want to ignore accents

    warning: if any flags are enabled, the output tokens may not be a substring of the input text

    :param text: to extract words from
    :param nfkd: unicode normal form compatibility decomposition
    :param casefold: lowercase but better
    :param replace_ascii: make ascii-like where possible
    :param strip_diacritics: unwrap graphemes and only keep base char
    :return: list of words
    """

    # pre-process (and sanity check)
    text = _preprocess(text, nfkd=nfkd, casefold=casefold, replace_ascii=replace_ascii)

    # get all word tokens
    tokens = []
    token_buffer = []
    for match in _REGEX_GRAPHEME.finditer(text):
        grapheme = match.group(0)

        # don't count underscore as a word token, despite what the unicode standard says
        if grapheme[0] not in {'_'}:
            if _REGEX_WORD_CHAR.match(grapheme):
                token_buffer.append(grapheme[0] if strip_diacritics else grapheme)
                continue

        # not a word-like grapheme, append current word
        if token_buffer:
            tokens.append(''.join(token_buffer))
            token_buffer.clear()

    return tokens


if __name__ == '__main__':
    print(json.dumps(tokenize('𝐇𝐞𝐥𝐥𝐨 𝐖𝐨𝐫𝐥𝐝')))
    print(json.dumps(tokenize('𝗛𝗲𝗹𝗹𝗼 𝗪𝗼𝗿𝗹𝗱')))
    print(json.dumps(tokenize('𝐻𝑒𝑙𝑙𝑜 𝑊𝑜𝑟𝑙𝑑')))
    print(json.dumps(tokenize('𝘏𝘦𝘭𝘭𝘰 𝘞𝘰𝘳𝘭𝘥')))
    print(json.dumps(tokenize('𝑯𝒆𝒍𝒍𝒐 𝑾𝒐𝒓𝒍𝒅')))
    print(json.dumps(tokenize('𝙃𝙚𝙡𝙡𝙤 𝙒𝙤𝙧𝙡𝙙')))
