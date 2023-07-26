# export some of our flake moduels for re-use in other projects
{ ...
}: {
  flake.modules.flake-parts = {
    writers = ./writers;
  };
}
