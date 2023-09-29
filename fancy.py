import string
from dataclasses import dataclass
from dataclasses import field


@dataclass(frozen=True)
class CharacterMapping:
    translation_table: dict[str, str]
    __inverted_translation_table: dict[str, str] = field(default_factory=dict, init=False, repr=False)

    __cached_maketrans: dict[int, str] = field(default_factory=dict, init=False, repr=False)
    __cached_inverted_maketrans: dict[int, str] = field(default_factory=dict, init=False, repr=False)

    def __post_init__(self):
        # sanity checks
        assert isinstance(self.translation_table, dict)
        assert all(isinstance(k, str) for k in self.translation_table.keys())
        assert all(len(k) > 0 for k in self.translation_table.keys())
        assert all(isinstance(v, str) for v in self.translation_table.values())

        # invert the translation table
        for k, v in self.translation_table.items():
            if v:
                self.__inverted_translation_table.setdefault(v, k)

        # maketrans since str.translate is more efficient
        if all(len(k) == 1 for k in self.translation_table):
            self.__cached_maketrans.update(str.maketrans(self.translation_table))
        if all(len(k) == 1 for k in self.__inverted_translation_table):
            self.__cached_inverted_maketrans.update(str.maketrans(self.__inverted_translation_table))

    def from_ascii(self, text: str) -> str:
        if self.__cached_maketrans:
            return text.translate(self.__cached_maketrans)
        if self.translation_table:
            return self._translate(text, self.translation_table)
        return text

    def to_ascii(self, text: str) -> str:
        if self.__cached_inverted_maketrans:
            return text.translate(self.__cached_inverted_maketrans)
        if self.__inverted_translation_table:
            return self._translate(text, self.__inverted_translation_table)
        return text

    @staticmethod
    def _translate(text: str, translation_table: dict[str, str]) -> str:
        lengths = sorted(set(len(k) for k in translation_table), reverse=True)
        assert all(lengths)  # should never end up with a zero length

        out = []
        cursor = 0
        while cursor < len(text):
            for l in lengths:
                if cursor + l > len(text):
                    continue  # technically this check is unnecessary since it'll still behave correctly
                if text[cursor:cursor + l] in translation_table:
                    out.append(translation_table[text[cursor:cursor + l]])
                    cursor += l
                    break
            else:
                out.append(text[cursor])
                cursor += 1
        return ''.join(out)


def mapping(
        upper: str | list[str] | None = None,
        lower: str | list[str] | None = None,
        digit: str | list[str] | None = None,
        ascii: str | list[str] | None = None,
        chars: str | list[str] | None = None,
        *,
        # remove: str | None = None,
        other: dict[str, str] | None = None,
        mirror_missing_case: bool = True,
) -> CharacterMapping:
    # todo: special handling for whitespace?
    _mapping = dict()
    if upper:
        assert all(isinstance(x, str) for x in upper)
        assert len(upper) == 26
        _mapping.update(dict(zip('ABCDEFGHIJKLMNOPQRSTUVWXYZ', upper)))
        if not lower and mirror_missing_case:
            _mapping.update(dict(zip('abcdefghijklmnopqrstuvwxyz', upper)))
    if lower:
        assert all(isinstance(x, str) for x in lower)
        assert len(lower) == 26
        _mapping.update(dict(zip('abcdefghijklmnopqrstuvwxyz', lower)))
        if not upper and mirror_missing_case:
            _mapping.update(dict(zip('ABCDEFGHIJKLMNOPQRSTUVWXYZ', lower)))
    if digit:
        assert all(isinstance(x, str) for x in digit)
        assert len(digit) == 10
        _mapping.update(dict(zip('0123456789', digit)))

    if ascii or chars:
        assert all(isinstance(x, str) for x in ascii)
        assert all(isinstance(x, str) for x in chars)
        assert len(ascii) == len(chars)
        _mapping.update(dict(zip(ascii, chars)))
    if other:
        assert isinstance(other, dict)
        assert all(isinstance(k, str) for k in other)
        assert all(len(k) == 1 for k in other)
        _mapping.update(other)

    if not _mapping:
        raise ValueError('no input')

    return CharacterMapping(translation_table=_mapping)


