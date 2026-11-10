"""
gerar_musica.py — trilhas instrumentais originais (sem direitos autorais), geradas por codigo.

Estilos:
  house  — dance animado, 124 BPM, Do maior (C-G-Am-F), bumbo em 4, hats fora do tempo, riser
  funk   — pop-funk saltitante, 112 BPM, Sol maior (G-D-Em-C), baixo sincopado, stabs, swing

Uso: python gerar_musica.py <estilo> saida.wav [duracao_segundos]
"""
import sys, wave
import numpy as np

SR = 44100
rng = np.random.default_rng(11)


def midi(n):
    return 440.0 * 2 ** ((n - 69) / 12)


def env(n, a=0.005, d=0.2):
    t = np.arange(n) / SR
    return np.minimum(t / a, 1) * np.exp(-t / d)


def kick(n=int(SR * 0.32), punch=1.0):
    t = np.arange(n) / SR
    f = 48 + 140 * np.exp(-t * 32)
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 10) * 1.15 * punch


def hat(n=int(SR * 0.05), open_=False):
    n = int(SR * (0.22 if open_ else 0.05))
    x = np.diff(rng.standard_normal(n), prepend=0)
    return x * np.exp(-np.arange(n) / SR * (22 if open_ else 95)) * (0.16 if open_ else 0.17)


def clap(n=int(SR * 0.2)):
    x = rng.standard_normal(n)
    x = x - np.convolve(x, np.ones(8) / 8, "same")
    t = np.arange(n) / SR
    return x * (np.exp(-t * 26) + 0.7 * np.exp(-((t - 0.011) ** 2) * 8000)) * 0.38


def riser(dur):
    n = int(dur * SR)
    x = np.diff(rng.standard_normal(n), prepend=0)
    return x * (np.linspace(0, 1, n) ** 2.2) * 0.22


def saw(freq, n, a=0.004, d=0.18, harm=6, amp=1.0):
    t = np.arange(n) / SR
    y = sum(np.sin(2 * np.pi * freq * k * t) / k for k in range(1, harm + 1))
    return y * env(n, a, d) * amp


def tone(freq, n, harm=(1, .5, .25), a=0.01, d=0.25):
    t = np.arange(n) / SR
    y = sum(h * np.sin(2 * np.pi * freq * (i + 1) * t) for i, h in enumerate(harm))
    return y * env(n, a, d)


def add(L, R, sig, start, pan=0.5):
    i = int(start * SR)
    if i >= len(L) or i < 0:
        return
    j = min(len(L), i + len(sig))
    L[i:j] += sig[: j - i] * (1 - pan) * 1.4
    R[i:j] += sig[: j - i] * pan * 1.4


def finish(L, R, N):
    out = np.stack([L[:N], R[:N]], axis=1)
    fi = int(0.04 * SR); fo = int(2.0 * SR)
    out[:fi] *= np.linspace(0, 1, fi)[:, None]
    out[-fo:] *= np.linspace(1, 0, fo)[:, None]
    out = np.tanh(out * 1.5)
    return out * (0.89 / np.max(np.abs(out)))


