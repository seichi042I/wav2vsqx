from numpy import ceil
import pyopenjtalk
from pathlib import Path
from xml.dom.minidom import Document
import re

# 各条件を正規表現で表す
c1 = '[ウクスツヌフムユルグズヅブプヴ][ァィェォ]'  # ウ段＋「ァ/ィ/ェ/ォ」
c2 = '[イキシチニヒミリギジヂビピ][ャュェョ]'  # イ段（「イ」を除く）＋「ャ/ュ/ェ/ョ」
c3 = '[テデ][ィュ]'  # 「テ/デ」＋「ャ/ィ/ュ/ョ」
c4 = '[ァ-ヴー]'  # カタカナ１文字（長音含む）

cond = '('+c1+'|'+c2+'|'+c3+'|'+c4+')'
re_mora = re.compile(cond)


def moraWakachi(kana_text):
    return re_mora.findall(kana_text)


miku_go = {
    "あ": "a",    "い": "i",     "う": "M",     "え": "e",    "お": "o",
    "か": "k a",  "き": "k' i",  "く": "k M",   "け": "k e",  "こ": "k o",
    "さ": "s a",  "し": "S i",   "す": "s M",   "せ": "s e",  "そ": "s o",
    "た": "t a",  "ち": "tS i",  "つ": "ts M",  "て": "t e",  "と": "t o",
    "な": "n a",  "に": "J i",   "ぬ": "n M",   "ね": "n e",  "の": "n o",
    "は": "h a",  "ひ": "C i",   "ふ": "p\\ M", "へ": "h e",  "ほ": "h o",
    "ま": "m a",  "み": "m' i",  "む": "m M",   "め": "m e",  "も": "m o",
    "ら": "4 a",  "り": "4' i",  "る": "4 M",   "れ": "4 e",  "ろ": "4 o",
    "が": "g a",  "ぎ": "g' i",  "ぐ": "g M",   "げ": "g e",  "ご": "g o",
    "ざ": "dz a", "じ": "dZ i",  "ず": "dz M",  "ぜ": "dz e", "ぞ": "dz o",
    "だ": "d a",  "ぢ": "dZ i",  "づ": "dz M",  "で": "d e",  "ど": "d o",
    "ば": "b a",  "び": "b' i",  "ぶ": "b M",   "べ": "b e",  "ぼ": "b o",
    "ぱ": "p a",  "ぴ": "p' i",  "ぷ": "p M",   "ぺ": "p e",  "ぽ": "p o",
    "や": "j a",  "ゆ": "j M",   "よ": "j o",
    "わ": "w a",  "ゐ": "w i",   "ゑ": "w e",   "を": "o",    "ん": "N\\",
    "ふぁ": "p\ a", "つぁ": "ts a",
    "うぃ": "w i",  "すぃ": "s i",   "ずぃ": "dz i", "つぃ": "ts i",  "てぃ": "t' i",
    "でぃ": "d' i", "ふぃ": "p\' i",
    "とぅ": "t M",  "どぅ": "d M",
    "いぇ": "j e",  "うぇ": "w e",   "きぇ": "k' e", "しぇ": "S e",   "ちぇ": "tS e",
    "つぇ": "ts e", "てぇ": "t' e",  "にぇ": "J e",  "ひぇ": "C e",   "みぇ": "m' e",
    "りぇ": "4' e", "ぎぇ": "g' e",  "じぇ": "dZ e", "でぇ": "d' e",  "びぇ": "b' e",
    "ぴぇ": "p' e", "ふぇ": "p\ e",
    "うぉ": "w o",  "つぉ": "ts o",  "ふぉ": "p\ o",
    "きゃ": "k' a", "しゃ": "S a",   "ちゃ": "tS a", "てゃ": "t' a",  "にゃ": "J a",
    "ひゃ": "C a",  "みゃ": "m' a",  "りゃ": "4' a", "ぎゃ": "N' a",  "じゃ": "dZ a",
    "でゃ": "d' a", "びゃ": "b' a",  "ぴゃ": "p' a", "ふゃ": "p\' a",
    "きゅ": "k' M", "しゅ": "S M",   "ちゅ": "tS M", "てゅ": "t' M",  "にゅ": "J M",
    "ひゅ": "C M",  "みゅ": "m' M",  "りゅ": "4' M", "ぎゅ": "g' M",  "じゅ": "dZ M",
    "でゅ": "d' M", "びゅ": "b' M",  "ぴゅ": "p' M", "ふゅ": "p\' M",
    "きょ": "k' o", "しょ": "S o",   "ちょ": "tS o", "てょ": "t' o",  "にょ": "J o",
    "ひょ": "C o",  "みょ": "m' o",  "りょ": "4' o", "ぎょ": "N' o",  "じょ": "dZ o",
    "でょ": "d' o", "びょ": "b' o",  "ぴょ": "p' o",

    "ア": "a",    "イ": "i",     "ウ": "M",     "エ": "e",    "オ": "o",
    "カ": "k a",  "キ": "k' i",  "ク": "k M",   "ケ": "k e",  "コ": "k o",
    "サ": "s a",  "シ": "S i",   "ス": "s M",   "セ": "s e",  "ソ": "s o",
    "タ": "t a",  "チ": "tS i",  "ツ": "ts M",  "テ": "t e",  "ト": "t o",
    "ナ": "n a",  "ニ": "J i",   "ヌ": "n M",   "ネ": "n e",  "ノ": "n o",
    "ハ": "h a",  "ヒ": "C i",   "フ": "p\\ M", "ヘ": "h e",  "ホ": "h o",
    "マ": "m a",  "ミ": "m' i",  "ム": "m M",   "メ": "m e",  "モ": "m o",
    "ラ": "4 a",  "リ": "4' i",  "ル": "4 M",   "レ": "4 e",  "ロ": "4 o",
    "ガ": "g a",  "ギ": "g' i",  "グ": "g M",   "ゲ": "g e",  "ゴ": "g o",
    "ザ": "dz a", "ジ": "dZ i",  "ズ": "dz M",  "ゼ": "dz e", "ゾ": "dz o",
    "ダ": "d a",  "ヂ": "dZ i",  "ヅ": "dz M",  "デ": "d e",  "ド": "d o",
    "バ": "b a",  "ビ": "b' i",  "ブ": "b M",   "ベ": "b e",  "ボ": "b o",
    "パ": "p a",  "ピ": "p' i",  "プ": "p M",   "ペ": "p e",  "ポ": "p o",
    "ヤ": "j a",  "ユ": "j M",   "ヨ": "j o",
    "ワ": "w a", "ヲ": "o",    "ン": "N\\",
    "ファ": "p\ a", "ツァ": "ts a",
    "ウィ": "w i",  "スィ": "s i",   "ズィ": "dz i", "ツィ": "ts i",  "ティ": "t' i",
    "ディ": "d' i", "フィ": "p\' i",
    "トゥ": "t M",  "ドゥ": "d M",
    "イェ": "j e",  "ウェ": "w e",   "キェ": "k' e", "シェ": "S e",   "チェ": "tS e",
    "ツェ": "ts e", "テェ": "t' e",  "ニェ": "J e",  "ヒェ": "C e",   "ミェ": "m' e",
    "リェ": "4' e", "ギェ": "g' e",  "ジェ": "dZ e", "デェ": "d' e",  "ビェ": "b' e",
    "ピェ": "p' e", "フェ": "p\ e",
    "ウォ": "w o",  "ツォ": "ts o",  "フォ": "p\ o",
    "キャ": "k' a", "シャ": "S a",   "チャ": "tS a", "テャ": "t' a",  "ニャ": "J a",
    "ヒャ": "C a",  "ミャ": "m' a",  "リャ": "4' a", "ギャ": "N' a",  "ジャ": "dZ a",
    "デャ": "d' a", "ビャ": "b' a",  "ピャ": "p' a", "フャ": "p\' a",
    "キュ": "k' M", "シュ": "S M",   "チュ": "tS M", "テュ": "t' M",  "ニュ": "J M",
    "ヒュ": "C M",  "ミュ": "m' M",  "リュ": "4' M", "ギュ": "g' M",  "ジュ": "dZ M",
    "デュ": "d' M", "ビュ": "b' M",  "ピュ": "p' M", "フュ": "p\' M",
    "キョ": "k' o", "ショ": "S o",   "チョ": "tS o", "テョ": "t' o",  "ニョ": "J o",
    "ヒョ": "C o",  "ミョ": "m' o",  "リョ": "4' o", "ギョ": "N' o",  "ジョ": "dZ o",
    "デョ": "d' o", "ビョ": "b' o",  "ピョ": "p' o"
}