mappings = {
    # https://unicode.org/charts/PDF/UFF00.pdf
    'Fullwidth':                 mapping(
        'ＡＢＣＤＥＦＧＨＩＪＫＬＭＮＯＰＱＲＳＴＵＶＷＸＹＺ',  # Fullwidth Latin Capital Letter
        'ａｂｃｄｅｆｇｈｉｊｋｌｍｎｏｐｑｒｓｔｕｖｗｘｙｚ',  # Fullwidth Latin Small Letter
        '０１２３４５６７８９',
        " !\"#$%&'()*+,-./:;<=>?@[\\]^_`{|}~¢£¥",
        " ！＂＃＄％＆＇（）＊＋，－．／：；＜＝＞？＠［＼］＾＿｀｛｜｝～￠￡￥"),

    # https://unicode.org/charts/PDF/U1D400.pdf
    # todo: support greek/cyrillic chars too
    'Bold':                      mapping(
        '𝐀𝐁𝐂𝐃𝐄𝐅𝐆𝐇𝐈𝐉𝐊𝐋𝐌𝐍𝐎𝐏𝐐𝐑𝐒𝐓𝐔𝐕𝐖𝐗𝐘𝐙',  # Mathematical Bold Capital
        '𝐚𝐛𝐜𝐝𝐞𝐟𝐠𝐡𝐢𝐣𝐤𝐥𝐦𝐧𝐨𝐩𝐪𝐫𝐬𝐭𝐮𝐯𝐰𝐱𝐲𝐳',  # Mathematical Bold Small
        '𝟎𝟏𝟐𝟑𝟒𝟓𝟔𝟕𝟖𝟗'),  # Mathematical Bold Digit
    'Italic':                    mapping(
        '𝐴𝐵𝐶𝐷𝐸𝐹𝐺𝐻𝐼𝐽𝐾𝐿𝑀𝑁𝑂𝑃𝑄𝑅𝑆𝑇𝑈𝑉𝑊𝑋𝑌𝑍',  # Mathematical Italic Capital
        '𝑎𝑏𝑐𝑑𝑒𝑓𝑔ℎ𝑖𝑗𝑘𝑙𝑚𝑛𝑜𝑝𝑞𝑟𝑠𝑡𝑢𝑣𝑤𝑥𝑦𝑧'),  # Mathematical Italic Small (with planck constant)
    'Bold Italic':               mapping(
        '𝑨𝑩𝑪𝑫𝑬𝑭𝑮𝑯𝑰𝑱𝑲𝑳𝑴𝑵𝑶𝑷𝑸𝑹𝑺𝑻𝑼𝑽𝑾𝑿𝒀𝒁',  # Mathematical Bold Italic Capital
        '𝒂𝒃𝒄𝒅𝒆𝒇𝒈𝒉𝒊𝒋𝒌𝒍𝒎𝒏𝒐𝒑𝒒𝒓𝒔𝒕𝒖𝒗𝒘𝒙𝒚𝒛'),  # Mathematical Bold Italic Small
    'Script':                    mapping(
        '𝒜ℬ𝒞𝒟ℰℱ𝒢ℋℐ𝒥𝒦ℒℳ𝒩𝒪𝒫𝒬ℛ𝒮𝒯𝒰𝒱𝒲𝒳𝒴𝒵',  # Mathematical Script Capital
        '𝒶𝒷𝒸𝒹ℯ𝒻ℊ𝒽𝒾𝒿𝓀𝓁𝓂𝓃ℴ𝓅𝓆𝓇𝓈𝓉𝓊𝓋𝓌𝓍𝓎𝓏'),  # Mathematical Script Small
    'Bold Script':               mapping(
        '𝓐𝓑𝓒𝓓𝓔𝓕𝓖𝓗𝓘𝓙𝓚𝓛𝓜𝓝𝓞𝓟𝓠𝓡𝓢𝓣𝓤𝓥𝓦𝓧𝓨𝓩',  # Mathematical Bold Script Capital
        '𝓪𝓫𝓬𝓭𝓮𝓯𝓰𝓱𝓲𝓳𝓴𝓵𝓶𝓷𝓸𝓹𝓺𝓻𝓼𝓽𝓾𝓿𝔀𝔁𝔂𝔃'),  # Mathematical Bold Script Small
    'Fraktur':                   mapping(
        '𝔄𝔅ℭ𝔇𝔈𝔉𝔊ℌℑ𝔍𝔎𝔏𝔐𝔑𝔒𝔓𝔔ℜ𝔖𝔗𝔘𝔙𝔚𝔛𝔜ℨ',  # Mathematical Fraktur Capital
        '𝔞𝔟𝔠𝔡𝔢𝔣𝔤𝔥𝔦𝔧𝔨𝔩𝔪𝔫𝔬𝔭𝔮𝔯𝔰𝔱𝔲𝔳𝔴𝔵𝔶𝔷'),  # Mathematical Fraktur Small
    'Bold Fraktur':              mapping(
        '𝕬𝕭𝕮𝕯𝕰𝕱𝕲𝕳𝕴𝕵𝕶𝕷𝕸𝕹𝕺𝕻𝕼𝕽𝕾𝕿𝖀𝖁𝖂𝖃𝖄𝖅',  # Mathematical Bold Fraktur Capital
        '𝖆𝖇𝖈𝖉𝖊𝖋𝖌𝖍𝖎𝖏𝖐𝖑𝖒𝖓𝖔𝖕𝖖𝖗𝖘𝖙𝖚𝖛𝖜𝖝𝖞𝖟'),  # Mathematical Bold Fraktur Small
    'Double-Struck':             mapping(
        '𝔸𝔹ℂ𝔻𝔼𝔽𝔾ℍ𝕀𝕁𝕂𝕃𝕄ℕ𝕆ℙℚℝ𝕊𝕋𝕌𝕍𝕎𝕏𝕐ℤ',  # Mathematical Double-Struck Capital
        '𝕒𝕓𝕔𝕕𝕖𝕗𝕘𝕙𝕚𝕛𝕜𝕝𝕞𝕟𝕠𝕡𝕢𝕣𝕤𝕥𝕦𝕧𝕨𝕩𝕪𝕫',  # Mathematical Double-Struck Small
        '𝟘𝟙𝟚𝟛𝟜𝟝𝟞𝟟𝟠𝟡',  # Mathematical Double-Struck Digit
        ';:()|[]', '⨟⦂⦇⦈⫿⟦⟧'),
    'Sans-Serif':                mapping(
        '𝖠𝖡𝖢𝖣𝖤𝖥𝖦𝖧𝖨𝖩𝖪𝖫𝖬𝖭𝖮𝖯𝖰𝖱𝖲𝖳𝖴𝖵𝖶𝖷𝖸𝖹',  # Mathematical Sans-Serif Capital
        '𝖺𝖻𝖼𝖽𝖾𝖿𝗀𝗁𝗂𝗃𝗄𝗅𝗆𝗇𝗈𝗉𝗊𝗋𝗌𝗍𝗎𝗏𝗐𝗑𝗒𝗓',  # Mathematical Sans-Serif Small
        '𝟢𝟣𝟤𝟥𝟦𝟧𝟨𝟩𝟪𝟫'),  # Mathematical Sans-Serif Digit
    'Sans-Serif Bold':           mapping(
        '𝗔𝗕𝗖𝗗𝗘𝗙𝗚𝗛𝗜𝗝𝗞𝗟𝗠𝗡𝗢𝗣𝗤𝗥𝗦𝗧𝗨𝗩𝗪𝗫𝗬𝗭',  # Mathematical Sans-Serif Bold Capital
        '𝗮𝗯𝗰𝗱𝗲𝗳𝗴𝗵𝗶𝗷𝗸𝗹𝗺𝗻𝗼𝗽𝗾𝗿𝘀𝘁𝘂𝘃𝘄𝘅𝘆𝘇',  # Mathematical Sans-Serif Bold Small
        '𝟬𝟭𝟮𝟯𝟰𝟱𝟲𝟳𝟴𝟵'),  # Mathematical Sans-Serif Bold Digit
    'Sans-Serif Italic':         mapping(
        '𝘈𝘉𝘊𝘋𝘌𝘍𝘎𝘏𝘐𝘑𝘒𝘓𝘔𝘕𝘖𝘗𝘘𝘙𝘚𝘛𝘜𝘝𝘞𝘟𝘠𝘡',  # Mathematical Sans-Serif Italic Capital
        '𝘢𝘣𝘤𝘥𝘦𝘧𝘨𝘩𝘪𝘫𝘬𝘭𝘮𝘯𝘰𝘱𝘲𝘳𝘴𝘵𝘶𝘷𝘸𝘹𝘺𝘻'),  # Mathematical Sans-Serif Italic Small
    'Sans-Serif Bold Italic':    mapping(
        '𝘼𝘽𝘾𝘿𝙀𝙁𝙂𝙃𝙄𝙅𝙆𝙇𝙈𝙉𝙊𝙋𝙌𝙍𝙎𝙏𝙐𝙑𝙒𝙓𝙔𝙕',  # Mathematical Sans-Serif Bold Italic Capital
        '𝙖𝙗𝙘𝙙𝙚𝙛𝙜𝙝𝙞𝙟𝙠𝙡𝙢𝙣𝙤𝙥𝙦𝙧𝙨𝙩𝙪𝙫𝙬𝙭𝙮𝙯'),  # Mathematical Sans-Serif Bold Italic Small
    'Monospace':                 mapping(
        '𝙰𝙱𝙲𝙳𝙴𝙵𝙶𝙷𝙸𝙹𝙺𝙻𝙼𝙽𝙾𝙿𝚀𝚁𝚂𝚃𝚄𝚅𝚆𝚇𝚈𝚉',  # Mathematical Monospace Capital
        '𝚊𝚋𝚌𝚍𝚎𝚏𝚐𝚑𝚒𝚓𝚔𝚕𝚖𝚗𝚘𝚙𝚚𝚛𝚜𝚝𝚞𝚟𝚠𝚡𝚢𝚣',  # Mathematical Monospace Small
        '𝟶𝟷𝟸𝟹𝟺𝟻𝟼𝟽𝟾𝟿'),  # Mathematical Monospace Digit

    # '⓵⓶⓷⓸⓹⓺⓻⓼⓽'  # Double Circled Digit (missing zero)
    'Circled':                   mapping(
        'ⒶⒷⒸⒹⒺⒻⒼⒽⒾⒿⓀⓁⓂⓃⓄⓅⓆⓇⓈⓉⓊⓋⓌⓍⓎⓏ',  # Circled Latin Capital Letter
        'ⓐⓑⓒⓓⓔⓕⓖⓗⓘⓙⓚⓛⓜⓝⓞⓟⓠⓡⓢⓣⓤⓥⓦⓧⓨⓩ',  # Circled Latin Small Letter
        '⓪①②③④⑤⑥⑦⑧⑨',  # Circled Digit
        ' +', '◯⨁'),
    'Squared Latin':             mapping(
        '🄰🄱🄲🄳🄴🄵🄶🄷🄸🄹🄺🄻🄼🄽🄾🄿🅀🅁🅂🅃🅄🅅🅆🅇🅈🅉'),  # Squared Latin Capital Letter ⊡
    'Negative Circled':          mapping(
        '🅐🅑🅒🅓🅔🅕🅖🅗🅘🅙🅚🅛🅜🅝🅞🅟🅠🅡🅢🅣🅤🅥🅦🅧🅨🅩',  # Negative Circled Latin Capital Letter
        digit='⓿❶❷❸❹❺❻❼❽❾'),  # Dingbat Negative Circled Digit
    'Negative Squared':          mapping(
        '🅰🅱🅲🅳🅴🅵🅶🅷🅸🅹🅺🅻🅼🅽🅾🅿🆀🆁🆂🆃🆄🆅🆆🆇🆈🆉',  # Negative Squared Latin Capital Letter
        other={'?': '🯄'}),
    'Parenthesized':             mapping(
        '🄐🄑🄒🄓🄔🄕🄖🄗🄘🄙🄚🄛🄜🄝🄞🄟🄠🄡🄢🄣🄤🄥🄦🄧🄨🄩',  # Parenthesized Latin Capital Letter
        '⒜⒝⒞⒟⒠⒡⒢⒣⒤⒥⒦⒧⒨⒩⒪⒫⒬⒭⒮⒯⒰⒱⒲⒳⒴⒵',  # Parenthesized Latin Small Letter
        '㈇⑴⑵⑶⑷⑸⑹⑺⑻⑼'),  # Parenthesized Digit (plus hangul ieung)

    # https://rupertshepherd.info/resource_pages/superscript-letters-in-unicode
    # https://en.wikipedia.org/wiki/Unicode_subscripts_and_superscripts
    # https://unicode.org/charts/PDF/U1D80.pdf
    # https://unicode.org/charts/PDF/U1D00.pdf
    'superscript':               mapping(
        'ᴬᴮꟲᴰᴱꟳᴳᴴᴵᴶᴷᴸᴹᴺᴼᴾꟴᴿˢᵀᵁⱽᵂᵡʏᶻ',  # missing S,Z inserted from lowercase, X from greek
        'ᵃᵇᶜᵈᵉᶠᵍʰⁱʲᵏˡᵐⁿᵒᵖ𐞥ʳˢᵗᵘᵛʷˣʸᶻ',
        '⁰¹²³⁴⁵⁶⁷⁸⁹',  # ꝰ
        '!~Æœ+-=()', 'ꜝ῀ᴭꟹ⁺⁻⁼⁽⁾'),

    # either ZWNJ or ZWSP work, but people are more wary of ZWSP nowadays
    # ZWNJ example: 🇭‌🇪‌🇱‌🇱‌🇴‌ 🇼‌🇴‌🇷‌🇱‌🇩‌!
    # ZWSP example: 🇭​🇪​🇱​🇱​🇴​ 🇼​🇴​🇷​🇱​🇩​!
    'Regional Indicator Symbol': mapping(
        [f'{x}\u200C' for x in '🇦🇧🇨🇩🇪🇫🇬🇭🇮🇯🇰🇱🇲🇳🇴🇵🇶🇷🇸🇹🇺🇻🇼🇽🇾🇿']),  # Regional Indicator Symbol Letter + ZWNJ

    # https://www.compart.com/en/unicode/search?q=reversed#characters
    'reversed':                  mapping(
        'AᗺƆᗡƎꟻວHIᒐꓘ⅃MИOꟼϘЯƧTUVWXYZ',  # Ↄ
        'ɒdɔbɘʇ𝼁ʜiįʞlmnoqpɿƨtυvwxγz',
        '', ';?,~', '⁏⸮⹁∽'),
    'small caps':                mapping('ᴀʙᴄᴅᴇꜰɢʜɪᴊᴋʟᴍɴᴏᴘǫʀsᴛᴜᴠᴡxʏᴢ'),

    # https://unicode.org/charts/PDF/U0530.pdf
    'armenian':                  mapping('ԹՅՇԺȝԲԳիɿʝƙԼʍըՕբզՐՖԵՄVաՃկչ'),
    # https://unicode.org/charts/PDF/U0370.pdf
    'greek':                     mapping('', 'αβͼ∂εϝςϟιϳκλмησρϙͱϛϯμνωχγζ'),  # and a bit of coptic
    # https://unicode.org/charts/PDF/U4E00.pdf
    # https://unicode.org/charts/PDF/U3400.pdf
    # https://unicode.org/charts/PDF/U20000.pdf
    # https://unicode.org/charts/PDF/U2A700.pdf
    # https://unicode.org/charts/PDF/U2B820.pdf
    # https://unicode.org/charts/PDF/U2CEB0.pdf
    # https://unicode.org/charts/PDF/U30000.pdf
    # https://unicode.org/charts/PDF/U31350.pdf
    # https://unicode.org/charts/PDF/U2EBF0.pdf
    # https://unicode.org/charts/PDF/UF900.pdf
    # https://unicode.org/charts/PDF/U2F800.pdf
    # https://unicode.org/charts/PDF/U2F00.pdf
    # https://unicode.org/charts/PDF/U2E80.pdf
    # https://unicode.org/charts/PDF/U31C0.pdf
    # https://unicode.org/charts/PDF/U2FF0.pdf
    'chinese':                   mapping('卂乃匚ᗪ乇千Ꮆ卄丨了长乚爪几口卩Ɋ尺丂ㄒㄩ丷山乂ㄚ乙'),  # 力
    # ++ 艹
    # A 𠔼
    # B ⻖⻏ 阝㠯
    # BB 𨸙
    # BE 𮤹
    # BI 𨸖
    # C 匚 匸 𠥓
    # CO 叵
    # e ⺋
    # E 幺 纟㭅 𬼖 U+30004
    # G 包 𠃚 𠫔 𭅲 㔾
    # g 𢎘
    # I 工
    # i 讠
    # II U+2EBF0
    # ij ⺉
    # IJ 刂
    # IJ 𢀕
    # IL 𠃖
    # it 计
    # iT 订
    # j ⼃ ⼅
    # jil 川
    # JJ U+30052
    # JL 儿
    # K U+30020
    # K 飞
    # L U+3136B
    # l ⼁
    # L 𠃊㇗㇄
    # LJ 𠄍
    # LL 𠃏
    # NL 劜
    # O ⼝ ⼞ ㇣
    # oc 𫩔
    # OE 吆
    # OI 叿
    # oij 𠮧
    # ojil 𠯀
    # ol 𠮝
    # ON 叽 叻
    # OO 吅
    # OOO 品
    # OP 叩
    # os 𫩐
    # OT 吓 叮
    # ot 𠮟
    # OY 吖
    # OZ 𠮙
    # P ⼫ 尸 户
    # TB 邒
    # U 凹 U+2F81D ⼐
    # WB 屷
    # WI 屸
    # X 㐅
    # y 𬼀
    # YP 𠨍
    # yy 𫡅
    # z ㇊ ㇠
    # ZZ 𠃐
    # 彐 灬 门𠆢 𡿨

    # https://unicode.org/charts/PDF/U16A0.pdf
    'runic':                     mapping('ABCDEFGHIJKLMNOPQRSTUVWXYZ'),

    # A ᚢ ᚣ ᚤ ᛟ
    # B ᛒ ᛔ
    # C ᚲ ᛈ
    # D ᚦ ᚧ
    # E ᛊ
    # F ᚨ ᚩ ᚪ ᚫ
    # G
    # H ᚳ ᚺ ᚻ
    # I ᛁ ᛂ ᛨ ᛧ
    # J
    # K ᛕ
    # L ᚳ
    # M ᛖ ᛗ
    # N ᛲ
    # O ᛃ ᛥ ᛜ
    # P ᚹ
    # Q ᛩ ᛰ
    # R ᚱ
    # S ᛇ ᛢ
    # T ᛏ
    # U
    # V
    # W ᛠ
    # X ᚷ ᚸ ᛤ ᛶ ᛞ
    # Y ᚠ ᚴ ᚵ ᚶ ᛉ
    # Z
    # ᚼ ᚽ ᚾ ᛀ ᛋ ᛡ ᛬ ᛫ ᛭

    # https://unicode.org/charts/PDF/U13A0.pdf
    # https://unicode.org/charts/PDF/UAB70.pdf
    'cherokee':                  None,

    # promising
    # https://unicode.org/charts/PDF/U11AC0.pdf
    # https://unicode.org/charts/PDF/U16B00.pdf
    # https://unicode.org/charts/PDF/U2C80.pdf
    # https://unicode.org/charts/PDF/U10300.pdf
    # https://unicode.org/charts/PDF/U102A0.pdf

    # https://github.com/Secret-chest/fancify-text/blob/main/fancify_text/fontData.py
    'curly':                     mapping('ąცƈɖɛʄɠɧıʝƙƖɱŋơ℘զཞʂɬų۷ῳҳყʑ'),
    'currency':                  mapping('₳₿¢₫€₣₲HIJ₭£₥₦O₱QR$₮UV₩X¥₴'),
    'cool':                      mapping('ᗩᗷᑕᗪEᖴGᕼIᒍKᒪᗰᑎOᑭᑫᖇᔕTᑌᐯᗯ᙭Yᘔ'),
    'magic':                     mapping('αႦƈԃҽϝɠԋιʝƙʅɱɳσρϙɾʂƚυʋɯxყȥ'),
    'upside down':               mapping('∀ᗺϽᗡƎℲƃHIſꓘ˥WNOԀQᴚS⊥∩ΛMXʎZ',  # ⱯᗺƆᗡƎℲ⅁HIᒋꓘ⅂ꟽNOԀტᴚSꞱՈΛM X⅄Z
                                         'ɐqɔpǝɟƃɥ!ɾʞןɯuodbɹsʇnʌʍxʎz',  # ɐqɔpǝɟɓɥᴉſʞlɯuodbɹsʇnʌʍxʎz
                                         '', '.!?', '˙¡¿'),

    # https://unicode.org/charts/PDF/UA000.pdf
    # https://unicode.org/charts/PDF/UA490.pdf
    'squiggle 1':                mapping('ꍏꌃꉓꀸꍟꎇꁅꃅꀤꀭꀘ꒒ꂵꈤꂦꉣꆰꋪꌗ꓄ꀎꃴꅏꊼꌩꁴ'),
    'squiggle 2':                mapping('ꋬꃳꉔ꒯ꏂꊰꍌꁝ꒐꒻ꀘ꒒ꂵꋊꄲꉣꆰꋪꇙ꓄꒤꒦ꅐꉧꌦꁴ'),
    'squiggle 3':                mapping('ꋫꃃꏸꁕꍟꄘꁍꑛꂑꀭꀗ꒒ꁒꁹꆂꉣꁸ꒓ꌚ꓅ꐇꏝꅐꇓꐟꁴ'),
    'squiggle 4':                mapping('ꍏꌃꉓꀸꍟꎇꁅꃅꀤꀭꀘ꒒ꂵꈤꂦꉣꆰꋪꌗ꓄ꀎꃴꅏꊼꌩꁴ'),

    # https://www.compart.com/en/unicode/search?q=Old+Italic+Letter#characters
    'old italic':                mapping('𐌀𐌁𐌂𐌃𐌄𐌅Ᏽ𐋅𐌉Ꮭ𐌊𐌋𐌌𐌍Ꝋ𐌐𐌒𐌓𐌔𐌕𐌵ᕓᏔ𐋄𐌙Ɀ'),
    'old italic 2':              mapping('𐌀𐌁𐌂𐌃𐌄𐌅Ɠ𐋅𐌉Ɉ𐌊𐌋𐌌𐌍Ꝋ𐌐𐌒Ɽ𐌔𐌕𐌵ƲᏔ𐋄𐌙Ɀ'),
}

