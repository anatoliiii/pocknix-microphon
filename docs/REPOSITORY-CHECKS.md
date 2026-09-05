# Checks performed before publication

- Applied 0001 + 0002 to the original local WCD preimage; output matches the
  acoustically validated module source byte-for-byte.
- Checked optional 0003 against a reconstructed stereo preimage; output matches
  tested mono logic (with a corrected explanatory comment).
- Ran stage-module.py against the matching source and completed external-module
  compilation and MODPOST using the original build tree. Not installed again.
- Offline unittest: synthesized two switched tone windows, verified silence,
  1 kHz amplitude, rejection of stereo input. No hardware accessed by those tests.
- Python syntax, relative Markdown links and private-path checks passed.
- No raw audio, binaries, device images, backup archives, boot IDs or full logs
  included in Git. Publication helpers are distinct from local acceptance scripts.

Run offline checks yourself: `python3 -m unittest discover -s tests -v`.
These checks do not replace device testing; see VALIDATION.md.
