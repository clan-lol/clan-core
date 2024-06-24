{ self, ... }:
{
  flake.templates = {
    new-clan = {
      description = "Initialize a new clan flake";
      path = ./new-clan;
    };
    empty = {
      description = "A empty clan template. Primarily for usage with the clan ui";
      path = ./empty;
    };
    default = self.templates.new-clan;
    minimal = {
      description = "for clans managed via (G)UI";
      path = ./minimal;
    };
  };
}
