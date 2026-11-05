# Garrison 0.1.13 shared audio startup failure

Korea and Berber both queue voices but the normal client never starts their
playback process after native readiness fails. Current channels report none /
no_consumer. The former successful session 5232 logged backend pid 11312 and
played Berber clips. Failed Korea session 26976 logs actual Korean PBG matches
and queued select/move cues; failed Berber session 19724 also reports no_consumer.

The matching installed audio-backend SHA256 is
ba2df897f800e4c753f088fcb6a8ef2bf2baca8633fe64a273746131a24d0415.
Four Korean Vorbis clips successfully decode/admit with that unmodified backend
using a dummy process ID, documented named pipe and gain zero. This is not an
audible test or a workaround launcher. Both archives are recognized as carrying
audio. Their bundle/channel keys match their respective scripts.

The guide says the normal client starts the backend for staged archives with
audio; the mod supplies clips, matching SCAR helpers and script session/cues.
Korea 0.2.2 repairs its missing helper member and speech-volume declaration.
This cannot create a missing client-owned playback process. Do not rewrite or
reencode thousands of voices to conceal this external launch failure.

Investigate the client readiness/retention/mount path and start-backend ordering.
A four-owner startup delay is only a hypothesis; a one-mod run is not yet available.
Keep ordinary import-and-Play support, matching client/agent/backend, and game
integrity. No native loose-audio installer, private player launcher or automatic
process attachment is part of this report. No telemetry was sent externally.
