{
  fetchurl,
  runCommand,
}:
let
  geist-regular = fetchurl {
    url = "https://github.com/vercel/geist-font/raw/7bce30121bdadfa8aadd5761b7fbda04d64c470e/fonts/Geist/webfonts/Geist-Regular.woff2";
    hash = "sha256-bQfiUE+DYxYCLRa6WHmlIVNTwv98s4HaClOp9G3tXwo=";
  };
  geist-medium = fetchurl {
    url = "https://github.com/vercel/geist-font/raw/7bce30121bdadfa8aadd5761b7fbda04d64c470e/fonts/Geist/webfonts/Geist-Medium.woff2";
    hash = "sha256-9Tw1DTi/7VIpsDtToLJb/XTZhOhItU9c1P17xPnZ02w=";
  };
  geist-semibold = fetchurl {
    url = "https://github.com/vercel/geist-font/raw/7bce30121bdadfa8aadd5761b7fbda04d64c470e/fonts/Geist/webfonts/Geist-SemiBold.woff2";
    hash = "sha256-Dpia8fMSsLE0OFfUqit1jKM0S7t7Zt5LwQROjI8yVJk=";
  };
  geist-mono-regular = fetchurl {
    url = "https://github.com/vercel/geist-font/raw/7bce30121bdadfa8aadd5761b7fbda04d64c470e/fonts/GeistMono/webfonts/GeistMono-Regular.woff2";
    hash = "sha256-SKbRHoKeTDBR+9JSXg9h68soGhUyBqGknnVYvq/+4xQ=";
  };
  geist-mono-medium = fetchurl {
    url = "https://github.com/vercel/geist-font/raw/7bce30121bdadfa8aadd5761b7fbda04d64c470e/fonts/GeistMono/webfonts/GeistMono-Medium.woff2";
    hash = "sha256-V3lOUKezrGJ3h4WO8XxvBILIxhXzI7SaId5abnA5aQQ=";
  };
  geist-mono-semibold = fetchurl {
    url = "https://github.com/vercel/geist-font/raw/7bce30121bdadfa8aadd5761b7fbda04d64c470e/fonts/GeistMono/webfonts/GeistMono-SemiBold.woff2";
    hash = "sha256-MNhO7HLZSBBvE4Fqh2vah2RPbR7jZWBrZq0oXOXbCjo=";
  };
in
runCommand "" { } ''
  mkdir -p $out

  cp ${geist-regular} $out/Geist-Regular.woff2
  cp ${geist-medium} $out/Geist-Medium.woff2
  cp ${geist-semibold} $out/Geist-SemiBold.woff2

  cp ${geist-mono-regular} $out/GeistMono-Regular.woff2
  cp ${geist-mono-medium} $out/GeistMono-Medium.woff2
  cp ${geist-mono-semibold} $out/GeistMono-SemiBold.woff2
''
