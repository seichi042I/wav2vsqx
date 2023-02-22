# -*- coding: utf-8 -*-
import subprocess
from subprocess import PIPE


import numpy as np
import librosa
import music21 as m21
from xml.dom import minidom
from pathlib import Path

from f0_extractor.pitch_extract import Harvest
from utils import *


def json2doc(data):
    doc = minidom.parse(str(Path(__file__).parent / "vsqx_frame.xml"))

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
            posTick_text = doc.createTextNode(str(POSTICK))
            posTick.appendChild(posTick_text)
            note.appendChild(posTick)
            # durTick
            durTick = doc.createElement('durTick')
            durTick_text = doc.createTextNode(str(DURTICK))
            durTick.appendChild(durTick_text)
            note.appendChild(durTick)
            # noteNum
            noteNum = doc.createElement('noteNum')
            noteNum_text = doc.createTextNode(str(NOTENUM))
            noteNum.appendChild(noteNum_text)
            note.appendChild(noteNum)
            # velocity
            velocity = doc.createElement('velocity')
            velocity_text = doc.createTextNode(str(VELOCITY))
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


def wav2vsqx(
    data_dirpath: Path,
    out_filepath: Path,
    no_pitch_bend: bool = False,
    n_fft: int = 512,
    hop_length: int = 256
):

    g2p_julius(data_dirpath / "text", data_dirpath / "segmentation/text")
    proc = subprocess.Popen(f"cd {Path(__file__).parent}/data/ && "+"ls | while read file;do sox $file -r 16000 -c 1 -b 16 ./segmentation/audio/$file;echo '${file} is converted.'; done", shell=True, stdout=PIPE,
                            stderr=PIPE, text=True)
    proc = subprocess.Popen(f"cd {Path(__file__).parent}/segmentation-kit-4.3.1 && perl segment_julius.pl", shell=True, stdout=PIPE,
                            stderr=PIPE, text=True)

    date = proc.stderr
    print('STDOUT: {}'.format(date))

    data, sr = librosa.load(data_dirpath / "voice.wav", dtype=np.double)

    harvest = Harvest(fs=sr, n_fft=n_fft, hop_length=hop_length,
                      use_log_f0=False, use_token_averaged_f0=False,
                      f0min=300,
                      f0max=800)

    f0 = harvest.forward(data)

    spf = hop_length/sr
    kana, times, frames, offset = lab_analisys(
        data_dirpath, spf=spf)

    # create stream array
    f2n = m21.pitch.Pitch()
    stream = []
    pit = []
    for lyrics, time, f in zip(kana, times, frames):
        mora_freqs = f0[f[0]:f[1]]
        note_freq = np.sum(mora_freqs)/len(mora_freqs)
        f2n.frequency = note_freq
        tick = int(time[1]*1000)-int(time[0]*1000)

        stream.extend(create_note_json(tick, f2n.midi, lyrics))
        pit.extend([np.log2(mf/note_freq)*4096 for mf in mora_freqs])

    stream[0]['tick'] = offset
    pit_pos = [offset+int(spf*i*1000) for i in range(len(pit))]

    # create json
    if no_pitch_bend:
        json = {**json_header, **{'stream': stream}}
    else:
        json = {**json_header, **{'stream': stream,
                                  'pitch': pit, 'pitch_pos': pit_pos}}

    # json to xmldoc
    doc = json2doc(json)

    # save to vsqx file
    bytes_data = doc.toprettyxml('', '', 'utf-8')
    with open("/home/user/host/files/test.vsqx", "wb") as f:
        f.write(bytes_data)


wav2vsqx(Path(f'{__file__}').parent / 'data', Path("/home/user/host"))
