# -*- coding: utf-8 -*-
from typing import Tuple
import xml.dom.minidom
import pyopenjtalk

import numpy as np
import librosa
import music21 as m21

from f0_extractor.pitch_extract import Harvest
unicode = str

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


def lab_analisys(filepath: str):
    with open(filepath, "r") as f:
        lines = f.readlines()
    moras = []
    times = []
    frames = []
    elapsed = [0, 0]
    mora = ''

    for l in lines:
        l = l.replace('\n', '').split(' ')
        print(l)
        if l[2] in ['a', 'i', 'u', 'e', 'o', 'A', 'I', 'U', 'E', 'O']:  # 母音があれば終端
            if mora == '':
                elapsed[0] = float(l[0])
            elapsed[1] = float(l[1])
            mora += f' {l[2]}'
            frame = [int(np.ceil(elapsed[0]/(hop_len/sr))),
                     int(np.ceil(elapsed[1]/(hop_len/sr)))]

            moras.append(mora)
            times.append(elapsed)
            frames.append(frame)

            mora = ''
            elapsed = [0, 0]

        elif not l[2] in ['silB', 'silE', "sp"]:  # 特殊記号以外は子音。子音が来たら始端
            if mora == '':
                mora += l[2]
                elapsed[0] = float(l[0])
            elif mora == 'n':  # 一つ前がnならば「ん」なので区切る
                elapsed[1] = float(l[0])
                frame = [int(np.ceil(elapsed[0]/(hop_len/sr))),
                         int(np.ceil(elapsed[1]/(hop_len/sr)))]

                moras.append('N')
                times.append(elapsed)
                frames.append(frame)
                mora = l[2]
                elapsed = [float(l[0]), 0]
        else:
            moras.append(l[2])
            times.append([float(l[0]), float(l[1])])
            frames.append([int(np.ceil(float(l[0])/(hop_len/sr))),
                           int(np.ceil(float(l[1])/(hop_len/sr)))])
    print(moras)
    kana = pyopenjtalk.g2p(text="流しぎりが完全に入れば、デバフの効果が付与される", kana=True)
    # print(kana)
    # print(len(moras))
    # print(times)
    # print(frames)
    # print(len(kana))

    return kana, moras, times, frames


def json2vsqx(data):
    resolution_value = str(data["resolution"])
    format_value = str(data["format"])
    tracks_value = str(data["tracks"])

    doc = xml.dom.minidom.Document()
    vsq3 = doc.createElementNS(
        'http://www.yamaha.co.jp/vocaloid/schema/vsq3/', 'vsq3')
    vsq3.setAttribute("xmlns", "http://www.yamaha.co.jp/vocaloid/schema/vsq3/")
    vsq3.setAttribute("xmlns:xsi", "http://www.w3.org/2001/XMLSchema-instance")
    vsq3.setAttribute("xsi:schemaLocation",
                      "http://www.yamaha.co.jp/vocaloid/schema/vsq3/ vsq3.xsd")

# vender
    vender = doc.createElement('vender')
    vender_value = doc.createCDATASection("Yamaha corporation")
    vender.appendChild(vender_value)
    vsq3.appendChild(vender)
# version
    version = doc.createElement('version')
    version_value = doc.createCDATASection("3.0.0.11")
    version.appendChild(version_value)
    vsq3.appendChild(version)
