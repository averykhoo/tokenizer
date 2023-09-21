# https://unicode.org/charts/PDF/U1D400.pdf
s = (
    # '⓵⓶⓷⓸⓹⓺⓻⓼⓽'  # Double Circled Digit (missing zero)

    'ⒶⒷⒸⒹⒺⒻⒼⒽⒾⒿⓀⓁⓂⓃⓄⓅⓆⓇⓈⓉⓊⓋⓌⓍⓎⓏ'  # Circled Latin Capital Letter
    'ⓐⓑⓒⓓⓔⓕⓖⓗⓘⓙⓚⓛⓜⓝⓞⓟⓠⓡⓢⓣⓤⓥⓦⓧⓨⓩ'  # Circled Latin Small Letter 
    '⓪①②③④⑤⑥⑦⑧⑨'  # Circled Digit

    'ＡＢＣＤＥＦＧＨＩＪＫＬＭＮＯＰＱＲＳＴＵＶＷＸＹＺ'  # Fullwidth Latin Capital Letter 
    'ａｂｃｄｅｆｇｈｉｊｋｌｍｎｏｐｑｒｓｔｕｖｗｘｙｚ'  # Fullwidth Latin Small Letter 

    # https://unicode.org/charts/PDF/U2700.pdf
    '𝐀𝐁𝐂𝐃𝐄𝐅𝐆𝐇𝐈𝐉𝐊𝐋𝐌𝐍𝐎𝐏𝐐𝐑𝐒𝐓𝐔𝐕𝐖𝐗𝐘𝐙'  # Mathematical Bold Capital
    '𝐚𝐛𝐜𝐝𝐞𝐟𝐠𝐡𝐢𝐣𝐤𝐥𝐦𝐧𝐨𝐩𝐪𝐫𝐬𝐭𝐮𝐯𝐰𝐱𝐲𝐳'  # Mathematical Bold Small
    '𝟎𝟏𝟐𝟑𝟒𝟓𝟔𝟕𝟖𝟗'  # Mathematical Bold Digit

    '𝐴𝐵𝐶𝐷𝐸𝐹𝐺𝐻𝐼𝐽𝐾𝐿𝑀𝑁𝑂𝑃𝑄𝑅𝑆𝑇𝑈𝑉𝑊𝑋𝑌𝑍'  # Mathematical Italic Capital
    '𝑎𝑏𝑐𝑑𝑒𝑓𝑔ℎ𝑖𝑗𝑘𝑙𝑚𝑛𝑜𝑝𝑞𝑟𝑠𝑡𝑢𝑣𝑤𝑥𝑦𝑧'  # Mathematical Italic Small (and planck constant)
    '𝑨𝑩𝑪𝑫𝑬𝑭𝑮𝑯𝑰𝑱𝑲𝑳𝑴𝑵𝑶𝑷𝑸𝑹𝑺𝑻𝑼𝑽𝑾𝑿𝒀𝒁'  # Mathematical Bold Italic Capital
    '𝒂𝒃𝒄𝒅𝒆𝒇𝒈𝒉𝒊𝒋𝒌𝒍𝒎𝒏𝒐𝒑𝒒𝒓𝒔𝒕𝒖𝒗𝒘𝒙𝒚𝒛'  # Mathematical Bold Italic Small

    '𝒜ℬ𝒞𝒟ℰℱ𝒢ℋℐ𝒥𝒦ℒℳ𝒩𝒪𝒫𝒬ℛ𝒮𝒯𝒰𝒱𝒲𝒳𝒴𝒵'  # Mathematical Script Capital
    '𝒶𝒷𝒸𝒹ℯ𝒻ℊ𝒽𝒾𝒿𝓀𝓁𝓂𝓃ℴ𝓅𝓆𝓇𝓈𝓉𝓊𝓋𝓌𝓍𝓎𝓏'  # Mathematical Script Small
    '𝓐𝓑𝓒𝓓𝓔𝓕𝓖𝓗𝓘𝓙𝓚𝓛𝓜𝓝𝓞𝓟𝓠𝓡𝓢𝓣𝓤𝓥𝓦𝓧𝓨𝓩'  # Mathematical Bold Script Capital
    '𝓪𝓫𝓬𝓭𝓮𝓯𝓰𝓱𝓲𝓳𝓴𝓵𝓶𝓷𝓸𝓹𝓺𝓻𝓼𝓽𝓾𝓿𝔀𝔁𝔂𝔃'  # Mathematical Bold Script Small

    '𝔄𝔅ℭ𝔇𝔈𝔉𝔊ℌℑ𝔍𝔎𝔏𝔐𝔑𝔒𝔓𝔔ℜ𝔖𝔗𝔘𝔙𝔚𝔛𝔜ℨ'  # Mathematical Fraktur Capital
    '𝔞𝔟𝔠𝔡𝔢𝔣𝔤𝔥𝔦𝔧𝔨𝔩𝔪𝔫𝔬𝔭𝔮𝔯𝔰𝔱𝔲𝔳𝔴𝔵𝔶𝔷'  # Mathematical Fraktur Small
    '𝕬𝕭𝕮𝕯𝕰𝕱𝕲𝕳𝕴𝕵𝕶𝕷𝕸𝕹𝕺𝕻𝕼𝕽𝕾𝕿𝖀𝖁𝖂𝖃𝖄𝖅'  # Mathematical Bold Fraktur Capital
    '𝖆𝖇𝖈𝖉𝖊𝖋𝖌𝖍𝖎𝖏𝖐𝖑𝖒𝖓𝖔𝖕𝖖𝖗𝖘𝖙𝖚𝖛𝖜𝖝𝖞𝖟'  # Mathematical Bold Fraktur Small

    '𝔸𝔹ℂ𝔻𝔼𝔽𝔾ℍ𝕀𝕁𝕂𝕃𝕄ℕ𝕆ℙℚℝ𝕊𝕋𝕌𝕍𝕎𝕏𝕐ℤ'  # Mathematical Double-Struck Capital
    '𝕒𝕓𝕔𝕕𝕖𝕗𝕘𝕙𝕚𝕛𝕜𝕝𝕞𝕟𝕠𝕡𝕢𝕣𝕤𝕥𝕦𝕧𝕨𝕩𝕪𝕫'  # Mathematical Double-Struck Small
    '𝟘𝟙𝟚𝟛𝟜𝟝𝟞𝟟𝟠𝟡'  # Mathematical Double-Struck Digit
    # see also ⨾ ⨟ ⦂ ⦇  ⦈ ⫿ ⟦ ⟧ and chinese fullstop

    '𝖠𝖡𝖢𝖣𝖤𝖥𝖦𝖧𝖨𝖩𝖪𝖫𝖬𝖭𝖮𝖯𝖰𝖱𝖲𝖳𝖴𝖵𝖶𝖷𝖸𝖹'  # Mathematical Sans-Serif Capital
    '𝖺𝖻𝖼𝖽𝖾𝖿𝗀𝗁𝗂𝗃𝗄𝗅𝗆𝗇𝗈𝗉𝗊𝗋𝗌𝗍𝗎𝗏𝗐𝗑𝗒𝗓'  # Mathematical Sans-Serif Small
    '𝟢𝟣𝟤𝟥𝟦𝟧𝟨𝟩𝟪𝟫'  # Mathematical Sans-Serif Digit
    '𝗔𝗕𝗖𝗗𝗘𝗙𝗚𝗛𝗜𝗝𝗞𝗟𝗠𝗡𝗢𝗣𝗤𝗥𝗦𝗧𝗨𝗩𝗪𝗫𝗬𝗭'  # Mathematical Sans-Serif Bold Capital
    '𝗮𝗯𝗰𝗱𝗲𝗳𝗴𝗵𝗶𝗷𝗸𝗹𝗺𝗻𝗼𝗽𝗾𝗿𝘀𝘁𝘂𝘃𝘄𝘅𝘆𝘇'  # Mathematical Sans-Serif Bold Small
    '𝟬𝟭𝟮𝟯𝟰𝟱𝟲𝟳𝟴𝟵'  # Mathematical Sans-Serif Bold Digit

    '𝘈𝘉𝘊𝘋𝘌𝘍𝘎𝘏𝘐𝘑𝘒𝘓𝘔𝘕𝘖𝘗𝘘𝘙𝘚𝘛𝘜𝘝𝘞𝘟𝘠𝘡'  # Mathematical Sans-Serif Italic Capital
    '𝘢𝘣𝘤𝘥𝘦𝘧𝘨𝘩𝘪𝘫𝘬𝘭𝘮𝘯𝘰𝘱𝘲𝘳𝘴𝘵𝘶𝘷𝘸𝘹𝘺𝘻'  # Mathematical Sans-Serif Italic Small
    '𝘼𝘽𝘾𝘿𝙀𝙁𝙂𝙃𝙄𝙅𝙆𝙇𝙈𝙉𝙊𝙋𝙌𝙍𝙎𝙏𝙐𝙑𝙒𝙓𝙔𝙕'  # Mathematical Sans-Serif Bold Italic Capital
    '𝙖𝙗𝙘𝙙𝙚𝙛𝙜𝙝𝙞𝙟𝙠𝙡𝙢𝙣𝙤𝙥𝙦𝙧𝙨𝙩𝙪𝙫𝙬𝙭𝙮𝙯'  # Mathematical Sans-Serif Bold Italic Small

    '𝙰𝙱𝙲𝙳𝙴𝙵𝙶𝙷𝙸𝙹𝙺𝙻𝙼𝙽𝙾𝙿𝚀𝚁𝚂𝚃𝚄𝚅𝚆𝚇𝚈𝚉'  # Mathematical Monospace Capital
    '𝚊𝚋𝚌𝚍𝚎𝚏𝚐𝚑𝚒𝚓𝚔𝚕𝚖𝚗𝚘𝚙𝚚𝚛𝚜𝚝𝚞𝚟𝚠𝚡𝚢𝚣'  # Mathematical Monospace Small
    '𝟶𝟷𝟸𝟹𝟺𝟻𝟼𝟽𝟾𝟿'  # Mathematical Monospace Digit

    '🄐🄑🄒🄓🄔🄕🄖🄗🄘🄙🄚🄛🄜🄝🄞🄟🄠🄡🄢🄣🄤🄥🄦🄧🄨🄩'  # Parenthesized Latin Capital Letter
    '⒜⒝⒞⒟⒠⒡⒢⒣⒤⒥⒦⒧⒨⒩⒪⒫⒬⒭⒮⒯⒰⒱⒲⒳⒴⒵'  # Parenthesized Latin Small Letter
    '㈇⑴⑵⑶⑷⑸⑹⑺⑻⑼'  # Parenthesized Digit (plus hangul ieung)
    '🄰🄱🄲🄳🄴🄵🄶🄷🄸🄹🄺🄻🄼🄽🄾🄿🅀🅁🅂🅃🅄🅅🅆🅇🅈🅉'  # Squared Latin Capital Letter ⊡
    '🅐🅑🅒🅓🅔🅕🅖🅗🅘🅙🅚🅛🅜🅝🅞🅟🅠🅡🅢🅣🅤🅥🅦🅧🅨🅩'  # Negative Circled Latin Capital Letter 
    '⓿❶❷❸❹❺❻❼❽❾'  # Dingbat Negative Circled Digit
    '🅰🅱🅲🅳🅴🅵🅶🅷🅸🅹🅺🅻🅼🅽🅾🅿🆀🆁🆂🆃🆄🆅🆆🆇🆈🆉'  # Negative Squared Latin Capital Letter 🯄 
    '🇦🇧🇨🇩🇪🇫🇬🇭🇮🇯🇰🇱🇲🇳🇴🇵🇶🇷🇸🇹🇺🇻🇼🇽🇾🇿'  # Regional Indicator Symbol Letter (add zwsp `​`) 
    # 🇦​🇧​🇨​🇩​🇪​🇫​🇬​🇭​🇮​🇯​🇰​🇱​🇲​🇳​🇴​🇵​🇶​🇷​🇸​🇹​🇺​🇻​🇼​🇽​🇾​🇿​

    # todo https://rupertshepherd.info/resource_pages/superscript-letters-in-unicode
    # todo https://en.wikipedia.org/wiki/Unicode_subscripts_and_superscripts
    'ᵃᵇᶜᵈᵉᶠᶢʰⁱʲᵏˡᵐⁿᵒᵖ𐞥ʳˢᵗᵘᵛʷˣʸᶻ'  # superscript small 
    '⁰¹²³⁴⁵⁶⁷⁸⁹'  # superscript digits  (see also ꜝ )

    # https://github.com/Secret-chest/fancify-text/blob/main/fancify_text/fontData.py
    'AᗺƆᗡƎꟻວHIᒐꓘ⅃MИOꟼϘЯƧTUVWXYZ'  # reversed https://www.compart.com/en/unicode/search?q=reversed#characters
    'ɒdɔbɘʇ𝼁ʜiįʞlmnoqpɿƨtυvwxγz'  # reversed ⁏ Ↄ ⸮ ⹁ 
    'ąცƈɖɛʄɠɧıʝƙƖɱŋơ℘զཞʂɬų۷ῳҳყʑ'  # curly
    '₳₿¢₫€₣₲HIJ₭£₥₦O₱QR$₮UV₩X¥₴'  # currency
    'ᗩᗷᑕᗪEᖴGᕼIᒍKᒪᗰᑎOᑭᑫᖇᔕTᑌᐯᗯ᙭Yᘔ'  # cool
    'αႦƈԃҽϝɠԋιʝƙʅɱɳσρϙɾʂƚυʋɯxყȥ'  # magic
    'ᴀʙᴄᴅᴇꜰɢʜɪᴊᴋʟᴍɴᴏᴘǫʀsᴛᴜᴠᴡxʏᴢ'  # small caps
    '∀ᗺϽᗡƎℲƃHIſꓘ˥WNOԀQᴚS⊥∩ΛMXʎZɐqɔpǝɟƃɥ!ɾʞןɯuodbɹsʇnʌʍxʎz˙¡¿'  # upside down
    '卂乃匚ᗪ乇千Ꮆ卄丨ﾌҜㄥ爪几ㄖ卩Ɋ尺丂ㄒㄩᐯ山乂ㄚ乙'  # wiry

    '𐌀𐌁𐌂𐌃𐌄𐌅 g h 𐌆 j 𐌊𐌋𐌌𐌍𐌏𐌓𐌒'  # https://www.compart.com/en/unicode/search?q=Old+Italic+Letter#characters
    '𐌀𐌁𐌂𐌃𐌄𐌅Ᏽ𐋅𐌉Ꮭ𐌊𐌋𐌌𐌍Ꝋ𐌐𐌒𐌓𐌔𐌕𐌵ᕓᏔ𐋄𐌙Ɀ'  # old italic
    'ꍏꌃꉓꀸꍟꎇꁅꃅꀤꀭꀘ꒒ꂵꈤꂦꉣꆰꋪꌗ꓄ꀎꃴꅏꊼꌩꁴ'  # squiggle
    'ꋬꃳꉔ꒯ꏂꊰꍌꁝ꒐꒻ꀘ꒒ꂵꋊꄲꉣꆰꋪꇙ꓄꒤꒦ꅐꉧꌦꁴ'  # squiggle
    'ꋫꃃꏸꁕꍟꄘꁍꑛꂑꀭꀗ꒒ꁒꁹꆂꉣꁸ꒓ꌚ꓅ꐇꏝꅐꇓꐟꁴ'
    'ꍏꌃꉓꀸꍟꎇꁅꃅꀤꀭꀘ꒒ꂵꈤꂦꉣꆰꋪꌗ꓄ꀎꃴꅏꊼꌩꁴ'
    'a͓̽b͓̽c͓̽d͓̽e͓̽f͓̽g͓̽h͓̽i͓̽j͓̽k͓̽l͓̽m͓̽n͓̽o͓̽p͓̽q͓̽r͓̽s͓̽t͓̽u͓̽v͓̽w͓̽x͓̽y͓̽z͓̽'

    'ԹՅՇԺȝԲԳɧɿʝƙʅʍՌρφՐՏԵՄעաՃՎՀΙ'  # armenian
    'αвς∂єfgнιנкℓмиσρףяѕтυνωאָуz'  # greek
    'αв¢∂єƒgнιנкℓмησρqяѕтυνωχуz'

)
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
}

