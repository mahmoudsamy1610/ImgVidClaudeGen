# Original music-box lullaby, synthesized from plain tones (no samples).
import numpy as np, wave
SR = 44100
BPM = 96
BEAT = 60 / BPM
TOTAL = 58.0
N = lambda name: {"C":0,"D":2,"E":4,"F":5,"G":7,"A":9,"B":11}[name[0]] + (1 if "#" in name else 0) + 12 * (int(name[-1]) + 1)
freq = lambda m: 440.0 * 2 ** ((m - 69) / 12)

def pluck(f, dur, amp):
    t = np.arange(int(SR * dur)) / SR
    env = np.exp(-t * 3.2) * np.minimum(1, t / 0.004)
    tone = (np.sin(2*np.pi*f*t) + 0.35*np.sin(2*np.pi*2*f*t) * np.exp(-t*6)
            + 0.12*np.sin(2*np.pi*3.01*f*t) * np.exp(-t*9))
    return amp * env * tone

out = np.zeros(int(SR * (TOTAL + 3)))
def place(t, f, dur, amp):
    i = int(t * SR); s = pluck(f, dur, amp); out[i:i+len(s)] += s[:len(out)-i]

# 8-bar phrase, melody in eighths ("." = rest), chords C Am F G C Am F G->C
melody = [
 "E5 . G5 . C6 . G5 .", "A5 . G5 . E5 . . .", "F5 . A5 . C6 . A5 .", "G5 . F5 . D5 . . .",
 "E5 . G5 . C6 . D6 .", "C6 . A5 . E5 . . .", "F5 . E5 . D5 . G5 .", "C5 . . . . . . .",
]
chords = [["C3","G3","E4"],["A2","E3","C4"],["F2","C3","A3"],["G2","D3","B3"]] * 2
chords[7] = ["C3","G3","E4"]
bar = 4 * BEAT
t0 = 0.6
bars_total = int((TOTAL - t0) // bar)
for b in range(bars_total):
    k = b % 8
    start = t0 + b * bar
    for j, note in enumerate(melody[k].split()):
        if note != ".":
            place(start + j * BEAT / 2, freq(N(note)), 2.2, 0.20)
    for j, note in enumerate(chords[k]):  # gentle rolled arpeggio
        place(start + j * BEAT, freq(N(note)), 2.6, 0.13)
        place(start + (2.5 + j * 0.5) * BEAT, freq(N(note)), 2.0, 0.07)

out = out[:int(SR * TOTAL)]
fade_in, fade_out = int(SR * 1.5), int(SR * 4.0)
out[:fade_in] *= np.linspace(0, 1, fade_in)
out[-fade_out:] *= np.linspace(1, 0, fade_out)
out = out / np.max(np.abs(out)) * 0.7
pcm = (out * 32767).astype(np.int16)
stereo = np.repeat(pcm[:, None], 2, axis=1)
with wave.open("musicbox.wav", "wb") as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes(stereo.tobytes())
print("ok", len(out) / SR)
