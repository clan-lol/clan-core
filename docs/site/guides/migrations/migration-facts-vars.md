# Migrate modules from `facts` to `vars`.

For a high level overview about `vars` see our [blog post](https://clan.lol/blog/vars/).

This guide will help you migrate your modules that still use our [`facts`](../../manual/secrets.md) backend
to the [`vars`](../../manual/vars-backend.md) backend.

The `vars` [module](../../reference/clan-core/vars.md) and the clan [command](../../reference/cli/vars.md) work in tandem, they should ideally be kept in sync.

## Keep Existing Values

In order to keep existing values and move them from `facts` to `vars`
we will need to set the corresponding option in the vars module:

```
migrateFact = "fact-name"
```

This will now check on `vars` generation if there is an existing `fact` with the
name already present and if that is the case will migrate it to `vars`.

Let us look at the mapping a little closer.
Suppose we have the following fact: `facts.services.vaultwarden.secret.admin`.
This would read as follows: The `vaultwarden` `fact` service has the `admin` secret.
In order to migrate this fact we would need to have the following `vars` configuration:

```nix
vars.generators.vaultwarden = {
    migrateFact = "vaultwarden";
    files.admin = {};
};
```

And this would read as follows: The vaultwarden `vars` module generates the admin file.


## Prompts

Because prompts can be a necessity for certain systems `vars` have a shorthand for defining them.
A prompt is a request for user input. Let us look how user input used to be handled in facts:

```nix
facts.services.forgejo-api = {
    secret.token = {};
    generator.prompt = "Please insert your forgejo api token";
    generator.script = "cp $prompt_value > $secret/token";
};
```
To have analogous functionality in `vars`:
```nix
vars.generators.forgejo-api = {
    prompts.token = {
        description = "Please insert your forgejo api token"
        persist = true;
    };
};
```
This does not only simplify prompting, it also now allows us to define multiple prompts in one generator.
A more analogous way to the `fact` method is available, in case the module author needs more flexibility with the prompt input:

```nix
vars.generators.forgejo-api = {
    files.token = {};
    prompts.token.description = "Please insert your forgejo api token";
    script = "cp $prompts/<name> $out/<name>";
};
```

## Migration of a complete module

Let us look closer at how we would migrate an existing generator for syncthing.
This is the `fact` module of syncthing:

```nix
facts.services.syncthing = {
  secret.key = {};
  secret.cert = {};
  public.id = {};

  generator.path = [
    pkgs.coreutils
    pkgs.gnugrep
    pkgs.syncthing
  ];

  generator.script = ''
    syncthing generate --config "$out"
    mv "$out"/key.pem "$secret"/key
    mv "$out"/cert.pem "$secret"/cert
    cat "$out"/config.xml | grep -oP '(?<=<device id=")[^"]+' | uniq > "$public"/id
  '';
};
```


This would be the corresponding `vars` module, which also will migrate existing facts.
```nix
vars.generators.syncthing = {
  migrateFact = "syncthing";

  files.key = {};
  files.cert = {};
  files.id.secret = false;

  runtimeInputs = [
    pkgs.coreutils
    pkgs.gnugrep
    pkgs.syncthing
  ];

  script = ''
    syncthing generate --config "$out"
    mv "$out"/key.pem "$out"/key
    mv "$out"/cert.pem "$out"/cert
    cat "$out"/config.xml | grep -oP '(?<=<device id=")[^"]+' | uniq > "$out"/id
  '';
};
```
Most of the usage patterns stay the same, but `vars` have a more ergonomic interface.
There are not two different ways to define files anymore (public/secret).
Now files are defined under the `files` attribute and are secret by default.


## Happy Migration

We hope this gives you a clear path to start and finish your migration from `facts` to `vars`.
Please do not hesitate reaching out if something is still unclear - either through [matrix](https://matrix.to/#/#clan:clan.lol) or through our git [forge](https://git.clan.lol/clan/clan-core).