# vVoiceTable
    vVoiceTable = doc.createElement('vVoiceTable')
    vVoice = doc.createElement('vVoice')
    # vBS
    vBS = doc.createElement('vBS')
    vBS_text = doc.createTextNode(u'0')
    vBS.appendChild(vBS_text)
    vVoice.appendChild(vBS)
    # vPC
    vPC = doc.createElement('vPC')
    vPC_text = doc.createTextNode(u'0')
    vPC.appendChild(vPC_text)
    vVoice.appendChild(vPC)
    # compID
    compID = doc.createElement('compID')
    compID_value = doc.createCDATASection("BEKDC85ZLWXHZECF")       # ここは変更が必要？
    compID.appendChild(compID_value)
    vVoice.appendChild(compID)
    # vVoiceName
    vVoiceName = doc.createElement('vVoiceName')
    vVoiceName_value = doc.createCDATASection("MIKU_V3_Original")
    vVoiceName.appendChild(vVoiceName_value)
    vVoice.appendChild(vVoiceName)
    # vVoiceParam
    vVoiceParam = doc.createElement('vVoiceParam')
    # bre
    bre = doc.createElement('bre')
    bre_text = doc.createTextNode(u'0')
    bre.appendChild(bre_text)
    vVoiceParam.appendChild(bre)
    # bri
    bri = doc.createElement('bri')
    bri_text = doc.createTextNode(u'0')
    bri.appendChild(bri_text)
    vVoiceParam.appendChild(bri)
    # cle
    cle = doc.createElement('cle')
    cle_text = doc.createTextNode(u'0')
    cle.appendChild(cle_text)
    vVoiceParam.appendChild(cle)
    # gen
    gen = doc.createElement('gen')
    gen_text = doc.createTextNode(u'0')
    gen.appendChild(gen_text)
    vVoiceParam.appendChild(gen)
    # ope
    ope = doc.createElement('ope')
    ope_text = doc.createTextNode(u'0')
    ope.appendChild(ope_text)
    vVoiceParam.appendChild(ope)
    vVoice.appendChild(vVoiceParam)
    vVoiceTable.appendChild(vVoice)
    vsq3.appendChild(vVoiceTable)

# mixer
    mixer = doc.createElement('mixer')
    # masterUnit
    masterUnit = doc.createElement('masterUnit')
    # outDev
    outDev = doc.createElement('outDev')
    outDev_text = doc.createTextNode(u'0')
    outDev.appendChild(outDev_text)
    masterUnit.appendChild(outDev)
    # retLevel
    retLevel = doc.createElement('retLevel')
    retLevel_text = doc.createTextNode(u'0')
    retLevel.appendChild(retLevel_text)
    masterUnit.appendChild(retLevel)
    # vol
    vol = doc.createElement('vol')
    vol_text = doc.createTextNode(u'0')
    vol.appendChild(vol_text)
    masterUnit.appendChild(vol)
    mixer.appendChild(masterUnit)

    # vsUnit
    vsUnit = doc.createElement('vsUnit')
    # vsTrackNo
    vsTrackNo = doc.createElement('vsTrackNo')
    vsTrackNo_text = doc.createTextNode(u'0')
    vsTrackNo.appendChild(vsTrackNo_text)
    vsUnit.appendChild(vsTrackNo)
    # inGain
    inGain = doc.createElement('inGain')
    inGain_text = doc.createTextNode(u'0')
    inGain.appendChild(inGain_text)
    vsUnit.appendChild(inGain)
    # sendLevel
    sendLevel = doc.createElement('sendLevel')
    sendLevel_text = doc.createTextNode(u'-898')
    sendLevel.appendChild(sendLevel_text)
    vsUnit.appendChild(sendLevel)
    # sendEnable
    sendEnable = doc.createElement('sendEnable')
    sendEnable_text = doc.createTextNode(u'0')
    sendEnable.appendChild(sendEnable_text)
    vsUnit.appendChild(sendEnable)
    # mute
    mute = doc.createElement('mute')
    mute_text = doc.createTextNode(u'0')
    mute.appendChild(mute_text)
    vsUnit.appendChild(mute)
    # solo
    solo = doc.createElement('solo')
    solo_text = doc.createTextNode(u'0')
    solo.appendChild(solo_text)
    vsUnit.appendChild(solo)
    # pan
    pan = doc.createElement('pan')
    pan_text = doc.createTextNode(u'80')
    pan.appendChild(pan_text)
    vsUnit.appendChild(pan)
    # vol
    vol = doc.createElement('vol')
    vol_text = doc.createTextNode(u'0')
    vol.appendChild(vol_text)
    vsUnit.appendChild(vol)
    mixer.appendChild(vsUnit)

    # seUnit
    seUnit = doc.createElement('seUnit')
    # inGain
    inGain = doc.createElement('inGain')
    inGain_text = doc.createTextNode(u'0')
    inGain.appendChild(inGain_text)
    seUnit.appendChild(inGain)
    # sendLevel
    sendLevel = doc.createElement('sendLevel')
    sendLevel_text = doc.createTextNode(u'-898')
    sendLevel.appendChild(sendLevel_text)
    seUnit.appendChild(sendLevel)
    # sendEnable
    sendEnable = doc.createElement('sendEnable')
    sendEnable_text = doc.createTextNode(u'0')
    sendEnable.appendChild(sendEnable_text)
    seUnit.appendChild(sendEnable)
    # mute
    mute = doc.createElement('mute')
    mute_text = doc.createTextNode(u'0')
    mute.appendChild(mute_text)
    seUnit.appendChild(mute)
    # solo
    solo = doc.createElement('solo')
    solo_text = doc.createTextNode(u'0')
    solo.appendChild(solo_text)
    seUnit.appendChild(solo)
    # pan
    pan = doc.createElement('pan')
    pan_text = doc.createTextNode(u'80')
    pan.appendChild(pan_text)
    seUnit.appendChild(pan)
    # vol
    vol = doc.createElement('vol')
    vol_text = doc.createTextNode(u'0')
    vol.appendChild(vol_text)
    seUnit.appendChild(vol)
    mixer.appendChild(seUnit)

    # karaokeUnit
    karaokeUnit = doc.createElement('karaokeUnit')
    # inGain
    inGain = doc.createElement('inGain')
    inGain_text = doc.createTextNode(u'0')
    inGain.appendChild(inGain_text)
    karaokeUnit.appendChild(inGain)
    # mute
    mute = doc.createElement('mute')
    mute_text = doc.createTextNode(u'0')
    mute.appendChild(mute_text)
    karaokeUnit.appendChild(mute)
    # solo
    solo = doc.createElement('solo')
    solo_text = doc.createTextNode(u'0')
    solo.appendChild(solo_text)
    karaokeUnit.appendChild(solo)
    # vol
    vol = doc.createElement('vol')
    vol_text = doc.createTextNode(u'-129')
    vol.appendChild(vol_text)
    karaokeUnit.appendChild(vol)
    mixer.appendChild(karaokeUnit)
    vsq3.appendChild(mixer)

