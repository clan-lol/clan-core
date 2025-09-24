# tests for the nixos options to jsonschema converter
# run these tests via `nix-unit ./test.nix`
{
  lib ? (import <nixpkgs> { }).lib,
  slib ? (import ./. { inherit lib; }),
}:
let
  eval =
    modules:
    let
      evaledConfig = lib.evalModules {
        inherit modules;
      };
    in
    evaledConfig;
in
{
  test_default = {
    expr = slib.getPrios {
      options =
        (eval [
          {
            options.foo.bar = lib.mkOption {
              type = lib.types.bool;
              description = "Test Description";
              default = true;
            };
          }
        ]).options;
    };
    expected = {
      foo = {
        bar = {
          __this = {
            files = [ "<unknown-file>" ];
            prio = 1500;
            total = false;
            type = "bool";
          };
        };
      };
    };
  };
  test_no_default = {
    expr = slib.getPrios {
      options =
        (eval [
          {
            options.foo.bar = lib.mkOption {
              type = lib.types.bool;
            };
          }
        ]).options;
    };
    expected = {
      foo = {
        bar = {
          __this = {
            files = [ ];
            prio = 9999;
            total = false;
            type = "bool";
          };
        };
      };
    };
  };

  test_submodule = {
    expr = slib.getPrios {
      options =
        (eval [
          {
            options.foo = lib.mkOption {
              type = lib.types.submodule {
                options = {
                  bar = lib.mkOption {
                    type = lib.types.bool;
                  };
                };
              };
            };
          }
        ]).options;
    };
    expected = {
      foo = {
        __this = {
          files = [ ];
          prio = 9999;
          total = true;
          type = "submodule";
        };
        bar = {
          __this = {
            files = [ ];
            prio = 9999;
            total = false;
            type = "bool";
          };
        };
      };
    };
  };

  test_submodule_with_merging =
    let
      evaluated = (
        eval [
          {
            options.foo = lib.mkOption {
              type = lib.types.submodule {
                _file = "option";
                options = {
                  normal = lib.mkOption {
                    type = lib.types.bool;
                  };
                  default = lib.mkOption {
                    type = lib.types.bool;
                  };
                  optionDefault = lib.mkOption {
                    type = lib.types.bool;
                    default = true;
                  };
                  unset = lib.mkOption {
                    type = lib.types.bool;
                  };
                };
              };
            };
          }
          {
            _file = "default";
            foo.default = lib.mkDefault true;
          }
          {
            _file = "normal";
            foo.normal = false;
          }
        ]
      );
    in
    {
      inherit evaluated;
      expr = slib.getPrios {
        options = evaluated.options;
      };
      expected = {
        foo = {
          __this = {
            files = [
              "normal"
              "default"
            ];
            prio = 100;
            total = true;
            type = "submodule";
          };
          default = {
            __this = {
              files = [ "default" ];
              prio = 1000;
              total = false;
              type = "bool";
            };
          };
          normal = {
            __this = {
              files = [ "normal" ];
              prio = 100;
              total = false;
              type = "bool";
            };
          };
          optionDefault = {
            __this = {
              files = [ "option" ];
              prio = 1500;
              total = false;
              type = "bool";
            };
          };
          unset = {
            __this = {
              files = [ ];
              prio = 9999;
              total = false;
              type = "bool";
            };
          };
        };
      };
    };

  test_submoduleWith =
    let
      evaluated = (
        eval [
          {
            options.foo = lib.mkOption {
              type = lib.types.submoduleWith {
                modules = [
                  {
                    options.bar = lib.mkOption {
                      type = lib.types.bool;
                    };
                  }
                ];
              };
            };
          }
          {
            foo.bar = false;
          }
        ]
      );
    in
    {
      inherit evaluated;
      expr = slib.getPrios {
        options = evaluated.options;
      };
      expected = {
        foo = {
          __this = {
            files = [ "<unknown-file>" ];
            prio = 100;
            total = true;
            type = "submodule";
          };
          bar = {
            __this = {
              files = [ "<unknown-file>" ];
              prio = 100;
              total = false;
              type = "bool";
            };
          };
        };
      };
    };

  # TODO(@hsjobeki): Cover this edge case
  # Blocked by: https://github.com/NixOS/nixpkgs/pull/390952 check back once that is merged
  # test_freeform =
  #   let
  #     evaluated = (
  #       eval [
  #         {
  #           freeformType = with lib.types; attrsOf (int);
  #           options = {
  #             foo = lib.mkOption {
  #               type = lib.types.int;
  #               default = 0;
  #             };
  #           };
  #         }
  #         {
  #           bar = lib.mkForce 123;
  #           baz = 1;
  #         }
  #         {
  #           bar = 10;
  #         }
  #       ]
  #     );
  #   in
  #   {
  #     inherit evaluated;
  #     expr = slib.getPrios {
  #       options = evaluated.options;
  #     };
  #     expected = {
  #     };
  #   };

  test_attrsOf_submodule =
    let
      evaluated = eval [
        {
          options.foo = lib.mkOption {
            type = lib.types.attrsOf (
              lib.types.submodule {
                options = {
                  bar = lib.mkOption {
                    type = lib.types.int;
                    default = 0;
                  };
                };
              }
            );
          };
          config.foo = {
            "nested" = {
              "bar" = 2; # <- 100 prio ?
            };
            "other" = {
              "bar" = lib.mkForce 2; # <- 50 prio ?
            };
          };
        }
      ];
    in
    {
      expr = slib.getPrios { options = evaluated.options; };
      expected = {
        foo = {
          __this = {
            files = [ "<unknown-file>" ];
            prio = 100;
            total = false;
            type = "attrsOf";
          };
          nested = {
            bar = {
              __this = {
                files = [ "<unknown-file>" ];
                prio = 100;
                total = false;
                type = "int";
              };
            };
          };
          other = {
            bar = {
              __this = {
                files = [ "<unknown-file>" ];
                prio = 50;
                total = false;
                type = "int";
              };
            };
          };
        };
      };
    };
  test_attrsOf_attrsOf_submodule =
    let
      evaluated = eval [
        {
          options.foo = lib.mkOption {
            type = lib.types.attrsOf (
              lib.types.attrsOf (
                lib.types.submodule {
                  options = {
                    bar = lib.mkOption {
                      type = lib.types.int;
                      default = 0;
                    };
                  };
                }
              )
            );
          };
          config.foo = {
            a.b = {
              bar = 1;
            };
            a.c = {
              bar = 1;
            };
            x.y = {
              bar = 1;
            };
            x.z = {
              bar = 1;
            };
          };
        }
      ];
    in
    {
      inherit evaluated;
      expr = slib.getPrios { options = evaluated.options; };
      expected = {
        foo = {
          __this = {
            files = [ "<unknown-file>" ];
            prio = 100;
            total = false;
            type = "attrsOf";
          };
          a = {
            b = {
              bar = {
                __this = {
                  files = [ "<unknown-file>" ];
                  prio = 100;
                  total = false;
                  type = "int";
                };
              };
            };
            c = {
              bar = {
                __this = {
                  files = [ "<unknown-file>" ];
                  prio = 100;
                  total = false;
                  type = "int";
                };
              };
            };
          };
          x = {
            y = {
              bar = {
                __this = {
                  files = [ "<unknown-file>" ];
                  prio = 100;
                  total = false;
                  type = "int";
                };
              };
            };
            z = {
              bar = {
                __this = {
                  files = [ "<unknown-file>" ];
                  prio = 100;
                  total = false;
                  type = "int";
                };
              };
            };
          };
        };
      };
    };

  test_attrsOf_submodule_default =
    let
      evaluated = eval [
        {
          options.machines = lib.mkOption {
            type = lib.types.attrsOf (
              lib.types.submodule {
                options = {
                  prim = lib.mkOption {
                    type = lib.types.int;
                    default = 2;
                  };
                  settings = lib.mkOption {
                    type = lib.types.submodule { };
                    default = { };
                  };
                  fludl = lib.mkOption {
                    type = lib.types.submodule { };
                    default = { };
                  };
                };
              }
            );
          };
        }
        ({
          _file = "inventory.json";
          machines.jon = {
            prim = 3;
          };
        })
        ({
          # _file = "clan.nix";
          machines.jon = { };
        })

      ];
    in
    {
      inherit evaluated;
      expr = slib.getPrios { options = evaluated.options; };
      expected = {
        machines = {
          __this = {
            files = [
              "<unknown-file>"
              "inventory.json"
            ];
            prio = 100;
            total = false;
            type = "attrsOf";
          };
          jon = {
            fludl = {
              __this = {
                files = [ "<unknown-file>" ];
                prio = 1500;
                total = true;
                type = "submodule";
              };
            };
            prim = {
              __this = {
                files = [ "inventory.json" ];
                prio = 100;
                total = false;
                type = "int";
              };
            };
            settings = {
              __this = {
                files = [ "<unknown-file>" ];
                prio = 1500;
                total = true;
                type = "submodule";
              };
            };
          };
        };
      };
    };
  test_listOf_submodule_default =
    let
      evaluated = eval [
        {
          options.machines = lib.mkOption {
            type = lib.types.listOf (
              lib.types.submodule {
                options = {
                  prim = lib.mkOption {
                    type = lib.types.int;
                    default = 2;
                  };
                  settings = lib.mkOption {
                    type = lib.types.submodule { };
                    default = { };
                  };
                  fludl = lib.mkOption {
                    type = lib.types.submodule { };
                    default = { };
                  };
                };
              }
            );
          };
        }
        ({
          _file = "inventory.json";
          machines = [
            {
              prim = 10;
            }
          ];
        })
        ({
          _file = "clan.nix";
          machines = [
            {
              prim = 3;
            }
          ];
        })
      ];
    in
    {
      inherit evaluated;
      expr = slib.getPrios { options = evaluated.options; };
      expected = {
        machines = {
          __list = [
            {
              fludl = {
                __this = {
                  files = [ "<unknown-file>" ];
                  prio = 1500;
                  total = true;
                  type = "submodule";
                };
              };
              prim = {
                __this = {
                  files = [ "clan.nix" ];
                  prio = 100;
                  total = false;
                  type = "int";
                };
              };
              settings = {
                __this = {
                  files = [ "<unknown-file>" ];
                  prio = 1500;
                  total = true;
                  type = "submodule";
                };
              };
            }
            {
              fludl = {
                __this = {
                  files = [ "<unknown-file>" ];
                  prio = 1500;
                  total = true;
                  type = "submodule";
                };
              };
              prim = {
                __this = {
                  files = [ "inventory.json" ];
                  prio = 100;
                  total = false;
                  type = "int";
                };
              };
              settings = {
                __this = {
                  files = [ "<unknown-file>" ];
                  prio = 1500;
                  total = true;
                  type = "submodule";
                };
              };
            }
          ];
          __this = {
            files = [
              "clan.nix"
              "inventory.json"
            ];
            prio = 100;
            total = false;
            type = "listOf";
          };
        };
      };
    };
}
