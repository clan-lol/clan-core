system:
builtins.fetchurl {
  url = "https://git.clan.lol/clan/test-fixtures/raw/commit/4a2bc56d886578124b05060d3fb7eddc38c019f8/nixos-vm-facter-json/${system}.json";
  sha256 =
    {
      aarch64-linux = "sha256:1rlfymk03rmfkm2qgrc8l5kj5i20srx79n1y1h4nzlpwaz0j7hh2";
      x86_64-linux = "sha256:16myh0ll2gdwsiwkjw5ba4dl23ppwbsanxx214863j7nvzx42pws";
    }
    .${system};
}
