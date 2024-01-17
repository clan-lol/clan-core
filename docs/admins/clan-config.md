# cLAN config

`clan config` allows you to manage your nixos configuration via the terminal.
Similar as how `git config` reads and sets git options, `clan config` does the same with your nixos options
It also supports auto completion making it easy to find the right options.

## Set up clan-config

Add the clan tool to your flake inputs:

```
clan.url = "git+https://git.clan.lol/clan/clan-core";
```

and inside the mkFlake:

```
imports = [
  inputs.clan.flakeModules.clan-config
];
```

Add an empty config file and add it to git

```command
echo "{}" > ./clan-settings.json
git add ./clan-settings.json
```

Import the clan-config module into your nixos configuration:

```nix
{
  imports = [
    # clan-settings.json is located in the same directory as your flake.
    # Adapt the path if necessary.
    (builtins.fromJSON (builtins.readFile ./clan-settings.json))
  ];
}


```

Make sure your nixos configuration is set a default

```nix
{self, ...}: {
  flake.nixosConfigurations.default = self.nixosConfigurations.my-machine;
}
```

Use all inputs provided by the clan-config devShell in your own devShell:

```nix
{ ... }: {
  perSystem = { pkgs, self', ... }: {
    devShells.default = pkgs.mkShell {
      inputsFrom = [ self'.devShells.clan-config ];
      # ...
    };
  };
}
```

re-load your dev-shell to make the clan tool available.

```command
clan config --help
```
