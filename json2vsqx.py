# -*- coding: utf-8 -*-

import numpy as np
import librosa
import music21 as m21
from xml.dom import minidom
from pathlib import Path

from f0_extractor.pitch_extract import Harvest
from utils import *
unicode = str


def json2vsqx(data):
    doc = minidom.parse("vsqx_frame.xml")

    musicalPart = doc.getElementsByTagName('musicalPart')[0]
    vsTrack = doc.getElementsByTagName('vsTrack')[0]


# ==========ここから楽譜============================
    # pitch
    musicalPart.appendChild(set_pitch_bend_sensitivity(doc, 12))
    for pit, pos in zip(data['pitch'], data['pitch_pos']):
        musicalPart.appendChild(pitch_plot(doc, pos, pit))
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
            phnms_text = doc.createCDATASection(kana2mkp(LYRICS))
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
# ==================================================

    vsTrack.appendChild(musicalPart)

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
    data, sr = librosa.load("data/voice.wav", dtype=np.double)
    n_fft = 256
    hop_length = 128
    harvest = Harvest(fs=sr, n_fft=n_fft, hop_length=hop_length,
                      use_log_f0=False, use_token_averaged_f0=False)

    f0 = harvest.forward(data)

    kana, moras, times, frames = lab_analisys(
        Path("data"), spf=(hop_length/sr))
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