vowel = ['a', 'i', 'u', 'e', 'o', 'A', 'I', 'U', 'E', 'O']
special = ['silB', 'silE', "sp"]


def kana2mkp(kana: str = 'ら', def_phoneme: str = '4 a') -> str:
    """仮名からPiapro Studio用の音素に変換

    Args:
        kana (str, optional): 変換したいモーラ. Defaults to 'ら'.

    Returns:
        str: 音素
    """
    return miku_go.get(kana, def_phoneme)


def g2p_julius(text_filepath: Path, out_dirpath: Path):
    with open(text_filepath, 'r') as in_file:
        for line in in_file.readlines():
            name = "voice"
            text = line

            phoneme = pyopenjtalk.g2p(text, kana=False)
            phoneme = phoneme.lower()
            phoneme = phoneme.replace('pau', 'sp')
            phoneme = phoneme.replace('cl', 'q')
            print(phoneme)
            Path("text").mkdir(exist_ok=True, parents=True)
            with open(out_dirpath / f'{name}.txt', 'w') as out_file:
                out_file.write(phoneme)


def lab_analisys(dirpath: Path, spf: float):
    """labファイルからモーラと継続時間を解析

    Args:
        filepath (Path): labファイルのパス
        spf (float): 1フレームが何秒か。sec per frame
    Returns:
        Tuple[str, str, List, List]: kanaはカタカナの文字列。morasはjuliusの音素。timesは秒単位でモーラの開始時刻と終了時刻のリスト。framesはモーラ単位のstftの開始フレームと終了フレーム。
    """
    with open(dirpath / "segmentation/lab/voice.lab", "r") as f:
        lines = f.readlines()
    moras = []
    times = []
    frames = []
    elapsed = [0, 0]
    mora = ''
    for l in lines:
        # 改行削除
        begin, end, phoneme = l.replace('\n', '').split(' ')

        if phoneme in vowel:  # 母音があれば終端
            if mora == '':
                elapsed[0] = float(begin)

            elapsed[1] = float(end)
            mora += phoneme

            frame = [int(ceil(e/spf)) for e in elapsed]

            moras.append(mora)
            times.append(elapsed)
            frames.append(frame)

            mora = ''
            elapsed = [0, 0]

        elif not phoneme in special:  # 特殊記号以外は子音。子音が来たら始端
            if mora == '':
                mora += phoneme
                elapsed[0] = float(begin)
            elif mora == 'n' or mora == 'q':  # 一つ前がnならば「ん」なので区切る
                elapsed[1] = float(begin)

                frame = [int(ceil(e/spf)) for e in elapsed]

                moras.append(mora)
                times.append(elapsed)
                frames.append(frame)

                mora = phoneme
                elapsed = [float(begin), 0]
        else:  # 特殊記号が来たら区切る
            moras.append(phoneme)
            elapsed = [float(begin), float(end)]
            times.append(elapsed)
            frames.append([int(ceil(e/spf)) for e in elapsed])

            elapsed = [0, 0]

    with open(dirpath / "text", "r") as f:
        text = f.readline()
        text = text.replace('\n', '').replace('。', '')
    kana = pyopenjtalk.g2p(text=text, kana=True)

    return moraWakachi(kana), times[1:-1], frames[1:-1], int(times[1][0]*1000)