# masterTrack        本当はテンポが細かく決まっている場合があるけど、今回はデフォルトにする
    masterTrack = doc.createElement('masterTrack')
    # seqName
    seqName = doc.createElement('seqName')
    seqName_text = doc.createCDATASection(u'none')
    seqName.appendChild(seqName_text)
    masterTrack.appendChild(seqName)
    # comment
    comment = doc.createElement('comment')
    comment_text = doc.createCDATASection(u'none')
    comment.appendChild(comment_text)
    masterTrack.appendChild(comment)
    # resolution
    resolution = doc.createElement('resolution')
    resolution_text = doc.createTextNode(unicode(resolution_value))
    resolution.appendChild(resolution_text)
    masterTrack.appendChild(resolution)
    # preMeasure
    preMeasure = doc.createElement('preMeasure')
    preMeasure_text = doc.createTextNode('4')
    preMeasure.appendChild(preMeasure_text)
    masterTrack.appendChild(preMeasure)
    # timeSig
    timeSig = doc.createElement('timeSig')
    # posMes
    posMes = doc.createElement('posMes')
    posMes_text = doc.createTextNode(u'0')
    posMes.appendChild(posMes_text)
    timeSig.appendChild(posMes)
    # nume
    nume = doc.createElement('nume')
    nume_text = doc.createTextNode(u'4')
    nume.appendChild(nume_text)
    timeSig.appendChild(nume)
    # denomi
    denomi = doc.createElement('denomi')
    denomi_text = doc.createTextNode(u'4')
    denomi.appendChild(denomi_text)
    timeSig.appendChild(denomi)
    masterTrack.appendChild(timeSig)
    # tempo
    tempo = doc.createElement('tempo')
    # posTick
    posTick = doc.createElement('posTick')
    posTick_text = doc.createTextNode(u'0')
    posTick.appendChild(posTick_text)
    tempo.appendChild(posTick)
    # bpm
    bpm = doc.createElement('bpm')
    bpm_text = doc.createTextNode(u'12000')
    bpm.appendChild(bpm_text)
    tempo.appendChild(bpm)
    masterTrack.appendChild(tempo)
    vsq3.appendChild(masterTrack)

