# Compact historical output recovery

archives/working-output-022-recovery.tar.gz preserves every former output file,
including batch records, previews, historical preflights/diagnostics and current
assembly metadata. ACCEPTED_CLEANUP_PLAN.json records each file SHA256/size.
All archive members were streamed and verified against those hashes before
loose files were removed. Current source, models/voices and accepted ZIP stay
separate. Ordinary builds recreate output/current using tools/build.py.

To inspect: Python 3.13 tarfile.open(archive, "r:gz").getnames().
To restore these historical outputs under the existing Korea source, first ensure
output does not exist and the destination root is the intended existing checkout;
then use tarfile.open(archive, "r:gz").extractall(path=root, filter="data").
Members are regular files under output/ only. This is recovery evidence; old
preparation scripts may describe superseded versions and are not current release
entrypoints. Do not run an old recipe merely because its output was restored.
