{ clanLib, lib }:
{
  test_minimal_generator =
    let
      eval = clanLib.clan {
        # Inject exports from the top-level
        exports.":::" = {
          # Inject contract for testing
          imports = [
            ../../modules/clan/export-modules/generators.nix
          ];
          generators.one =
            { config, ... }:
            {
              runtimeInputs = [ config.pkgs.hello ];
              files.file1 = { };
              prompts.prompt1 = { };
              dependencies.B = {
                _type = "vars.dependency";
                exportKey = "serviceA:instanceA1:client:jon";
                generator = "B";
              };
              script = ''
                hello > $out/file1
              '';
            };
        };

        directory = ./.;
        self = {
          clan = eval.config;
          inputs = { };
        };

      };

      # The resulting generator mapped to a "x86_64-linux" system
      generator = eval.config.clanInternals.systems.x86_64-linux.exports.":::".generators.one;
    in
    {
      inherit eval generator;
      expr = {
        # Force the 'list [ <thunk> ] -> list [ <derivation> ]' - in the runtimeInputs to make sure
        # Depending on pkgs is possible. If not, this would raise an error
        runtimeInputsEvaluates = lib.seq (map (thunk: lib.seq thunk true) generator.runtimeInputs) true;

        # Strict checks
        inherit (generator)
          name
          dependencies
          prompts
          ;

        # Things that can only be shallowly checked (type)
        scriptIsString = lib.isString generator.script;
        finalScriptIsDerivation = lib.isDerivation generator.finalScript;
        pkgsIsAttrs = lib.isAttrs generator.pkgs;
      };
      expected = {
        dependencies = {
          B = {
            _type = "vars.dependency";
            exportKey = "serviceA:instanceA1:client:jon";
            generator = "B";
          };
        };
        finalScriptIsDerivation = true;
        name = "one";
        pkgsIsAttrs = true;
        prompts = {
          prompt1 = {
            description = "prompt1";
            display = {
              group = null;
              helperText = null;
              label = null;
              required = true;
            };
            name = "prompt1";
            persist = false;
            type = "line";
          };
        };
        runtimeInputsEvaluates = true;
        scriptIsString = true;
      };
    };
}
