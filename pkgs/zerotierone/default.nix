{
  zerotierone,
  stdenv,
  lib,
}:
# halalify zerotierone
zerotierone.overrideAttrs (old: {
  # Maybe a sandbox issue?
  # zerotierone> [phy] Binding UDP listen socket to 127.0.0.1/60002... FAILED.
  doCheck = old.doCheck && !stdenv.hostPlatform.isDarwin;
  meta = old.meta // {
    license = lib.licenses.apsl20;
  };
})