# vsTrack
    vsTrack = doc.createElement('vsTrack')
    # vsTrackNo
    vsTrackNo = doc.createElement('vsTrackNo')
    vsTrackNo_text = doc.createTextNode(u'0')
    vsTrackNo.appendChild(vsTrackNo_text)
    vsTrack.appendChild(vsTrackNo)
    # trackName
    trackName = doc.createElement('trackName')
    trackName_text = doc.createCDATASection(u'MIKU_V3_Original')
    trackName.appendChild(trackName_text)
    vsTrack.appendChild(trackName)
    # comment
    comment = doc.createElement('comment')
    comment_text = doc.createCDATASection(u'Track')
    comment.appendChild(comment_text)
    vsTrack.appendChild(comment)
    # musicalPart
    musicalPart = doc.createElement('musicalPart')
    # posTick
    posTick = doc.createElement('posTick')
    posTick_text = doc.createTextNode(u'7680')
    posTick.appendChild(posTick_text)
    musicalPart.appendChild(posTick)
    # playTime
    playTime = doc.createElement('playTime')
    playTime_text = doc.createTextNode(u'614400')        # ここは伸ばす?
    playTime.appendChild(playTime_text)
    musicalPart.appendChild(playTime)
    # partName
    partName = doc.createElement('partName')
    partName_text = doc.createCDATASection(u'MIKU_V3_Original')
    partName.appendChild(partName_text)
    musicalPart.appendChild(partName)
    # comment
    comment = doc.createElement('comment')
    comment_text = doc.createCDATASection(u'')
    comment.appendChild(comment_text)
    musicalPart.appendChild(comment)

    # stylePlugin
    stylePlugin = doc.createElement('stylePlugin')
    # stylePluginID
    stylePluginID = doc.createElement('stylePluginID')
    stylePluginID_text = doc.createCDATASection(
        u'ACA9C502-A04B-42b5-B2EB-5CEA36D16FCE')
    stylePluginID.appendChild(stylePluginID_text)
    stylePlugin.appendChild(stylePluginID)
    # stylePluginName
    stylePluginName = doc.createElement('stylePluginName')
    stylePluginName_text = doc.createCDATASection(
        u'VOCALOID2 Compatible Style')
    stylePluginName.appendChild(stylePluginName_text)
    stylePlugin.appendChild(stylePluginName)
    # version
    version = doc.createElement('version')
    version_text = doc.createCDATASection(u'3.0.0.1')
    version.appendChild(version_text)
    stylePlugin.appendChild(version)
    musicalPart.appendChild(stylePlugin)

    # partStyle
    partStyle = doc.createElement('partStyle')
    # attr accent
    attr = doc.createElement('attr')
    attr.setAttribute("id", "accent")
    attr_text = doc.createTextNode(u'50')
    attr.appendChild(attr_text)
    partStyle.appendChild(attr)
    # attr bendDep
    attr = doc.createElement('attr')
    attr.setAttribute("id", "bendDep")
    attr_text = doc.createTextNode(u'8')
    attr.appendChild(attr_text)
    partStyle.appendChild(attr)
    # attr bendLen
    attr = doc.createElement('attr')
    attr.setAttribute("id", "bendLen")
    attr_text = doc.createTextNode(u'0')
    attr.appendChild(attr_text)
    partStyle.appendChild(attr)
    # attr decay
    attr = doc.createElement('attr')
    attr.setAttribute("id", "decay")
    attr_text = doc.createTextNode(u'50')
    attr.appendChild(attr_text)
    partStyle.appendChild(attr)
    # attr fallPort
    attr = doc.createElement('attr')
    attr.setAttribute("id", "fallPort")
    attr_text = doc.createTextNode(u'0')
    attr.appendChild(attr_text)
    partStyle.appendChild(attr)
    # attr opening
    attr = doc.createElement('attr')
    attr.setAttribute("id", "opening")
    attr_text = doc.createTextNode(u'127')
    attr.appendChild(attr_text)
    partStyle.appendChild(attr)
    # attr risePort
    attr = doc.createElement('attr')
    attr.setAttribute("id", "risePort")
    attr_text = doc.createTextNode(u'0')
    attr.appendChild(attr_text)
    partStyle.appendChild(attr)
    musicalPart.appendChild(partStyle)

    # singer
    singer = doc.createElement('singer')
    # posTick
    posTick = doc.createElement('posTick')
    posTick_text = doc.createTextNode(u'0')
    posTick.appendChild(posTick_text)
    singer.appendChild(posTick)
    # vBS
    vBS = doc.createElement('vBS')
    vBS_text = doc.createTextNode(u'0')
    vBS.appendChild(vBS_text)
    singer.appendChild(vBS)
    # vPC
    vPC = doc.createElement('vPC')
    vPC_text = doc.createTextNode(u'0')
    vPC.appendChild(vPC_text)
    singer.appendChild(vPC)
    musicalPart.appendChild(singer)

    # pitch bend
    def set_pitch_bend_sensitivity(sensitivity: int = 0):
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

    def pitch_plot(pos: int, pitch: int = 0):
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

