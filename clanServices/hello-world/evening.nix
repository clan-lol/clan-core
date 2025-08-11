{
  roles.evening.perInstance =
    { settings, ... }:
    {
      nixosModule =
        { ... }:
        {
          imports = [ ];
          environment.etc.hello.text = "${settings.greeting} World!";
        };
    };
}
