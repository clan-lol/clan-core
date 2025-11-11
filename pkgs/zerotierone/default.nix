{
  zerotierone,
  stdenv,
  lib,
  includeController ? false,
}:
# halalify zerotierone
(
  # ZeroTier 1.16+ requires building with controller support when controller is enabled
  if includeController && lib.versionAtLeast zerotierone.version "1.16" then
    zerotierone.override { enableUnfree = true; }
  else
    zerotierone
).overrideAttrs
  (old: {
    # Maybe a sandbox issue?
    # zerotierone> [phy] Binding UDP listen socket to 127.0.0.1/60002... FAILED.
    doCheck = old.doCheck && !stdenv.hostPlatform.isDarwin;
    meta = old.meta // {
      license = lib.licenses.apsl20;
    };
  })
