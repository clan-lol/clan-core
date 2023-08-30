{ self, ... }: {
  flake.templates = {
    new-clan = {
      description = "Initialize a new clan flake";
      path = ./new-clan;
    };
    default = self.templates.new-clan;
  };
}
