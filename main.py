# Svengali GUI authoring tool for Teddy Ruxpin tapes
# 2021 furrtek

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

wf = wave.open('out.wav', 'wb')
wf.setnchannels(1)
wf.setsampwidth(1)
wf.setframerate(44100)

p = pyaudio.PyAudio()

current_channel = 0
pulse_timer = 0
gap_timer = 0
frame_timer = 0
phase = 0

gap_length = [30, 32, 35, 37, 40, 42, 44, 52]

def callback(in_data, frame_count, time_info, status):
    global current_channel, pulse_timer, gap_timer, frame_timer
    global frame_length, pulse_length, phase

    data = ''
    for s in range(0, frame_count):
        if frame_timer == frame_length:
            # 27 ~ 70
            gap_length[1] = int(gap_min + 21 + math.sin(phase) * 22)
            gap_length[2] = int(gap_min + 21 + math.sin(phase*1.1) * 22)
            gap_length[5] = int(gap_min + 21 + math.sin(phase*2.3) * 22)
            phase += 0.1
            frame_timer = 0
            current_channel = 0
            pulse_timer = 0
            gap_timer = 0

        if pulse_timer == pulse_length:
            v = 127
            if current_channel < 8:
                if gap_timer == gap_length[current_channel]:
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

        wf.writeframesraw(struct.pack('B', v))

        #v = int(127 + math.cos(phase) * 127)
        data += chr(v)
        #data += chr(v and 255)
    return (data, pyaudio.paContinue)

stream = p.open(format = pyaudio.paUInt8,
                channels = 1,
                rate = 44100,
                output = True,
                stream_callback = callback)

stream.start_stream()

#while stream.is_active():
#    time.sleep(0.1)

time.sleep(track_duration)

stream.stop_stream()
stream.close()
wf.close()

p.terminate()
