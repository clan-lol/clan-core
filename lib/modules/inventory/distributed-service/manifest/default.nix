{ lib, ... }:
let
  inherit (lib) mkOption;
  inherit (lib) types;
in
{
  options = {
    name = mkOption {
      description = ''
        The name of the module

        Mainly used to create an error context while evaluating.
        This helps backtracking which module was included; And where an error came from originally.
      '';
      type = types.str;
    };
    description = mkOption {
      type = types.str;
      description = ''
        A Short description of the module.
      '';
      default = "No description";
    };
    readme = mkOption {
      type = types.str;
      description = ''
        Extended usage description
      '';
      default = "";
    };
    categories = mkOption {
      default = [ "Uncategorized" ];
      description = ''
        Categories are used for Grouping and searching.

        While initial oriented on [freedesktop](https://specifications.freedesktop.org/menu-spec/latest/category-registry.html) the following categories are allowed
      '';
      type = types.listOf (
        types.enum [
          "AudioVideo"
          "Audio"
          "Video"
          "Development"
          "Education"
          "Game"
          "Graphics"
          "Social"
          "Network"
          "Office"
          "Science"
          "System"
          "Settings"
          "Utility"
          "Uncategorized"
        ]
      );
    };

    features = mkOption {
      description = ''
        Enable built-in features for the module

        See the documentation for each feature:
        - API
      '';
      type = types.submoduleWith {
        modules = [
          {
            options.API = mkOption {
              type = types.bool;
              # This is read only, because we don't support turning it off yet
              readOnly = true;
              default = true;
              description = ''
                Enables automatic API schema conversion for the interface of this module.
              '';
            };
          }
        ];
      };
      default = { };
    };
  };
}