def house(dur):
    BEAT = 60 / 124; bar = BEAT * 4
    N = int(dur * SR); L = np.zeros(N); R = np.zeros(N)
    prog = [(48, [60, 64, 67]), (55, [59, 62, 67]), (45, [57, 60, 64]), (53, [57, 60, 65])]  # C G Am F
    lead = {0: [76, 79, 76, 74], 1: [74, 79, 74, 71], 2: [72, 76, 72, 69], 3: [72, 77, 76, 72]}
    for b in range(int(dur / bar) + 2):
        root, chord = prog[b % 4]
        t0 = b * bar
        intro = b < 2
        drop = b >= 4
        # acordes em stabs fora do tempo
        for off in (0.5, 1.5, 2.5, 3.5):
            if intro and off > 1.6:
                continue
            for note in chord:
                add(L, R, saw(midi(note), int(0.22 * SR), d=0.07, harm=4, amp=0.07), t0 + off * BEAT, 0.5)
        # arpejo/lead em colcheias (gancho)
        mel = lead[b % 4]
        for s in range(8):
            note = mel[s % 4] + (12 if s >= 4 and drop else 0)
            add(L, R, tone(midi(note), int(0.3 * SR), harm=(1, .55, .3, .15), a=0.003, d=0.1) * 0.15,
                t0 + s * BEAT / 2, 0.35 + 0.3 * (s % 2))
        if intro:
            for beat in range(4):
                add(L, R, hat() * 0.8, t0 + beat * BEAT + BEAT / 2)
            continue
        if b % 4 == 3 and not drop:  # riser antes do drop
            add(L, R, riser(2 * BEAT), t0 + 2 * BEAT)
        for beat in range(4):
            tb = t0 + beat * BEAT
            add(L, R, kick(), tb, 0.5)                       # bumbo em 4
            add(L, R, hat(open_=True) * 1.0, tb + BEAT / 2)  # hat aberto fora do tempo
            for q in (0, 0.25, 0.75):
                add(L, R, hat() * 0.5, tb + q * BEAT, 0.5 + 0.2 * (q > 0.5))
            if beat in (1, 3):
                add(L, R, clap(), tb)
            # baixo fora do tempo
            add(L, R, saw(midi(root - 12), int(0.25 * SR), d=0.11, harm=5, amp=0.30), tb + BEAT / 2)
    return finish(L, R, N)


def funk(dur):
    BEAT = 60 / 112; bar = BEAT * 4
    swing = 0.12 * BEAT / 2
    N = int(dur * SR); L = np.zeros(N); R = np.zeros(N)
    prog = [(43, [55, 59, 62]), (50, [57, 62, 66]), (40, [55, 59, 64]), (48, [55, 60, 64])]  # G D Em C
    hook = {0: [79, 83, 86, 83], 1: [78, 81, 86, 81], 2: [76, 79, 83, 79], 3: [79, 84, 83, 79]}
    for b in range(int(dur / bar) + 2):
        root, chord = prog[b % 4]
        t0 = b * bar
        intro = b < 1
        for s in range(8):  # gancho em colcheias com swing
            note = hook[b % 4][s % 4]
            ts = t0 + s * BEAT / 2 + (swing if s % 2 else 0)
            add(L, R, tone(midi(note), int(0.28 * SR), harm=(1, .5, .35, .2), a=0.002, d=0.09) * 0.17, ts, 0.3 + 0.4 * (s % 2))
        for pos in (1.5, 3, 3.5):  # stabs
            if intro:
                continue
            for note in chord:
                add(L, R, saw(midi(note), int(0.18 * SR), d=0.06, harm=5, amp=0.075), t0 + pos * BEAT, 0.5)
        if intro:
            for beat in range(4):
                add(L, R, hat() * 0.8, t0 + beat * BEAT)
            continue
        for beat in range(4):
            tb = t0 + beat * BEAT
            if beat in (0, 2):
                add(L, R, kick(), tb, 0.5)
            if beat in (1, 3):
                add(L, R, clap(), tb)
            for q in range(4):  # hats em 16 com swing
                add(L, R, hat() * (1.0 if q % 2 == 0 else 0.55), tb + q * BEAT / 4 + (swing / 2 if q % 2 else 0), 0.5)
        add(L, R, kick() * 0.9, t0 + 1.5 * BEAT, 0.5)  # bumbo sincopado
        # baixo funk
        for pos, off in ((0, 0), (0.75, 0), (1.5, 12), (2.5, 0), (3.25, 7), (3.75, 0)):
            add(L, R, saw(midi(root - 12 + off), int(0.2 * SR), d=0.09, harm=4, amp=0.36), t0 + pos * BEAT, 0.5)
    return finish(L, R, N)


ESTILOS = {"house": house, "funk": funk}

if __name__ == "__main__":
    estilo, dst = sys.argv[1], sys.argv[2]
    dur = float(sys.argv[3]) if len(sys.argv) > 3 else 34
    y = (ESTILOS[estilo](dur) * 32767).astype(np.int16)
    with wave.open(dst, "wb") as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes(y.tobytes())
    print(f"OK {estilo} -> {dst} ({dur:.1f}s)")