# https://unicode.org/charts/PDF/UFF00.pdf
wide = [
    " !\"#$%&'()*+,-./0123456789:;<=>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ[\\]^_`abcdefghijklmnopqrstuvwxyz{|}~¢£¥",
    " ！＂＃＄％＆＇（）＊＋，－．／０１２３４５６７８９：；＜＝＞？＠ＡＢＣＤＥＦＧＨＩＪＫＬＭＮＯＰＱＲＳＴＵＶＷＸＹＺ［＼］＾＿｀ａｂｃｄｅｆｇｈｉｊｋｌｍｎｏｐｑｒｓｔｕｖｗｘｙｚ｛｜｝～￠￡￥"
]

# https://www.unicode.org/L2/L2020/20275r-math-calligraphic.pdf
''.join(
    '\U0001D49C\uFE00'  # MATHEMATICAL CHANCERY CAPITAL A
    '\U0000212C\uFE00'  # MATHEMATICAL CHANCERY CAPITAL B
    '\U0001D49E\uFE00'  # MATHEMATICAL CHANCERY CAPITAL C
    '\U0001D49F\uFE00'  # MATHEMATICAL CHANCERY CAPITAL D
    '\U00002130\uFE00'  # MATHEMATICAL CHANCERY CAPITAL E
    '\U00002131\uFE00'  # MATHEMATICAL CHANCERY CAPITAL F
    '\U0001D4A2\uFE00'  # MATHEMATICAL CHANCERY CAPITAL G
    '\U0000210B\uFE00'  # MATHEMATICAL CHANCERY CAPITAL H
    '\U00002110\uFE00'  # MATHEMATICAL CHANCERY CAPITAL I
    '\U0001D4A5\uFE00'  # MATHEMATICAL CHANCERY CAPITAL J
    '\U0001D4A6\uFE00'  # MATHEMATICAL CHANCERY CAPITAL K
    '\U00002112\uFE00'  # MATHEMATICAL CHANCERY CAPITAL L
    '\U00002133\uFE00'  # MATHEMATICAL CHANCERY CAPITAL M
    '\U0001D4A9\uFE00'  # MATHEMATICAL CHANCERY CAPITAL N
    '\U0001D4AA\uFE00'  # MATHEMATICAL CHANCERY CAPITAL O
    '\U0001D4AB\uFE00'  # MATHEMATICAL CHANCERY CAPITAL P
    '\U0001D4AC\uFE00'  # MATHEMATICAL CHANCERY CAPITAL Q
    '\U0000211B\uFE00'  # MATHEMATICAL CHANCERY CAPITAL R
    '\U0001D4AE\uFE00'  # MATHEMATICAL CHANCERY CAPITAL S
    '\U0001D4AF\uFE00'  # MATHEMATICAL CHANCERY CAPITAL T
    '\U0001D4B0\uFE00'  # MATHEMATICAL CHANCERY CAPITAL U
    '\U0001D4B1\uFE00'  # MATHEMATICAL CHANCERY CAPITAL V
    '\U0001D4B2\uFE00'  # MATHEMATICAL CHANCERY CAPITAL W
    '\U0001D4B3\uFE00'  # MATHEMATICAL CHANCERY CAPITAL X
    '\U0001D4B4\uFE00'  # MATHEMATICAL CHANCERY CAPITAL Y
    '\U0001D4B5\uFE00'  # MATHEMATICAL CHANCERY CAPITAL Z
)
''.join(
    '\U0001D49C\uFE01'  # MATHEMATICAL ROUNDHAND CAPITAL A
    '\U0000212C\uFE01'  # MATHEMATICAL ROUNDHAND CAPITAL B
    '\U0001D49E\uFE01'  # MATHEMATICAL ROUNDHAND CAPITAL C
    '\U0001D49F\uFE01'  # MATHEMATICAL ROUNDHAND CAPITAL D
    '\U00002130\uFE01'  # MATHEMATICAL ROUNDHAND CAPITAL E
    '\U00002131\uFE01'  # MATHEMATICAL ROUNDHAND CAPITAL F
    '\U0001D4A2\uFE01'  # MATHEMATICAL ROUNDHAND CAPITAL G
    '\U0000210B\uFE01'  # MATHEMATICAL ROUNDHAND CAPITAL H
    '\U00002110\uFE01'  # MATHEMATICAL ROUNDHAND CAPITAL I
    '\U0001D4A5\uFE01'  # MATHEMATICAL ROUNDHAND CAPITAL J
    '\U0001D4A6\uFE01'  # MATHEMATICAL ROUNDHAND CAPITAL K
    '\U00002112\uFE01'  # MATHEMATICAL ROUNDHAND CAPITAL L
    '\U00002133\uFE01'  # MATHEMATICAL ROUNDHAND CAPITAL M
    '\U0001D4A9\uFE01'  # MATHEMATICAL ROUNDHAND CAPITAL N
    '\U0001D4AA\uFE01'  # MATHEMATICAL ROUNDHAND CAPITAL O
    '\U0001D4AB\uFE01'  # MATHEMATICAL ROUNDHAND CAPITAL P
    '\U0001D4AC\uFE01'  # MATHEMATICAL ROUNDHAND CAPITAL Q
    '\U0000211B\uFE01'  # MATHEMATICAL ROUNDHAND CAPITAL R
    '\U0001D4AE\uFE01'  # MATHEMATICAL ROUNDHAND CAPITAL S
    '\U0001D4AF\uFE01'  # MATHEMATICAL ROUNDHAND CAPITAL T
    '\U0001D4B0\uFE01'  # MATHEMATICAL ROUNDHAND CAPITAL U
    '\U0001D4B1\uFE01'  # MATHEMATICAL ROUNDHAND CAPITAL V
    '\U0001D4B2\uFE01'  # MATHEMATICAL ROUNDHAND CAPITAL W
    '\U0001D4B3\uFE01'  # MATHEMATICAL ROUNDHAND CAPITAL X
    '\U0001D4B4\uFE01'  # MATHEMATICAL ROUNDHAND CAPITAL Y
    '\U0001D4B5\uFE01'  # MATHEMATICAL ROUNDHAND CAPITAL Z
)
