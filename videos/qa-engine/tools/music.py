# Original upbeat music bed for the intro video, synthesized from plain tones and noise
# (no samples). Writes music.wav next to this script; convert it to
# assets/audio/music/bed.mp3 with ffmpeg. Needs numpy.
import os
import wave

import numpy as np

SR = 44100
BPM = 112
BEAT = 60 / BPM
TOTAL = 57.0
rng = np.random.default_rng(7)  # fixed seed: the same file every run


def midi(n):
    return 440.0 * 2 ** ((n - 69) / 12)


def tone(f, dur, amp, decay, shape="pluck"):
    t = np.arange(int(SR * dur)) / SR
    env = np.exp(-t * decay) * np.minimum(1, t / 0.005)
    if shape == "pad":
        env = np.minimum(1, t / 0.4) * np.exp(-t * decay)
        w = np.sin(2 * np.pi * f * t) + 0.5 * np.sin(2 * np.pi * f * 1.003 * t) + 0.25 * np.sin(2 * np.pi * 2 * f * t)
    else:
        w = np.sin(2 * np.pi * f * t) + 0.3 * np.sin(2 * np.pi * 2 * f * t) * np.exp(-t * 8)
    return amp * env * w


def kick(amp):
    t = np.arange(int(SR * 0.35)) / SR
    f = 110 * np.exp(-t * 18) + 45
    return amp * np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 9)


def hat(amp):
    t = np.arange(int(SR * 0.06)) / SR
    n = rng.standard_normal(len(t))
    n = np.diff(n, prepend=0)  # crude high-pass
    return amp * n * np.exp(-t * 70)


out = np.zeros(int(SR * (TOTAL + 2)))


def place(t, s):
    i = int(t * SR)
    out[i:i + len(s)] += s[: len(out) - i]


# I - V - vi - IV in D major, one chord per bar
chords = [[62, 66, 69], [69, 73, 76], [71, 74, 78], [67, 71, 74]]
bass = [38, 45, 47, 43]
bar = 4 * BEAT
nbars = int(TOTAL // bar) + 1
for b in range(nbars):
    start = b * bar
    k = b % 4
    for n in chords[k]:
        place(start, tone(midi(n - 12), bar * 1.1, 0.05, 0.6, "pad"))
    for step in range(8):  # eighth-note pluck arpeggio
        n = chords[k][step % 3] + (12 if step in (3, 7) else 0)
        place(start + step * BEAT / 2, tone(midi(n), 0.6, 0.07, 7))
    for beat in range(4):
        place(start + beat * BEAT, tone(midi(bass[k]), BEAT * 0.9, 0.16, 3))
        if b > 0:  # drums come in after the first bar
            place(start + beat * BEAT, kick(0.35))
            place(start + beat * BEAT + BEAT / 2, hat(0.05))

out = out[: int(SR * TOTAL)]
fi, fo = int(SR * 0.8), int(SR * 2.5)
out[:fi] *= np.linspace(0, 1, fi)
out[-fo:] *= np.linspace(1, 0, fo)
out = out / np.max(np.abs(out)) * 0.7
pcm = (out * 32767).astype(np.int16)
path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "music.wav")
with wave.open(path, "wb") as w:
    w.setnchannels(2)
    w.setsampwidth(2)
    w.setframerate(SR)
    w.writeframes(np.repeat(pcm[:, None], 2, axis=1).tobytes())
print("wrote", path, len(out) / SR, "s")
