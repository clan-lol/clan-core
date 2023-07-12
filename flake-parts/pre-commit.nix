{ self, ... }: {
  pre-commit.settings.hooks.alejandra.enable = true;
  pre-commit.settings.hooks.shellcheck.enable = true;
}
