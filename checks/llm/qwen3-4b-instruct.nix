{ pkgs }:

let
  # Got them from https://github.com/Gholamrezadar/ollama-direct-downloader

  # Download manifest
  manifest = pkgs.fetchurl {
    url = "https://registry.ollama.ai/v2/library/qwen3/manifests/4b-instruct";
    # You'll need to calculate this hash - run the derivation once and it will tell you the correct hash
    hash = "sha256-Dtze80WT6sGqK+nH0GxDLc+BlFrcpeyi8nZiwY8Wi6A=";
  };

  # Download blobs
  blob1 = pkgs.fetchurl {
    url = "https://registry.ollama.ai/v2/library/qwen3/blobs/sha256:b72accf9724e93698c57cbd3b1af2d3341b3d05ec2089d86d273d97964853cd2";
    hash = "sha256-tyrM+XJOk2mMV8vTsa8tM0Gz0F7CCJ2G0nPZeWSFPNI=";
  };

  blob2 = pkgs.fetchurl {
    url = "https://registry.ollama.ai/v2/library/qwen3/blobs/sha256:85e4a5b7b8ef0e48af0e8658f5aaab9c2324c76c1641493f4d1e25fce54b18b9";
    hash = "sha256-heSlt7jvDkivDoZY9aqrnCMkx2wWQUk/TR4l/OVLGLk=";
  };

  blob3 = pkgs.fetchurl {
    url = "https://registry.ollama.ai/v2/library/qwen3/blobs/sha256:eade0a07cac7712787bbce23d12f9306adb4781d873d1df6e16f7840fa37afec";
    hash = "sha256-6t4KB8rHcSeHu84j0S+TBq20eB2HPR324W94QPo3r+w=";
  };

  blob4 = pkgs.fetchurl {
    url = "https://registry.ollama.ai/v2/library/qwen3/blobs/sha256:d18a5cc71b84bc4af394a31116bd3932b42241de70c77d2b76d69a314ec8aa12";
    hash = "sha256-0YpcxxuEvErzlKMRFr05MrQiQd5wx30rdtaaMU7IqhI=";
  };

  blob5 = pkgs.fetchurl {
    url = "https://registry.ollama.ai/v2/library/qwen3/blobs/sha256:0914c7781e001948488d937994217538375b4fd8c1466c5e7a625221abd3ea7a";
    hash = "sha256-CRTHeB4AGUhIjZN5lCF1ODdbT9jBRmxeemJSIavT6no=";
  };
in
pkgs.stdenv.mkDerivation {
  pname = "ollama-qwen3-4b-instruct";
  version = "1.0";

  dontUnpack = true;

  buildPhase = ''
    mkdir -p $out/models/manifests/registry.ollama.ai/library/qwen3
    mkdir -p $out/models/blobs

    # Copy manifest
    cp ${manifest} $out/models/manifests/registry.ollama.ai/library/qwen3/4b-instruct

    # Copy blobs with correct names
    cp ${blob1} $out/models/blobs/sha256-b72accf9724e93698c57cbd3b1af2d3341b3d05ec2089d86d273d97964853cd2
    cp ${blob2} $out/models/blobs/sha256-85e4a5b7b8ef0e48af0e8658f5aaab9c2324c76c1641493f4d1e25fce54b18b9
    cp ${blob3} $out/models/blobs/sha256-eade0a07cac7712787bbce23d12f9306adb4781d873d1df6e16f7840fa37afec
    cp ${blob4} $out/models/blobs/sha256-d18a5cc71b84bc4af394a31116bd3932b42241de70c77d2b76d69a314ec8aa12
    cp ${blob5} $out/models/blobs/sha256-0914c7781e001948488d937994217538375b4fd8c1466c5e7a625221abd3ea7a
  '';

  installPhase = ''
    # buildPhase already created everything in $out
    :
  '';

  meta = with pkgs.lib; {
    description = "Qwen3 4B Instruct model for Ollama";
    license = "apache-2.0";
    platforms = platforms.all;
  };
}