# ==========ここから楽譜============================
    # pitch
    musicalPart.appendChild(set_pitch_bend_sensitivity(12))
    for pit, pos in zip(data['pitch'], data['pitch_pos']):
        musicalPart.appendChild(pitch_plot(pos, pit))
    POSTICK = 0
    DURTICK = 0
    for note in data["stream"]:
        if note["sub_type"] == "noteOn":
            VELOCITY = note["velocity"]
            A = note["tick"]
        if note["sub_type"] == "noteOff":
            if POSTICK == 0:
                POSTICK = A
                # musicalPart.appendChild(set_pitch_bend_sensitivity(12))
            else:
                POSTICK = POSTICK + (A + DURTICK)
            NOTENUM = note["note_num"]
            DURTICK = note["tick"]
            LYRICS = note.get("lyrics", "ら")
            # PIT_ARR = note.get("pitch",[0,0,0,0])
            # PIT_POS_ARR = note.get("pitch_pos",[0,50,100,150])
            # print POSTICK, DURTICK, NOTENUM, VELOCITY
            # note
            note = doc.createElement('note')
            # posTick
            posTick = doc.createElement('posTick')
            posTick_text = doc.createTextNode(unicode(POSTICK))
            posTick.appendChild(posTick_text)
            note.appendChild(posTick)
            # durTick
            durTick = doc.createElement('durTick')
            durTick_text = doc.createTextNode(unicode(DURTICK))
            durTick.appendChild(durTick_text)
            note.appendChild(durTick)
            # noteNum
            noteNum = doc.createElement('noteNum')
            noteNum_text = doc.createTextNode(unicode(NOTENUM))
            noteNum.appendChild(noteNum_text)
            note.appendChild(noteNum)
            # velocity
            velocity = doc.createElement('velocity')
            velocity_text = doc.createTextNode(unicode(VELOCITY))
            velocity.appendChild(velocity_text)
            note.appendChild(velocity)
# ======================歌詞
            # lyric
            lyric = doc.createElement('lyric')
            lyric_text = doc.createCDATASection(LYRICS)
            lyric.appendChild(lyric_text)
            note.appendChild(lyric)
            # phnms
            phnms = doc.createElement('phnms')
            phnms_text = doc.createCDATASection(miku_go.get(LYRICS, '4 a'))
            phnms.appendChild(phnms_text)
            note.appendChild(phnms)
# ======================
            # noteStyle
            noteStyle = doc.createElement('noteStyle')
            # attr accent
            attr = doc.createElement('attr')
            attr.setAttribute("id", "accent")
            attr_text = doc.createTextNode(u'50')
            attr.appendChild(attr_text)
            noteStyle.appendChild(attr)
            # attr bendDep
            attr = doc.createElement('attr')
            attr.setAttribute("id", "bendDep")
            attr_text = doc.createTextNode(u'8')
            attr.appendChild(attr_text)
            noteStyle.appendChild(attr)
            # attr bendLen
            attr = doc.createElement('attr')
            attr.setAttribute("id", "bendLen")
            attr_text = doc.createTextNode(u'0')
            attr.appendChild(attr_text)
            noteStyle.appendChild(attr)
            # attr decay
            attr = doc.createElement('attr')
            attr.setAttribute("id", "decay")
            attr_text = doc.createTextNode(u'50')
            attr.appendChild(attr_text)
            noteStyle.appendChild(attr)
            # attr fallPort
            attr = doc.createElement('attr')
            attr.setAttribute("id", "fallPort")
            attr_text = doc.createTextNode(u'0')
            attr.appendChild(attr_text)
            noteStyle.appendChild(attr)
            # attr opening
            attr = doc.createElement('attr')
            attr.setAttribute("id", "opening")
            attr_text = doc.createTextNode(u'127')
            attr.appendChild(attr_text)
            noteStyle.appendChild(attr)
            # attr risePort
            attr = doc.createElement('attr')
            attr.setAttribute("id", "risePort")
            attr_text = doc.createTextNode(u'0')
            attr.appendChild(attr_text)
            noteStyle.appendChild(attr)
            # attr vibLen
            attr = doc.createElement('attr')
            attr.setAttribute("id", "vibLen")
            attr_text = doc.createTextNode(u'0')
            attr.appendChild(attr_text)
            noteStyle.appendChild(attr)
            # attr vibType
            attr = doc.createElement('attr')
            attr.setAttribute("id", "vibType")
            attr_text = doc.createTextNode(u'0')
            attr.appendChild(attr_text)
            noteStyle.appendChild(attr)
            note.appendChild(noteStyle)
            musicalPart.appendChild(note)

            # pitch bend
            # dur = DURTICK//len(PIT_ARR)
            # for i,p in enumerate(PIT_ARR):
            #     musicalPart.appendChild(pitch_plot(POSTICK+dur*i,p))
