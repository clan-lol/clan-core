{ clanLib, ... }:
let
  inherit (clanLib) select;
in
{
  test_simple_1 = {
    expr = select "a" { a = 1; };
    expected = 1;
  };
}
