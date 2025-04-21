# Test that we can generate vars
{
  vars.generators = {
    test_generator_1 = {
      files.hello = {
        secret = false;
      };
      script = ''
        echo "hello world 1" > $out/hello
      '';
    };
    test_generator_2 = {
      files.hello = {
        secret = false;
      };
      script = ''
        echo "hello world 2" > $out/hello
      '';
    };
  };
}
