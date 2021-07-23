# Svengali GUI authoring tool for Teddy Ruxpin tapes
# 2021 furrtek

from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt
from functools import partial
import pyaudio
import wave
import math
import struct
import time
import sys

# Frame repetition rate: 16.6ms ~60Hz
# Pulse width: 400us
# Shortest gap: 630us
# Longest gap: 1590us

# Channel 1: Unused
# Channel 2: Teddy's eyes
# Channel 3: Teddy's upper jaw
# Channel 4: Teddy's lower jaw
# Channel 5: Audio routing
# Channel 6: Grubby's eyes
# Channel 7: Grubby's upper jaw
# Channel 8: Grubby's lower jaw

track_duration = 2
audio_rate = 44100
frame_length = int(audio_rate * 16.6 / 1000)
pulse_length = int(audio_rate * 0.400 / 1000)
gap_min = int(audio_rate * 0.630 / 1000)
gap_max = int(audio_rate * 1.590 / 1000)

#p = pyaudio.PyAudio()

#gap_lengths = [30, 32, 35, 37, 40, 42, 44, 52]
gap_lengths = [0] * 8

def callback(in_data, frame_count, time_info, status):
    global current_channel, pulse_timer, gap_timer, frame_timer
    global frame_length, pulse_length, phase

    data = ''
    for s in range(0, frame_count):
        if frame_timer == frame_length:
            # 27 ~ 70
            #gap_lengths[1] = int(gap_min + 21 + math.sin(phase) * 22)
            #gap_lengths[2] = int(gap_min + 21 + math.sin(phase*1.1) * 22)
            #gap_lengths[5] = int(gap_min + 21 + math.sin(phase*2.3) * 22)
            phase += 0.1
            frame_timer = 0
            current_channel = 0
            pulse_timer = 0
            gap_timer = 0

        if pulse_timer == pulse_length:
            v = 127
            if current_channel < 8:
                if gap_timer == gap_lengths[current_channel]:
                    pulse_timer = 0
                    gap_timer = 0
                    current_channel += 1
                else:
                    if (current_channel < 8):
                        gap_timer += 1
        else:
            v = 127+80
            pulse_timer += 1

        frame_timer += 1

        wf.writeframesraw(struct.pack('>h', v))

        #v = int(127 + math.cos(phase) * 127)
        data += chr(v)
        data += chr(0)  #v and 255)
    return (data, pyaudio.paContinue)
    

def genAudio():
    current_channel = 0
    pulse_timer = 0
    gap_timer = 0
    frame_timer = 0

    wf = wave.open('out.wav', 'wb')
    wf.setnchannels(1)  # Mono
    wf.setsampwidth(1)  # UInt8
    wf.setframerate(audio_rate)

    for s in range(0, track_duration * audio_rate):
        if frame_timer == frame_length:
            frame_timer = 0
            current_channel = 0
            pulse_timer = 0
            gap_timer = 0

        if pulse_timer == pulse_length:
            v = 127
            if gap_timer == gap_length:
                pulse_timer = 0
                gap_timer = 0
                current_channel += 1
            else:
                if (current_channel < 8):
                    gap_timer += 1
        else:
            v = 127+80
            pulse_timer += 1
            if pulse_timer == pulse_length:
                # One-shot
                if current_channel < 8:
                    gap_length = gap_min + int(gap_lengths[current_channel] * 0.3)
                else:
                    gap_length = frame_length   # Make sure signal is 0 until end of the frame

        frame_timer += 1

        wf.writeframesraw(struct.pack('B', v))  # >h

    wf.close()

    
def test_func(iname, ch):
    v = widgets[iname].value()
    # print("ch %u: %u" % (ch, v))
    gap_lengths[ch] = v   #int(gap_min + slider_teddy_eyes.value())

def addSliders(box, offs):
    sliders = {'Eyes': (0, 100, 0),
                'Upper jaw': (0, 100, 1),
                'Lower jaw': (0, 100, 2)
    }

    for wname, params in sliders.items():
        iname = wname + str(offs)

        widgets[iname + '_lbl'] = QLabel(wname + ':')
        box.addWidget(widgets[iname + '_lbl'])

        widgets[iname] = QSlider(Qt.Horizontal)
        widgets[iname].setMinimum(params[0])
        widgets[iname].setMaximum(params[1])
        box.addWidget(widgets[iname])
        widgets[iname].sliderMoved.connect(partial(test_func, iname, offs + params[2]))


#stream = p.open(format = pyaudio.paInt16,
#                channels = 1,
#                rate = 44100,
#                output = True,
#                frames_per_buffer = 2048,
#                stream_callback = callback)
#stream.stop_stream()

app = QApplication([])

layout = QVBoxLayout()  # Window layout
w = QWidget()

w.setLayout(layout)
w.setWindowTitle("Svengali")

gb_teddy = QGroupBox("Teddy")
layout.addWidget(gb_teddy)
gb_grubby = QGroupBox("Grubby")
layout.addWidget(gb_grubby)

widgets = {}

vbox_teddy = QVBoxLayout()
gb_teddy.setLayout(vbox_teddy)
vbox_grubby = QVBoxLayout()
gb_grubby.setLayout(vbox_grubby)

addSliders(vbox_teddy, 1)
addSliders(vbox_grubby, 5)

layout.addWidget(QLabel('Who speaks ?'))
w_routing = QWidget()
layout.addWidget(w_routing)
hbox_routing = QHBoxLayout()
w_routing.setLayout(hbox_routing)
hbox_routing.addWidget(QCheckBox('Teddy'))
hbox_routing.addWidget(QCheckBox('Grubby'))

btn_gen = QPushButton('Gen audio')
layout.addWidget(btn_gen)
btn_gen.clicked.connect(genAudio)

w.show()

#stream.start_stream()

app.exec()

#while stream.is_active():
#    time.sleep(0.1)

#time.sleep(track_duration)

#stream.stop_stream()
#stream.close()
#p.terminate()