# A͟B͟C͟D͟E͟F͟G͟H͟I͟J͟K͟L͟M͟N͟O͟P͟Q͟R͟S͟T͟U͟V͟W͟X͟Y͟Z͟  a͟b͟c͟d͟e͟f͟g͟h͟i͟j͟k͟l͟m͟n͟o͟p͟q͟r͟s͟t͟u͟v͟w͟x͟y͟z͟

if __name__ == '__main__':
    # m = mappings['Regional Indicator Symbol']
    m = mappings['wiry']
    print(m)
    print(m.from_ascii('Hello world!'))
    print(m.to_ascii(m.from_ascii('Hello world!')))

# https://github.com/Secret-chest/fancify-text/blob/main/fancify_text/fontData.py
modifiers = {
    'slash':                   '̷',
    'longSlash':               '̸',
    'bridgeBelow':             '̺',
    'tilde':                   '̃',
    'dotAbove':                '̇',
    'diaeresis':               '̈',
    'verticalLineAbove':       '̍',
    'square':                  '⃞',
    'diamond':                 '⃟',
    'noSign':                  '⃠',
    'lrArrowAbove':            '⃡',
    'screen':                  '⃢',
    'triangle':                '⃤',
    'backslash':               '⃥',
    'doubleStroke':            '⃦',
    'annuity':                 '⃧',
    '3DotsBelow':              '⃨',
    'wideBridge':              '⃩',
    'doubleSlash':             '⃫',
    'leftArrowBelow':          '⃮',
    'rightArrowBelow':         '⃯',
    'asteriskAbove':           '⃰',
    'verticalLine':            '⃒',
    'shortVerticalLine':       '⃓',
    'ccwArrowAbove':           '⃔',
    'cwArrowAbove':            '⃕',
    'leftArrowAbove':          '⃖',
    'rightArrowAbove':         '⃗',
    'ring':                    '⃘',
    '3DotsAbove':              '⃛',
    '4DotsAbove':              '⃜',
    'grave':                   '̀',
    'acute':                   '́',
    'circumflex':              '̂',
    'breve':                   '̆',
    'hookAbove':               '̉',
    'ringAbove':               '̊',
    'doubleAcute':             '̋',
    'caron':                   '̌',
    'vzmet':                   '꙯',
    'tenMillionStars':         '꙰',
    'encasing':                '꙱',
    'billionSign':             '꙲',
    'seagull':                 '̼',
    'x':                       '̽',
    'verticalTilde':           '̾',
    'doubleOverline':          '̿',
    'overline':                '̅',
    'doubleVerticalLineBelow': '͈',
    'almostEqualAbove':        '͌',
    'lrArrowBelow':            '͍',
    'upwardArrowBelow':        '͎',
    'rightArrowhead':          '͐',
    'doubleTilde':             '͠',
    'underline':               '̲',
    'doubleUnderline':         '̳',
    'strikeShort':             '̵',
    'strike':                  '̶',
    'equalsSign':              '͇',
# }
#
# # https://www.unicode.org/L2/L2020/20275r-math-calligraphic.pdf
# ''.join(
#     '\U0001D49C\uFE00'  # MATHEMATICAL CHANCERY CAPITAL A
#     '\U0000212C\uFE00'  # MATHEMATICAL CHANCERY CAPITAL B
#     '\U0001D49E\uFE00'  # MATHEMATICAL CHANCERY CAPITAL C
#     '\U0001D49F\uFE00'  # MATHEMATICAL CHANCERY CAPITAL D
#     '\U00002130\uFE00'  # MATHEMATICAL CHANCERY CAPITAL E
#     '\U00002131\uFE00'  # MATHEMATICAL CHANCERY CAPITAL F
#     '\U0001D4A2\uFE00'  # MATHEMATICAL CHANCERY CAPITAL G
#     '\U0000210B\uFE00'  # MATHEMATICAL CHANCERY CAPITAL H
#     '\U00002110\uFE00'  # MATHEMATICAL CHANCERY CAPITAL I
#     '\U0001D4A5\uFE00'  # MATHEMATICAL CHANCERY CAPITAL J
#     '\U0001D4A6\uFE00'  # MATHEMATICAL CHANCERY CAPITAL K
#     '\U00002112\uFE00'  # MATHEMATICAL CHANCERY CAPITAL L
#     '\U00002133\uFE00'  # MATHEMATICAL CHANCERY CAPITAL M
#     '\U0001D4A9\uFE00'  # MATHEMATICAL CHANCERY CAPITAL N
#     '\U0001D4AA\uFE00'  # MATHEMATICAL CHANCERY CAPITAL O
#     '\U0001D4AB\uFE00'  # MATHEMATICAL CHANCERY CAPITAL P
#     '\U0001D4AC\uFE00'  # MATHEMATICAL CHANCERY CAPITAL Q
#     '\U0000211B\uFE00'  # MATHEMATICAL CHANCERY CAPITAL R
#     '\U0001D4AE\uFE00'  # MATHEMATICAL CHANCERY CAPITAL S
#     '\U0001D4AF\uFE00'  # MATHEMATICAL CHANCERY CAPITAL T
#     '\U0001D4B0\uFE00'  # MATHEMATICAL CHANCERY CAPITAL U
#     '\U0001D4B1\uFE00'  # MATHEMATICAL CHANCERY CAPITAL V
#     '\U0001D4B2\uFE00'  # MATHEMATICAL CHANCERY CAPITAL W
#     '\U0001D4B3\uFE00'  # MATHEMATICAL CHANCERY CAPITAL X
#     '\U0001D4B4\uFE00'  # MATHEMATICAL CHANCERY CAPITAL Y
#     '\U0001D4B5\uFE00'  # MATHEMATICAL CHANCERY CAPITAL Z
# )
# ''.join(
#     '\U0001D49C\uFE01'  # MATHEMATICAL ROUNDHAND CAPITAL A
#     '\U0000212C\uFE01'  # MATHEMATICAL ROUNDHAND CAPITAL B
#     '\U0001D49E\uFE01'  # MATHEMATICAL ROUNDHAND CAPITAL C
#     '\U0001D49F\uFE01'  # MATHEMATICAL ROUNDHAND CAPITAL D
#     '\U00002130\uFE01'  # MATHEMATICAL ROUNDHAND CAPITAL E
#     '\U00002131\uFE01'  # MATHEMATICAL ROUNDHAND CAPITAL F
#     '\U0001D4A2\uFE01'  # MATHEMATICAL ROUNDHAND CAPITAL G
#     '\U0000210B\uFE01'  # MATHEMATICAL ROUNDHAND CAPITAL H
#     '\U00002110\uFE01'  # MATHEMATICAL ROUNDHAND CAPITAL I
#     '\U0001D4A5\uFE01'  # MATHEMATICAL ROUNDHAND CAPITAL J
#     '\U0001D4A6\uFE01'  # MATHEMATICAL ROUNDHAND CAPITAL K
#     '\U00002112\uFE01'  # MATHEMATICAL ROUNDHAND CAPITAL L
#     '\U00002133\uFE01'  # MATHEMATICAL ROUNDHAND CAPITAL M
#     '\U0001D4A9\uFE01'  # MATHEMATICAL ROUNDHAND CAPITAL N
#     '\U0001D4AA\uFE01'  # MATHEMATICAL ROUNDHAND CAPITAL O
#     '\U0001D4AB\uFE01'  # MATHEMATICAL ROUNDHAND CAPITAL P
#     '\U0001D4AC\uFE01'  # MATHEMATICAL ROUNDHAND CAPITAL Q
#     '\U0000211B\uFE01'  # MATHEMATICAL ROUNDHAND CAPITAL R
#     '\U0001D4AE\uFE01'  # MATHEMATICAL ROUNDHAND CAPITAL S
#     '\U0001D4AF\uFE01'  # MATHEMATICAL ROUNDHAND CAPITAL T
#     '\U0001D4B0\uFE01'  # MATHEMATICAL ROUNDHAND CAPITAL U
#     '\U0001D4B1\uFE01'  # MATHEMATICAL ROUNDHAND CAPITAL V
#     '\U0001D4B2\uFE01'  # MATHEMATICAL ROUNDHAND CAPITAL W
#     '\U0001D4B3\uFE01'  # MATHEMATICAL ROUNDHAND CAPITAL X
#     '\U0001D4B4\uFE01'  # MATHEMATICAL ROUNDHAND CAPITAL Y
#     '\U0001D4B5\uFE01'  # MATHEMATICAL ROUNDHAND CAPITAL Z
# )
# string.ascii_uppercase
