{
  python3,
  fetchFromGitHub,
}:
rec {
  asyncore-wsgi = python3.pkgs.buildPythonPackage rec {
    pname = "asyncore-wsgi";
    version = "0.0.11";
    src = fetchFromGitHub {
      owner = "romanvm";
      repo = "asyncore-wsgi";
      rev = "${version}";
      sha256 = "sha256-06rWCC8qZb9H9qPUDQpzASKOY4VX+Y+Bm9a5e71Hqhc=";
    };
    pyproject = true;
    buildInputs = [
      python3.pkgs.setuptools
    ];
  };

  web-pdb = python3.pkgs.buildPythonPackage rec {
    pname = "web-pdb";
    version = "1.6.3";
    src = fetchFromGitHub {
      owner = "romanvm";
      repo = "python-web-pdb";
      rev = "${version}";
      sha256 = "sha256-VG0mHbogx0n1f38h9VVxFQgjvghipAf1rb43/Bwb/8I=";
    };
    pyproject = true;
    buildInputs = [
      python3.pkgs.setuptools
    ];
    propagatedBuildInputs = [
      python3.pkgs.bottle
      asyncore-wsgi
    ];
  };
}
