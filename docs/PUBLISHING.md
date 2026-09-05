# Publishing this repository

Project repository: https://github.com/anatoliiii/pocknix-microphon

To publish a separate fork from an offline checkout, use your own remote URL:

```sh
git remote add origin YOUR_REPOSITORY_URL
git push -u origin master
```

If using the ZIP archive, unpack, `git init -b master`, add and commit first.
The Git bundle distributed alongside it can instead be cloned to preserve history.
Choose your own author identity for future commits. The documentation import commit uses
a generic project identity, not an account credential or the device owner's email.

Review the tracked file list before publishing. Do not add results/, recordings,
factory images/modules, system backup archives, complete journal dumps, private
paths or user identifiers. The .gitignore excludes common generated artifacts.

When reporting another device, use the issue template and state whether speech,
switched tones, clean kernel windows and a second boot were actually checked.
Do not describe merely nonzero PCM as success. If a new kernel contains a proper
channel-mask fix, document that state rather than backporting the local array
workaround over it. Include source/version context with any proposed patch update.
