{ lib }:
let
  # Backend registry - backends are loaded from separate files
  backends = {
    in_repo = import ./backends/in-repo { inherit lib; };
    # ...
  };
in
# vars functions need to be constructed
# They depend on the store-backend
backends.in_repo