# ==================================================

    vsTrack.appendChild(musicalPart)
    vsq3.appendChild(vsTrack)

# seTrack
    seTrack = doc.createElement('seTrack')
    seTrack_text = doc.createTextNode(u'')
    seTrack.appendChild(seTrack_text)
    vsq3.appendChild(seTrack)

# karaokeTrack
    karaokeTrack = doc.createElement('karaokeTrack')
    karaokeTrack_text = doc.createTextNode(u'')
    karaokeTrack.appendChild(karaokeTrack_text)
    vsq3.appendChild(karaokeTrack)

# aux
    aux = doc.createElement('aux')
    # auxID
    auxID = doc.createElement('auxID')
    auxID_text = doc.createCDATASection(u'AUX_VST_HOST_CHUNK_INFO')
    auxID.appendChild(auxID_text)
    aux.appendChild(auxID)
    # content
    content = doc.createElement('content')
    content_text = doc.createCDATASection(
        u'VlNDSwAAAAADAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA=')
    content.appendChild(content_text)
    aux.appendChild(content)
    vsq3.appendChild(aux)
    doc.appendChild(vsq3)

    return doc


json_header = {'tracks': 1,
               'resolution': 500,
               'pitch': [0],
               'pitch_pos': [500],
               'format': 1}


def create_note_json(tick: int, note_num: int, lyrics: str):
    noteOn = {'velocity': 80, 'tick': 0,
              'sub_type': 'noteOn', 'channel': 0, 'note_num': note_num}
    noteOff = {u'velocity': 0, u'tick': tick, u'sub_type': u'noteOff',
               u'channel': 0, u'note_num': note_num, u'lyrics': lyrics}
    return noteOn, noteOff


if __name__ == '__main__':
    pit = [np.ceil(-512*np.sin(2*np.pi*x/40)) for x in range(2000)]
    pit_pos = [x*5 for x in range(2000)]

    no_pitch_bend = False
    data, sr = librosa.load("vsqx/wav.wav", dtype=np.double)
    n_fft = 256
    hop_len = 128
    harvest = Harvest(fs=sr, n_fft=n_fft, hop_length=hop_len,
                      use_log_f0=False, use_token_averaged_f0=False)

    f0 = harvest.forward(data)

    kana, moras, times, frames = lab_analisys("vsqx/lab.lab")
    print(times)
    print(frames)
    mora_ave = [np.sum(f0[f[0]:f[1]])/len(f0[f[0]:f[1]]) for f in frames]
    print(mora_ave)

    # 周波数からmidiのノート番号を出す
    f2n = m21.pitch.Pitch()
    stream = []
    pit = []
    for time, f, lyrics in zip(times[1:-1], frames[1:-1], kana):
        note_freq = np.sum(f0[f[0]:f[1]])/len(f0[f[0]:f[1]])
        f2n.frequency = note_freq
        tick = int(time[1]*1000)-int(time[0]*1000)
        stream.extend(create_note_json(tick, f2n.midi, lyrics))

        pit.extend([np.log2(f0[i]/note_freq)*4096 for i in range(f[0], f[1])])

    stream[0]['tick'] = 500
    print(stream)
    offset = int(np.ceil(times[1][0]*1000))
    pit_pos = [offset+8*i for i in range(len(pit))]
    if no_pitch_bend:
        data = {**json_header, **{'stream': stream}}
    else:
        data = {**json_header, **{'stream': stream,
                                  'pitch': pit, 'pitch_pos': pit_pos}}

    doc = json2vsqx(data)
    bytes_data = doc.toprettyxml('', '', 'utf-8')
    with open("/home/user/host/files/test.vsqx", "wb") as f:
        f.write(bytes_data)