# pitch bend


def set_pitch_bend_sensitivity(doc: Document, sensitivity: int = 0):
    # tag
    mCtrl = doc.createElement('mCtrl')
    posTick = doc.createElement('posTick')
    attr = doc.createElement('attr')
    attr.setAttribute("id", "PBS")

    # content
    pos_text = doc.createTextNode(f'0')
    attr_sens = doc.createTextNode(f'{sensitivity}')

    # append
    posTick.appendChild(pos_text)
    attr.appendChild(attr_sens)
    mCtrl.appendChild(posTick)
    mCtrl.appendChild(attr)

    return mCtrl


def pitch_plot(doc: Document, pos: int, pitch: int = 0):
    # tag
    mCtrl = doc.createElement('mCtrl')
    posTick = doc.createElement('posTick')
    attr = doc.createElement('attr')
    attr.setAttribute("id", "PIT")

    # content
    pos_text = doc.createTextNode(f'{pos}')
    attr_PIT = doc.createTextNode(f'{pitch}')

    # append
    posTick.appendChild(pos_text)
    attr.appendChild(attr_PIT)
    mCtrl.appendChild(posTick)
    mCtrl.appendChild(attr)

    return mCtrl


def create_note_json(tick: int, note_num: int, lyrics: str):
    noteOn = {'velocity': 80, 'tick': 0,
              'sub_type': 'noteOn', 'channel': 0, 'note_num': note_num}
    noteOff = {u'velocity': 0, u'tick': tick, u'sub_type': u'noteOff',
               u'channel': 0, u'note_num': note_num, u'lyrics': lyrics}
    return noteOn, noteOff
