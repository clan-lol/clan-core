# Display module for prompts
# Shared between machine vars and flake level vars
{ lib, ... }:
let
  inherit (lib) mkOption;
  inherit (lib.types) nullOr str bool;
in
{
  options = {
    display.group = mkOption {
      type = nullOr str;
      description = ''
        The group to display the prompt in.
        This is useful to group prompts together.
      '';
      default = null;
    };
    display.label = mkOption {
      type = nullOr str;
      description = ''
        The label to display for the prompt.
        If not set, the name of the prompt will be used.
      '';
      default = null;
    };
    display.required = mkOption {
      type = bool;
      description = ''
        Whether the prompt is required.
        If set to false, the user will be able to continue without providing a value.
      '';
      default = true;
    };
    display.helperText = mkOption {
      type = nullOr str;
      description = ''
        Additional text to display next to the prompt.
        This can be used to provide additional information about the prompt.
      '';
      default = null;
    };
  };
}
