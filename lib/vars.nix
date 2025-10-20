_: {
  getPublicValue =
    {

      backend ? "in_repo",
      default ? throw "getPublicValue: Public value ${machine}/${generator}/${file} not found!",
      shared ? false,
      generator,
      machine,
      file,
      flake,
    }:

    if backend == "in_repo" then
      let
        path =
          if shared then
            "${flake}/vars/shared/${generator}/${file}/value"
          else
            "${flake}/vars/per-machine/${machine}/${generator}/${file}/value";
      in
      if builtins.pathExists path then builtins.readFile path else default
    else
      throw "backend ${backend} does not implement getPublicValue";
}
