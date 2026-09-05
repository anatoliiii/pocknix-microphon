# Published aggregate measurements

PCM is signed 16-bit mono, 48 kHz. No raw recordings or boot identifiers included.

- boot1-tones: rows [second, RMS, 1 kHz amplitude].
- boot1-voice and boot2-voice: rows [second, min, max, RMS].
- boot2-tones: objects with second, RMS and amplitudes at 900/1000/1100 Hz.

Amplitude uses a one-second rectangular-window Goertzel calculation, expressed
in PCM counts. RMS includes DC. These are measured values, not pass thresholds.
No new kernel messages appeared in these four normal capture windows. A separate
diagnostic run with master dumps produced FIFO underflows and is explicitly
excluded from the claim of clean ordinary capture. See docs/VALIDATION.md.
