{
  floco = {
    pdefs = {
      "@aashutoshrathi/word-wrap" = {
        "1.2.6" = {
          fetchInfo = {
            narHash = "sha256-vxcOLRTxV2eOJ+ZE4wxnikfcXgDucSspwo0MlbctCHM=";
            type = "tarball";
            url = "https://registry.npmjs.org/@aashutoshrathi/word-wrap/-/word-wrap-1.2.6.tgz";
          };
          ident = "@aashutoshrathi/word-wrap";
          ltype = "file";
          treeInfo = { };
          version = "1.2.6";
        };
      };
      "@alloc/quick-lru" = {
        "5.2.0" = {
          fetchInfo = {
            narHash = "sha256-5oC3OqEwgp4zpwrvg94CEIdT6tuYQ23mw6ATTfvkAVk=";
            type = "tarball";
            url = "https://registry.npmjs.org/@alloc/quick-lru/-/quick-lru-5.2.0.tgz";
          };
          ident = "@alloc/quick-lru";
          ltype = "file";
          treeInfo = { };
          version = "5.2.0";
        };
      };
      "@apidevtools/json-schema-ref-parser" = {
        "9.0.6" = {
          depInfo = {
            "@jsdevtools/ono" = {
              descriptor = "^7.1.3";
              pin = "7.1.3";
              runtime = true;
            };
            call-me-maybe = {
              descriptor = "^1.0.1";
              pin = "1.0.2";
              runtime = true;
            };
            js-yaml = {
              descriptor = "^3.13.1";
              pin = "3.14.1";
              runtime = true;
            };
          };
          fetchInfo = {
            narHash = "sha256-DL2JBWzbR6j+azOZUhZVfQFMLaQn/U36L9Sqrm1wWuY=";
            type = "tarball";
            url = "https://registry.npmjs.org/@apidevtools/json-schema-ref-parser/-/json-schema-ref-parser-9.0.6.tgz";
          };
          ident = "@apidevtools/json-schema-ref-parser";
          ltype = "file";
          version = "9.0.6";
        };
      };
      "@apidevtools/openapi-schemas" = {
        "2.1.0" = {
          fetchInfo = {
            narHash = "sha256-TGITIgemkfjnqE283wlW394ws/zD290h4aSukni5gok=";
            type = "tarball";
            url = "https://registry.npmjs.org/@apidevtools/openapi-schemas/-/openapi-schemas-2.1.0.tgz";
          };
          ident = "@apidevtools/openapi-schemas";
          ltype = "file";
          treeInfo = { };
          version = "2.1.0";
        };
      };
      "@apidevtools/swagger-methods" = {
        "3.0.2" = {
          fetchInfo = {
            narHash = "sha256-VA52uJlATFGcKlcdKf+guS9KcsGj8xX9xS/UMnYbwnE=";
            type = "tarball";
            url = "https://registry.npmjs.org/@apidevtools/swagger-methods/-/swagger-methods-3.0.2.tgz";
          };
          ident = "@apidevtools/swagger-methods";
          ltype = "file";
          treeInfo = { };
          version = "3.0.2";
        };
      };
      "@apidevtools/swagger-parser" = {
        "10.1.0" = {
          depInfo = {
            "@apidevtools/json-schema-ref-parser" = {
              descriptor = "9.0.6";
              pin = "9.0.6";
              runtime = true;
            };
            "@apidevtools/openapi-schemas" = {
              descriptor = "^2.1.0";
              pin = "2.1.0";
              runtime = true;
            };
            "@apidevtools/swagger-methods" = {
              descriptor = "^3.0.2";
              pin = "3.0.2";
              runtime = true;
            };
            "@jsdevtools/ono" = {
              descriptor = "^7.1.3";
              pin = "7.1.3";
              runtime = true;
            };
            ajv = {
              descriptor = "^8.6.3";
              pin = "8.12.0";
              runtime = true;
            };
            ajv-draft-04 = {
              descriptor = "^1.0.0";
              pin = "1.0.0";
              runtime = true;
            };
            call-me-maybe = {
              descriptor = "^1.0.1";
              pin = "1.0.2";
              runtime = true;
            };
          };
          fetchInfo = {
            narHash = "sha256-tkHK7p5EEFumefvzpNLgVWvh7ZetwphZU62z7wiEm9A=";
            type = "tarball";
            url = "https://registry.npmjs.org/@apidevtools/swagger-parser/-/swagger-parser-10.1.0.tgz";
          };
          ident = "@apidevtools/swagger-parser";
          ltype = "file";
          peerInfo = {
            openapi-types = {
              descriptor = ">=7";
            };
          };
          version = "10.1.0";
        };
      };
      "@asyncapi/specs" = {
        "4.3.1" = {
          depInfo = {
            "@types/json-schema" = {
              descriptor = "^7.0.11";
              pin = "7.0.12";
              runtime = true;
            };
          };
          fetchInfo = {
            narHash = "sha256-Q4s0A33jGrhieSyaSFg+BAq35i2MQ7NJXO7gig61uuU=";
            type = "tarball";
            url = "https://registry.npmjs.org/@asyncapi/specs/-/specs-4.3.1.tgz";
          };
          ident = "@asyncapi/specs";
          ltype = "file";
          version = "4.3.1";
        };
      };
      "@babel/code-frame" = {
        "7.22.10" = {
          depInfo = {
            "@babel/highlight" = {
              descriptor = "^7.22.10";
              pin = "7.22.10";
              runtime = true;
            };
            chalk = {
              descriptor = "^2.4.2";
              pin = "2.4.2";
              runtime = true;
            };
          };
          fetchInfo = {
            narHash = "sha256-N+QkxeIKXliZM9qVqaRn5in7il5Qlp2o4UiHV/Ommx4=";
            type = "tarball";
            url = "https://registry.npmjs.org/@babel/code-frame/-/code-frame-7.22.10.tgz";
          };
          ident = "@babel/code-frame";
          ltype = "file";
          version = "7.22.10";
        };
      };
      "@babel/helper-module-imports" = {
        "7.22.5" = {
          depInfo = {
            "@babel/types" = {
              descriptor = "^7.22.5";
              pin = "7.22.10";
              runtime = true;
            };
          };
          fetchInfo = {
            narHash = "sha256-NAdh8sPfR2kgM02DlsTquAdlvquMkENNvTjgwy17BJY=";
            type = "tarball";
            url = "https://registry.npmjs.org/@babel/helper-module-imports/-/helper-module-imports-7.22.5.tgz";
          };
          ident = "@babel/helper-module-imports";
          ltype = "file";
          version = "7.22.5";
        };
      };
      "@babel/helper-string-parser" = {
        "7.22.5" = {
          fetchInfo = {
            narHash = "sha256-y/0Rkr/gxq9LKZTCgIy7cdlN/UnU+3GDYvOJS2YKtEQ=";
            type = "tarball";
            url = "https://registry.npmjs.org/@babel/helper-string-parser/-/helper-string-parser-7.22.5.tgz";
          };
          ident = "@babel/helper-string-parser";
          ltype = "file";
          treeInfo = { };
          version = "7.22.5";
        };
      };
      "@babel/helper-validator-identifier" = {
        "7.22.5" = {
          fetchInfo = {
            narHash = "sha256-OpTn+OSCkxiO2tihG7FejNDie/keO2otD2n2U1TmUDE=";
            type = "tarball";
            url = "https://registry.npmjs.org/@babel/helper-validator-identifier/-/helper-validator-identifier-7.22.5.tgz";
          };
          ident = "@babel/helper-validator-identifier";
          ltype = "file";
          treeInfo = { };
          version = "7.22.5";
        };
      };
      "@babel/highlight" = {
        "7.22.10" = {
          depInfo = {
            "@babel/helper-validator-identifier" = {
              descriptor = "^7.22.5";
              pin = "7.22.5";
              runtime = true;
            };
            chalk = {
              descriptor = "^2.4.2";
              pin = "2.4.2";
              runtime = true;
            };
            js-tokens = {
              descriptor = "^4.0.0";
              pin = "4.0.0";
              runtime = true;
            };
          };
          fetchInfo = {
            narHash = "sha256-IELoYu97y1aaexusOmoDN77kCyUkxA7W6Ht+0d+MVXQ=";
            type = "tarball";
            url = "https://registry.npmjs.org/@babel/highlight/-/highlight-7.22.10.tgz";
          };
          ident = "@babel/highlight";
          ltype = "file";
          version = "7.22.10";
        };
      };
      "@babel/runtime" = {
        "7.22.10" = {
          depInfo = {
            regenerator-runtime = {
              descriptor = "^0.14.0";
              pin = "0.14.0";
              runtime = true;
            };
          };
          fetchInfo = {
            narHash = "sha256-5ecEDXI/B/XZUtU3VFGYjC1yAMqmmoqb9Jyu03CI1rQ=";
            type = "tarball";
            url = "https://registry.npmjs.org/@babel/runtime/-/runtime-7.22.10.tgz";
          };
          ident = "@babel/runtime";
          ltype = "file";
          version = "7.22.10";
        };
      };
      "@babel/types" = {
        "7.22.10" = {
          depInfo = {
            "@babel/helper-string-parser" = {
              descriptor = "^7.22.5";
              pin = "7.22.5";
              runtime = true;
            };
            "@babel/helper-validator-identifier" = {
              descriptor = "^7.22.5";
              pin = "7.22.5";
              runtime = true;
            };
            to-fast-properties = {
              descriptor = "^2.0.0";
              pin = "2.0.0";
              runtime = true;
            };
          };
          fetchInfo = {
            narHash = "sha256-jParA6e3/z3DZJSKuZGg45f417DKgNw22WpS8JHcMm4=";
            type = "tarball";
            url = "https://registry.npmjs.org/@babel/types/-/types-7.22.10.tgz";
          };
          ident = "@babel/types";
          ltype = "file";
          version = "7.22.10";
        };
      };
      "@emotion/babel-plugin" = {
        "11.11.0" = {
          depInfo = {
            "@babel/helper-module-imports" = {
              descriptor = "^7.16.7";
              pin = "7.22.5";
              runtime = true;
            };
            "@babel/runtime" = {
              descriptor = "^7.18.3";
              pin = "7.22.10";
              runtime = true;
            };
            "@emotion/hash" = {
              descriptor = "^0.9.1";
              pin = "0.9.1";
              runtime = true;
            };
            "@emotion/memoize" = {
              descriptor = "^0.8.1";
              pin = "0.8.1";
              runtime = true;
            };
            "@emotion/serialize" = {
              descriptor = "^1.1.2";
              pin = "1.1.2";
              runtime = true;
            };
            babel-plugin-macros = {
              descriptor = "^3.1.0";
              pin = "3.1.0";
              runtime = true;
            };
            convert-source-map = {
              descriptor = "^1.5.0";
              pin = "1.9.0";
              runtime = true;
            };
            escape-string-regexp = {
              descriptor = "^4.0.0";
              pin = "4.0.0";
              runtime = true;
            };
            find-root = {
              descriptor = "^1.1.0";
              pin = "1.1.0";
              runtime = true;
            };
            source-map = {
              descriptor = "^0.5.7";
              pin = "0.5.7";
              runtime = true;
            };
            stylis = {
              descriptor = "4.2.0";
              pin = "4.2.0";
              runtime = true;
            };
          };
          fetchInfo = {
            narHash = "sha256-Ilo7GVRDjN2dnTTUq56yaE24jM28bNwvhpAcpERkwKc=";
            type = "tarball";
            url = "https://registry.npmjs.org/@emotion/babel-plugin/-/babel-plugin-11.11.0.tgz";
          };
          ident = "@emotion/babel-plugin";
          ltype = "file";
          version = "11.11.0";
        };
      };
      "@emotion/cache" = {
        "11.11.0" = {
          depInfo = {
            "@emotion/memoize" = {
              descriptor = "^0.8.1";
              pin = "0.8.1";
              runtime = true;
            };
            "@emotion/sheet" = {
              descriptor = "^1.2.2";
              pin = "1.2.2";
              runtime = true;
            };
            "@emotion/utils" = {
              descriptor = "^1.2.1";
              pin = "1.2.1";
              runtime = true;
            };
            "@emotion/weak-memoize" = {
              descriptor = "^0.3.1";
              pin = "0.3.1";
              runtime = true;
            };
            stylis = {
              descriptor = "4.2.0";
              pin = "4.2.0";
              runtime = true;
            };
          };
          fetchInfo = {
            narHash = "sha256-k65/sP2bhz+nfO3GaRggfIjjOHjjQrFlCZxAyr2Jaug=";
            type = "tarball";
            url = "https://registry.npmjs.org/@emotion/cache/-/cache-11.11.0.tgz";
          };
          ident = "@emotion/cache";
          ltype = "file";
          version = "11.11.0";
        };
      };
      "@emotion/hash" = {
        "0.9.1" = {
          fetchInfo = {
            narHash = "sha256-Qs/IZvsViULTvbwX21HS7aOGJhzqhlFWKNQsbSR4CZ0=";
            type = "tarball";
            url = "https://registry.npmjs.org/@emotion/hash/-/hash-0.9.1.tgz";
          };
          ident = "@emotion/hash";
          ltype = "file";
          treeInfo = { };
          version = "0.9.1";
        };
      };
      "@emotion/is-prop-valid" = {
        "1.2.1" = {
          depInfo = {
            "@emotion/memoize" = {
              descriptor = "^0.8.1";
              pin = "0.8.1";
              runtime = true;
            };
          };
          fetchInfo = {
            narHash = "sha256-We6aMrfU6pWiQ8jkB8+C4rm7kXUMrk77pg6iZSlxnz8=";
            type = "tarball";
            url = "https://registry.npmjs.org/@emotion/is-prop-valid/-/is-prop-valid-1.2.1.tgz";
          };
          ident = "@emotion/is-prop-valid";
          ltype = "file";
          version = "1.2.1";
        };
      };
      "@emotion/memoize" = {
        "0.8.1" = {
          fetchInfo = {
            narHash = "sha256-+K3MxkAdKfq3r1/bvSWKm5T91pYtPRSwU3BxcP+UwbU=";
            type = "tarball";
            url = "https://registry.npmjs.org/@emotion/memoize/-/memoize-0.8.1.tgz";
          };
          ident = "@emotion/memoize";
          ltype = "file";
          treeInfo = { };
          version = "0.8.1";
        };
      };
      "@emotion/react" = {
        "11.11.1" = {
          depInfo = {
            "@babel/runtime" = {
              descriptor = "^7.18.3";
              pin = "7.22.10";
              runtime = true;
            };
            "@emotion/babel-plugin" = {
              descriptor = "^11.11.0";
              pin = "11.11.0";
              runtime = true;
            };
            "@emotion/cache" = {
              descriptor = "^11.11.0";
              pin = "11.11.0";
              runtime = true;
            };
            "@emotion/serialize" = {
              descriptor = "^1.1.2";
              pin = "1.1.2";
              runtime = true;
            };
            "@emotion/use-insertion-effect-with-fallbacks" = {
              descriptor = "^1.0.1";
              pin = "1.0.1";
              runtime = true;
            };
            "@emotion/utils" = {
              descriptor = "^1.2.1";
              pin = "1.2.1";
              runtime = true;
            };
            "@emotion/weak-memoize" = {
              descriptor = "^0.3.1";
              pin = "0.3.1";
              runtime = true;
            };
            hoist-non-react-statics = {
              descriptor = "^3.3.1";
              pin = "3.3.2";
              runtime = true;
            };
          };
          fetchInfo = {
            narHash = "sha256-ZvH518HQiG5oe8HqovFSq5tDszQ3II0LJuPhc1Vw3D4=";
            type = "tarball";
            url = "https://registry.npmjs.org/@emotion/react/-/react-11.11.1.tgz";
          };
          ident = "@emotion/react";
          ltype = "file";
          peerInfo = {
            "@types/react" = {
              descriptor = "*";
              optional = true;
            };
            react = {
              descriptor = ">=16.8.0";
            };
          };
          version = "11.11.1";
        };
      };
      "@emotion/serialize" = {
        "1.1.2" = {
          depInfo = {
            "@emotion/hash" = {
              descriptor = "^0.9.1";
              pin = "0.9.1";
              runtime = true;
            };
            "@emotion/memoize" = {
              descriptor = "^0.8.1";
              pin = "0.8.1";
              runtime = true;
            };
            "@emotion/unitless" = {
              descriptor = "^0.8.1";
              pin = "0.8.1";
              runtime = true;
            };
            "@emotion/utils" = {
              descriptor = "^1.2.1";
              pin = "1.2.1";
              runtime = true;
            };
            csstype = {
              descriptor = "^3.0.2";
              pin = "3.1.2";
              runtime = true;
            };
          };
          fetchInfo = {
            narHash = "sha256-IquvCNrJ11jaPXqMWqVpyVIm3dbiHC2AgUEZ5Zu6kqw=";
            type = "tarball";
            url = "https://registry.npmjs.org/@emotion/serialize/-/serialize-1.1.2.tgz";
          };
          ident = "@emotion/serialize";
          ltype = "file";
          version = "1.1.2";
        };
      };
      "@emotion/sheet" = {
        "1.2.2" = {
          fetchInfo = {
            narHash = "sha256-dsxUUek0zrKIwmApTAfPn/hrrLhvvVGtTWfW0MY8exA=";
            type = "tarball";
            url = "https://registry.npmjs.org/@emotion/sheet/-/sheet-1.2.2.tgz";
          };
          ident = "@emotion/sheet";
          ltype = "file";
          treeInfo = { };
          version = "1.2.2";
        };
      };
      "@emotion/styled" = {
        "11.11.0" = {
          depInfo = {
            "@babel/runtime" = {
              descriptor = "^7.18.3";
              pin = "7.22.10";
              runtime = true;
            };
            "@emotion/babel-plugin" = {
              descriptor = "^11.11.0";
              pin = "11.11.0";
              runtime = true;
            };
            "@emotion/is-prop-valid" = {
              descriptor = "^1.2.1";
              pin = "1.2.1";
              runtime = true;
            };
            "@emotion/serialize" = {
              descriptor = "^1.1.2";
              pin = "1.1.2";
              runtime = true;
            };
            "@emotion/use-insertion-effect-with-fallbacks" = {
              descriptor = "^1.0.1";
              pin = "1.0.1";
              runtime = true;
            };
            "@emotion/utils" = {
              descriptor = "^1.2.1";
              pin = "1.2.1";
              runtime = true;
            };
          };
          fetchInfo = {
            narHash = "sha256-TGTWxQ9dt7yya8O8Dy+EOPtM8vWn+P2kVf2fX4dWwn0=";
            type = "tarball";
            url = "https://registry.npmjs.org/@emotion/styled/-/styled-11.11.0.tgz";
          };
          ident = "@emotion/styled";
          ltype = "file";
          peerInfo = {
            "@emotion/react" = {
              descriptor = "^11.0.0-rc.0";
            };
            "@types/react" = {
              descriptor = "*";
              optional = true;
            };
            react = {
              descriptor = ">=16.8.0";
            };
          };
          version = "11.11.0";
        };
      };
      "@emotion/unitless" = {
        "0.8.1" = {
          fetchInfo = {
            narHash = "sha256-B2djXKZlVIEqf+5TAsGmbeniZgW8903trkistFmAXs4=";
            type = "tarball";
            url = "https://registry.npmjs.org/@emotion/unitless/-/unitless-0.8.1.tgz";
          };
          ident = "@emotion/unitless";
          ltype = "file";
          treeInfo = { };
          version = "0.8.1";
        };
      };
      "@emotion/use-insertion-effect-with-fallbacks" = {
        "1.0.1" = {
          fetchInfo = {
            narHash = "sha256-EUTtLsRTFBboZtLqzTVd2S8BPlUide0xLLi1JbwR1nk=";
            type = "tarball";
            url = "https://registry.npmjs.org/@emotion/use-insertion-effect-with-fallbacks/-/use-insertion-effect-with-fallbacks-1.0.1.tgz";
          };
          ident = "@emotion/use-insertion-effect-with-fallbacks";
          ltype = "file";
          peerInfo = {
            react = {
              descriptor = ">=16.8.0";
            };
          };
          treeInfo = { };
          version = "1.0.1";
        };
      };
      "@emotion/utils" = {
        "1.2.1" = {
          fetchInfo = {
            narHash = "sha256-xTPhx8GzQJhjmY545XGgZLcq1dGBe0Q21XI4xtQYF1k=";
            type = "tarball";
            url = "https://registry.npmjs.org/@emotion/utils/-/utils-1.2.1.tgz";
          };
          ident = "@emotion/utils";
          ltype = "file";
          treeInfo = { };
          version = "1.2.1";
        };
      };
      "@emotion/weak-memoize" = {
        "0.3.1" = {
          fetchInfo = {
            narHash = "sha256-cH/YHQ7TsSbX34aywA+fYK0JbTisNMPqqYkt7t7JFI4=";
            type = "tarball";
            url = "https://registry.npmjs.org/@emotion/weak-memoize/-/weak-memoize-0.3.1.tgz";
          };
          ident = "@emotion/weak-memoize";
          ltype = "file";
          treeInfo = { };
          version = "0.3.1";
        };
      };
      "@esbuild/android-arm" = {
        "0.15.18" = {
          fetchInfo = {
            narHash = "sha256-cf76mZXfK+PE/UaJhDvTBo6YeEhbBs1f0KjNi/tuPu4=";
            type = "tarball";
            url = "https://registry.npmjs.org/@esbuild/android-arm/-/android-arm-0.15.18.tgz";
          };
          ident = "@esbuild/android-arm";
          ltype = "file";
          sysInfo = {
            cpu = [
              "aarch"
            ];
            os = [
              "unknown"
            ];
          };
          treeInfo = { };
          version = "0.15.18";
        };
      };
      "@esbuild/linux-loong64" = {
        "0.15.18" = {
          fetchInfo = {
            narHash = "sha256-HN33gpGgAKc6b/J2FLfimtiWjQWRBuZhUSCVwEMVOx4=";
            type = "tarball";
            url = "https://registry.npmjs.org/@esbuild/linux-loong64/-/linux-loong64-0.15.18.tgz";
          };
          ident = "@esbuild/linux-loong64";
          ltype = "file";
          sysInfo = {
            cpu = [
              "unknown"
            ];
            os = [
              "linux"
            ];
          };
          treeInfo = { };
          version = "0.15.18";
        };
      };
      "@eslint-community/eslint-utils" = {
        "4.4.0" = {
          depInfo = {
            eslint-visitor-keys = {
              descriptor = "^3.3.0";
              pin = "3.4.3";
              runtime = true;
            };
          };
          fetchInfo = {
            narHash = "sha256-CrSmqKzWpfViCs3gWz0ZqRC27bfw4wUxnM3OZ9T5e1g=";
            type = "tarball";
            url = "https://registry.npmjs.org/@eslint-community/eslint-utils/-/eslint-utils-4.4.0.tgz";
          };
          ident = "@eslint-community/eslint-utils";
          ltype = "file";
          peerInfo = {
            eslint = {
              descriptor = "^6.0.0 || ^7.0.0 || >=8.0.0";
            };
          };
          version = "4.4.0";
        };
      };
      "@eslint-community/regexpp" = {
        "4.6.2" = {
          fetchInfo = {
            narHash = "sha256-X7QHkcAJ+P+x+omTNauURct+SpiHSuBTrWp2Nb1Nqdc=";
            type = "tarball";
            url = "https://registry.npmjs.org/@eslint-community/regexpp/-/regexpp-4.6.2.tgz";
          };
          ident = "@eslint-community/regexpp";
          ltype = "file";
          treeInfo = { };
          version = "4.6.2";
        };
      };
      "@eslint/eslintrc" = {
        "2.1.2" = {
          depInfo = {
            ajv = {
              descriptor = "^6.12.4";
              pin = "6.12.6";
              runtime = true;
            };
            debug = {
              descriptor = "^4.3.2";
              pin = "4.3.4";
              runtime = true;
            };
            espree = {
              descriptor = "^9.6.0";
              pin = "9.6.1";
              runtime = true;
            };
            globals = {
              descriptor = "^13.19.0";
              pin = "13.21.0";
              runtime = true;
            };
            ignore = {
              descriptor = "^5.2.0";
              pin = "5.2.4";
              runtime = true;
            };
            import-fresh = {
              descriptor = "^3.2.1";
              pin = "3.3.0";
              runtime = true;
            };
            js-yaml = {
              descriptor = "^4.1.0";
              pin = "4.1.0";
              runtime = true;
            };
            minimatch = {
              descriptor = "^3.1.2";
              pin = "3.1.2";
              runtime = true;
            };
            strip-json-comments = {
              descriptor = "^3.1.1";
              pin = "3.1.1";
              runtime = true;
            };
          };
          fetchInfo = {
            narHash = "sha256-ZxaswEEtIF8dV71nd95lW2dwm8ao6HvfX9mMdxUqW0M=";
            type = "tarball";
            url = "https://registry.npmjs.org/@eslint/eslintrc/-/eslintrc-2.1.2.tgz";
          };
          ident = "@eslint/eslintrc";
          ltype = "file";
          version = "2.1.2";
        };
      };
      "@eslint/js" = {
        "8.47.0" = {
          fetchInfo = {
            narHash = "sha256-H2Tx7HBJxBqJDaED5Ji9Y3pRFYpVdi+d9KWWohWlWCA=";
            type = "tarball";
            url = "https://registry.npmjs.org/@eslint/js/-/js-8.47.0.tgz";
          };
          ident = "@eslint/js";
          ltype = "file";
          treeInfo = { };
          version = "8.47.0";
        };
      };
      "@exodus/schemasafe" = {
        "1.2.4" = {
          fetchInfo = {
            narHash = "sha256-WJZLDLA822t1wtIde29nQVh6ceaegGjSKJqoCtO0kp4=";
            type = "tarball";
            url = "https://registry.npmjs.org/@exodus/schemasafe/-/schemasafe-1.2.4.tgz";
          };
          ident = "@exodus/schemasafe";
          ltype = "file";
          treeInfo = { };
          version = "1.2.4";
        };
      };
      "@humanwhocodes/config-array" = {
        "0.11.10" = {
          depInfo = {
            "@humanwhocodes/object-schema" = {
              descriptor = "^1.2.1";
              pin = "1.2.1";
              runtime = true;
            };
            debug = {
              descriptor = "^4.1.1";
              pin = "4.3.4";
              runtime = true;
            };
            minimatch = {
              descriptor = "^3.0.5";
              pin = "3.1.2";
              runtime = true;
            };
          };
          fetchInfo = {
            narHash = "sha256-3lsWTzx2Yy5GpVrYhFLqtEK61QBHPtSZG8YcLi48kYA=";
            type = "tarball";
            url = "https://registry.npmjs.org/@humanwhocodes/config-array/-/config-array-0.11.10.tgz";
          };
          ident = "@humanwhocodes/config-array";
          ltype = "file";
          version = "0.11.10";
        };
      };
      "@humanwhocodes/module-importer" = {
        "1.0.1" = {
          fetchInfo = {
            narHash = "sha256-Nb94n00/pTJV4WS5mfDfrZZ8nM1AISYpZdus3DdqhCk=";
            type = "tarball";
            url = "https://registry.npmjs.org/@humanwhocodes/module-importer/-/module-importer-1.0.1.tgz";
          };
          ident = "@humanwhocodes/module-importer";
          ltype = "file";
          treeInfo = { };
          version = "1.0.1";
        };
      };
      "@humanwhocodes/object-schema" = {
        "1.2.1" = {
          fetchInfo = {
            narHash = "sha256-Wam8yUjM3QV6WEffbCtEyyUDqU+A4kG9AziFwcdQdyg=";
            type = "tarball";
            url = "https://registry.npmjs.org/@humanwhocodes/object-schema/-/object-schema-1.2.1.tgz";
          };
          ident = "@humanwhocodes/object-schema";
          ltype = "file";
          treeInfo = { };
          version = "1.2.1";
        };
      };
      "@ibm-cloud/openapi-ruleset" = {
        "0.45.5" = {
          depInfo = {
            "@ibm-cloud/openapi-ruleset-utilities" = {
              descriptor = "0.0.1";
              pin = "0.0.1";
              runtime = true;
            };
            "@stoplight/spectral-formats" = {
              descriptor = "^1.1.0";
              pin = "1.5.0";
              runtime = true;
            };
            "@stoplight/spectral-functions" = {
              descriptor = "^1.6.1";
              pin = "1.7.2";
              runtime = true;
            };
            "@stoplight/spectral-rulesets" = {
              descriptor = "^1.6.0";
              pin = "1.16.0";
              runtime = true;
            };
            lodash = {
              descriptor = "^4.17.21";
              pin = "4.17.21";
              runtime = true;
            };
            validator = {
              descriptor = "^13.7.0";
              pin = "13.11.0";
              runtime = true;
            };
          };
          fetchInfo = {
            narHash = "sha256-kfx4vz8qygy3O9Wue0iQB7ZFkASAfyEsXE+4pEY9fhA=";
            type = "tarball";
            url = "https://registry.npmjs.org/@ibm-cloud/openapi-ruleset/-/openapi-ruleset-0.45.5.tgz";
          };
          ident = "@ibm-cloud/openapi-ruleset";
          ltype = "file";
          version = "0.45.5";
        };
      };
      "@ibm-cloud/openapi-ruleset-utilities" = {
        "0.0.1" = {
          fetchInfo = {
            narHash = "sha256-weXNw60zx5ser/rgK3rNWs+HKuzyeADHnYtEGOnZSq8=";
            type = "tarball";
            url = "https://registry.npmjs.org/@ibm-cloud/openapi-ruleset-utilities/-/openapi-ruleset-utilities-0.0.1.tgz";
          };
          ident = "@ibm-cloud/openapi-ruleset-utilities";
          ltype = "file";
          treeInfo = { };
          version = "0.0.1";
        };
      };
      "@jridgewell/gen-mapping" = {
        "0.3.3" = {
          depInfo = {
            "@jridgewell/set-array" = {
              descriptor = "^1.0.1";
              pin = "1.1.2";
              runtime = true;
            };
            "@jridgewell/sourcemap-codec" = {
              descriptor = "^1.4.10";
              pin = "1.4.15";
              runtime = true;
            };
            "@jridgewell/trace-mapping" = {
              descriptor = "^0.3.9";
              pin = "0.3.19";
              runtime = true;
            };
          };
          fetchInfo = {
            narHash = "sha256-xPrSOTDF2y6CUZYfgGD7G8fPfeuEPHX5u6yI0zGyXm8=";
            type = "tarball";
            url = "https://registry.npmjs.org/@jridgewell/gen-mapping/-/gen-mapping-0.3.3.tgz";
          };
          ident = "@jridgewell/gen-mapping";
          ltype = "file";
          version = "0.3.3";
        };
      };
      "@jridgewell/resolve-uri" = {
        "3.1.1" = {
          fetchInfo = {
            narHash = "sha256-kaOy0d71N7ei+GkyUOOne6CPpMEEbo2hFQsvnSd7N/Y=";
            type = "tarball";
            url = "https://registry.npmjs.org/@jridgewell/resolve-uri/-/resolve-uri-3.1.1.tgz";
          };
          ident = "@jridgewell/resolve-uri";
          ltype = "file";
          treeInfo = { };
          version = "3.1.1";
        };
      };
      "@jridgewell/set-array" = {
        "1.1.2" = {
          fetchInfo = {
            narHash = "sha256-lIY9Ar8hajSi/s4DAlqWj/PD75pWG2HDxJ6x3S3t9bE=";
            type = "tarball";
            url = "https://registry.npmjs.org/@jridgewell/set-array/-/set-array-1.1.2.tgz";
          };
          ident = "@jridgewell/set-array";
          ltype = "file";
          treeInfo = { };
          version = "1.1.2";
        };
      };
      "@jridgewell/sourcemap-codec" = {
        "1.4.15" = {
          fetchInfo = {
            narHash = "sha256-+ICJJxqNi20xwMu9zCiG5DebMb/42EJfv3UfDYAyJ5k=";
            type = "tarball";
            url = "https://registry.npmjs.org/@jridgewell/sourcemap-codec/-/sourcemap-codec-1.4.15.tgz";
          };
          ident = "@jridgewell/sourcemap-codec";
          ltype = "file";
          treeInfo = { };
          version = "1.4.15";
        };
      };
      "@jridgewell/trace-mapping" = {
        "0.3.19" = {
          depInfo = {
            "@jridgewell/resolve-uri" = {
              descriptor = "^3.1.0";
              pin = "3.1.1";
              runtime = true;
            };
            "@jridgewell/sourcemap-codec" = {
              descriptor = "^1.4.14";
              pin = "1.4.15";
              runtime = true;
            };
          };
          fetchInfo = {
            narHash = "sha256-8EaRfhWPWnOVubzVybTrKWMsQY6QFHO59YKfEklXIIg=";
            type = "tarball";
            url = "https://registry.npmjs.org/@jridgewell/trace-mapping/-/trace-mapping-0.3.19.tgz";
          };
          ident = "@jridgewell/trace-mapping";
          ltype = "file";
          version = "0.3.19";
        };
      };
      "@jsdevtools/ono" = {
        "7.1.3" = {
          fetchInfo = {
            narHash = "sha256-ywRLaRsHaB9TbXF0Ml+slinvtx5wQON/bPtkFjA6cHc=";
            type = "tarball";
            url = "https://registry.npmjs.org/@jsdevtools/ono/-/ono-7.1.3.tgz";
          };
          ident = "@jsdevtools/ono";
          ltype = "file";
          treeInfo = { };
          version = "7.1.3";
        };
      };
      "@jsep-plugin/regex" = {
        "1.0.3" = {
          fetchInfo = {
            narHash = "sha256-jw6S8VuFFz/Z2yrNubd4hZu2mujvtJVPBGv0xDLNnrA=";
            type = "tarball";
            url = "https://registry.npmjs.org/@jsep-plugin/regex/-/regex-1.0.3.tgz";
          };
          ident = "@jsep-plugin/regex";
          ltype = "file";
          peerInfo = {
            jsep = {
              descriptor = "^0.4.0||^1.0.0";
            };
          };
          treeInfo = { };
          version = "1.0.3";
        };
      };
      "@jsep-plugin/ternary" = {
        "1.1.3" = {
          fetchInfo = {
            narHash = "sha256-rt95AV9TbJZwil386dCljPGd0cnN/cHCvcic7JO4c14=";
            type = "tarball";
            url = "https://registry.npmjs.org/@jsep-plugin/ternary/-/ternary-1.1.3.tgz";
          };
          ident = "@jsep-plugin/ternary";
          ltype = "file";
          peerInfo = {
            jsep = {
              descriptor = "^0.4.0||^1.0.0";
            };
          };
          treeInfo = { };
          version = "1.1.3";
        };
      };
      "@mui/base" = {
        "5.0.0-beta.11" = {
          depInfo = {
            "@babel/runtime" = {
              descriptor = "^7.22.6";
              pin = "7.22.10";
              runtime = true;
            };
            "@emotion/is-prop-valid" = {
              descriptor = "^1.2.1";
              pin = "1.2.1";
              runtime = true;
            };
            "@mui/types" = {
              descriptor = "^7.2.4";
              pin = "7.2.4";
              runtime = true;
            };
            "@mui/utils" = {
              descriptor = "^5.14.5";
              pin = "5.14.5";
              runtime = true;
            };
            "@popperjs/core" = {
              descriptor = "^2.11.8";
              pin = "2.11.8";
              runtime = true;
            };
            clsx = {
              descriptor = "^2.0.0";
              pin = "2.0.0";
              runtime = true;
            };
            prop-types = {
              descriptor = "^15.8.1";
              pin = "15.8.1";
              runtime = true;
            };
            react-is = {
              descriptor = "^18.2.0";
              pin = "18.2.0";
              runtime = true;
            };
          };
          fetchInfo = {
            narHash = "sha256-L9mIJewYlSXGB8pY9y4EqwllJFdVnmddSn2zFEXSJz8=";
            type = "tarball";
            url = "https://registry.npmjs.org/@mui/base/-/base-5.0.0-beta.11.tgz";
          };
          ident = "@mui/base";
          ltype = "file";
          peerInfo = {
            "@types/react" = {
              descriptor = "^17.0.0 || ^18.0.0";
              optional = true;
            };
            react = {
              descriptor = "^17.0.0 || ^18.0.0";
            };
            react-dom = {
              descriptor = "^17.0.0 || ^18.0.0";
            };
          };
          version = "5.0.0-beta.11";
        };
      };
      "@mui/core-downloads-tracker" = {
        "5.14.5" = {
          fetchInfo = {
            narHash = "sha256-EeWjfhAkXjO0weSJ+BfAoREhLFv7VZ0X/a42clZg++8=";
            type = "tarball";
            url = "https://registry.npmjs.org/@mui/core-downloads-tracker/-/core-downloads-tracker-5.14.5.tgz";
          };
          ident = "@mui/core-downloads-tracker";
          ltype = "file";
          treeInfo = { };
          version = "5.14.5";
        };
      };
      "@mui/icons-material" = {
        "5.14.3" = {
          depInfo = {
            "@babel/runtime" = {
              descriptor = "^7.22.6";
              pin = "7.22.10";
              runtime = true;
            };
          };
          fetchInfo = {
            narHash = "sha256-wmY7EzOahWuCF2g5vpcOeFZ8+iJKwyFLHsQiXh1R2jY=";
            type = "tarball";
            url = "https://registry.npmjs.org/@mui/icons-material/-/icons-material-5.14.3.tgz";
          };
          ident = "@mui/icons-material";
          ltype = "file";
          peerInfo = {
            "@mui/material" = {
              descriptor = "^5.0.0";
            };
            "@types/react" = {
              descriptor = "^17.0.0 || ^18.0.0";
              optional = true;
            };
            react = {
              descriptor = "^17.0.0 || ^18.0.0";
            };
          };
          version = "5.14.3";
        };
      };
      "@mui/material" = {
        "5.14.5" = {
          depInfo = {
            "@babel/runtime" = {
              descriptor = "^7.22.6";
              pin = "7.22.10";
              runtime = true;
            };
            "@mui/base" = {
              descriptor = "5.0.0-beta.11";
              pin = "5.0.0-beta.11";
              runtime = true;
            };
            "@mui/core-downloads-tracker" = {
              descriptor = "^5.14.5";
              pin = "5.14.5";
              runtime = true;
            };
            "@mui/system" = {
              descriptor = "^5.14.5";
              pin = "5.14.5";
              runtime = true;
            };
            "@mui/types" = {
              descriptor = "^7.2.4";
              pin = "7.2.4";
              runtime = true;
            };
            "@mui/utils" = {
              descriptor = "^5.14.5";
              pin = "5.14.5";
              runtime = true;
            };
            "@types/react-transition-group" = {
              descriptor = "^4.4.6";
              pin = "4.4.6";
              runtime = true;
            };
            clsx = {
              descriptor = "^2.0.0";
              pin = "2.0.0";
              runtime = true;
            };
            csstype = {
              descriptor = "^3.1.2";
              pin = "3.1.2";
              runtime = true;
            };
            prop-types = {
              descriptor = "^15.8.1";
              pin = "15.8.1";
              runtime = true;
            };
            react-is = {
              descriptor = "^18.2.0";
              pin = "18.2.0";
              runtime = true;
            };
            react-transition-group = {
              descriptor = "^4.4.5";
              pin = "4.4.5";
              runtime = true;
            };
          };
          fetchInfo = {
            narHash = "sha256-RLcOaaUERYtrN44yHjzzG88Eq6+ox5v6tLkMZ8QR5hQ=";
            type = "tarball";
            url = "https://registry.npmjs.org/@mui/material/-/material-5.14.5.tgz";
          };
          ident = "@mui/material";
          ltype = "file";
          peerInfo = {
            "@emotion/react" = {
              descriptor = "^11.5.0";
              optional = true;
            };
            "@emotion/styled" = {
              descriptor = "^11.3.0";
              optional = true;
            };
            "@types/react" = {
              descriptor = "^17.0.0 || ^18.0.0";
              optional = true;
            };
            react = {
              descriptor = "^17.0.0 || ^18.0.0";
            };
            react-dom = {
              descriptor = "^17.0.0 || ^18.0.0";
            };
          };
          version = "5.14.5";
        };
      };
      "@mui/private-theming" = {
        "5.14.5" = {
          depInfo = {
            "@babel/runtime" = {
              descriptor = "^7.22.6";
              pin = "7.22.10";
              runtime = true;
            };
            "@mui/utils" = {
              descriptor = "^5.14.5";
              pin = "5.14.5";
              runtime = true;
            };
            prop-types = {
              descriptor = "^15.8.1";
              pin = "15.8.1";
              runtime = true;
            };
          };
          fetchInfo = {
            narHash = "sha256-Zn1XcE+EbFzWngg+nXUoTJ87VVJI1X8uztLe8pRp9sI=";
            type = "tarball";
            url = "https://registry.npmjs.org/@mui/private-theming/-/private-theming-5.14.5.tgz";
          };
          ident = "@mui/private-theming";
          ltype = "file";
          peerInfo = {
            "@types/react" = {
              descriptor = "^17.0.0 || ^18.0.0";
              optional = true;
            };
            react = {
              descriptor = "^17.0.0 || ^18.0.0";
            };
          };
          version = "5.14.5";
        };
      };
      "@mui/styled-engine" = {
        "5.13.2" = {
          depInfo = {
            "@babel/runtime" = {
              descriptor = "^7.21.0";
              pin = "7.22.10";
              runtime = true;
            };
            "@emotion/cache" = {
              descriptor = "^11.11.0";
              pin = "11.11.0";
              runtime = true;
            };
            csstype = {
              descriptor = "^3.1.2";
              pin = "3.1.2";
              runtime = true;
            };
            prop-types = {
              descriptor = "^15.8.1";
              pin = "15.8.1";
              runtime = true;
            };
          };
          fetchInfo = {
            narHash = "sha256-1caHo5vUZbH7CWfnvIkon2Jrrfl8ar5NfKOGghrGCvs=";
            type = "tarball";
            url = "https://registry.npmjs.org/@mui/styled-engine/-/styled-engine-5.13.2.tgz";
          };
          ident = "@mui/styled-engine";
          ltype = "file";
          peerInfo = {
            "@emotion/react" = {
              descriptor = "^11.4.1";
              optional = true;
            };
            "@emotion/styled" = {
              descriptor = "^11.3.0";
              optional = true;
            };
            react = {
              descriptor = "^17.0.0 || ^18.0.0";
            };
          };
          version = "5.13.2";
        };
      };
      "@mui/system" = {
        "5.14.5" = {
          depInfo = {
            "@babel/runtime" = {
              descriptor = "^7.22.6";
              pin = "7.22.10";
              runtime = true;
            };
            "@mui/private-theming" = {
              descriptor = "^5.14.5";
              pin = "5.14.5";
              runtime = true;
            };
            "@mui/styled-engine" = {
              descriptor = "^5.13.2";
              pin = "5.13.2";
              runtime = true;
            };
            "@mui/types" = {
              descriptor = "^7.2.4";
              pin = "7.2.4";
              runtime = true;
            };
            "@mui/utils" = {
              descriptor = "^5.14.5";
              pin = "5.14.5";
              runtime = true;
            };
            clsx = {
              descriptor = "^2.0.0";
              pin = "2.0.0";
              runtime = true;
            };
            csstype = {
              descriptor = "^3.1.2";
              pin = "3.1.2";
              runtime = true;
            };
            prop-types = {
              descriptor = "^15.8.1";
              pin = "15.8.1";
              runtime = true;
            };
          };
          fetchInfo = {
            narHash = "sha256-KvEo9N9tA0dp+cFvP280Ih6aLrxABUd8OxSKgFO0B1s=";
            type = "tarball";
            url = "https://registry.npmjs.org/@mui/system/-/system-5.14.5.tgz";
          };
          ident = "@mui/system";
          ltype = "file";
          peerInfo = {
            "@emotion/react" = {
              descriptor = "^11.5.0";
              optional = true;
            };
            "@emotion/styled" = {
              descriptor = "^11.3.0";
              optional = true;
            };
            "@types/react" = {
              descriptor = "^17.0.0 || ^18.0.0";
              optional = true;
            };
            react = {
              descriptor = "^17.0.0 || ^18.0.0";
            };
          };
          version = "5.14.5";
        };
      };
      "@mui/types" = {
        "7.2.4" = {
          fetchInfo = {
            narHash = "sha256-vtMIrL4OoMnfvIlXr96iQ9+HB8uO9YY4eqaqcDLCiyo=";
            type = "tarball";
            url = "https://registry.npmjs.org/@mui/types/-/types-7.2.4.tgz";
          };
          ident = "@mui/types";
          ltype = "file";
          peerInfo = {
            "@types/react" = {
              descriptor = "*";
              optional = true;
            };
          };
          treeInfo = { };
          version = "7.2.4";
        };
      };
      "@mui/utils" = {
        "5.14.5" = {
          depInfo = {
            "@babel/runtime" = {
              descriptor = "^7.22.6";
              pin = "7.22.10";
              runtime = true;
            };
            "@types/prop-types" = {
              descriptor = "^15.7.5";
              pin = "15.7.5";
              runtime = true;
            };
            "@types/react-is" = {
              descriptor = "^18.2.1";
              pin = "18.2.1";
              runtime = true;
            };
            prop-types = {
              descriptor = "^15.8.1";
              pin = "15.8.1";
              runtime = true;
            };
            react-is = {
              descriptor = "^18.2.0";
              pin = "18.2.0";
              runtime = true;
            };
          };
          fetchInfo = {
            narHash = "sha256-mym+STz4KseB2TDlXB8qkcPKpvNQDU4r+9xTC99m84U=";
            type = "tarball";
            url = "https://registry.npmjs.org/@mui/utils/-/utils-5.14.5.tgz";
          };
          ident = "@mui/utils";
          ltype = "file";
          peerInfo = {
            react = {
              descriptor = "^17.0.0 || ^18.0.0";
            };
          };
          version = "5.14.5";
        };
      };
      "@next/env" = {
        "13.4.12" = {
          fetchInfo = {
            narHash = "sha256-Qyy4GCbJZ0e8LOJAbC/2aoOtndYOa7OsiI6M9o/NL7M=";
            type = "tarball";
            url = "https://registry.npmjs.org/@next/env/-/env-13.4.12.tgz";
          };
          ident = "@next/env";
          ltype = "file";
          treeInfo = { };
          version = "13.4.12";
        };
      };
      "@next/eslint-plugin-next" = {
        "13.4.12" = {
          depInfo = {
            glob = {
              descriptor = "7.1.7";
              pin = "7.1.7";
              runtime = true;
            };
          };
          fetchInfo = {
            narHash = "sha256-v6RnCuHYY2zqdrSKNb3yePpUev54QpibS1HSnndJ9+U=";
            type = "tarball";
            url = "https://registry.npmjs.org/@next/eslint-plugin-next/-/eslint-plugin-next-13.4.12.tgz";
          };
          ident = "@next/eslint-plugin-next";
          ltype = "file";
          version = "13.4.12";
        };
      };
      "@next/swc-darwin-arm64" = {
        "13.4.12" = {
          fetchInfo = {
            narHash = "sha256-8M4/Apxswf7eDvzmt0mGy1GkiF91nIp96OTBtoJ5Fjo=";
            type = "tarball";
            url = "https://registry.npmjs.org/@next/swc-darwin-arm64/-/swc-darwin-arm64-13.4.12.tgz";
          };
          ident = "@next/swc-darwin-arm64";
          ltype = "file";
          sysInfo = {
            cpu = [
              "aarch64"
            ];
            os = [
              "darwin"
            ];
          };
          treeInfo = { };
          version = "13.4.12";
        };
      };
      "@next/swc-darwin-x64" = {
        "13.4.12" = {
          fetchInfo = {
            narHash = "sha256-WIuOsoW1vwjG5W+tjfyWQgfipRdbkQDWA7u6/AUb83I=";
            type = "tarball";
            url = "https://registry.npmjs.org/@next/swc-darwin-x64/-/swc-darwin-x64-13.4.12.tgz";
          };
          ident = "@next/swc-darwin-x64";
          ltype = "file";
          sysInfo = {
            cpu = [
              "x86_64"
            ];
            os = [
              "darwin"
            ];
          };
          treeInfo = { };
          version = "13.4.12";
        };
      };
      "@next/swc-linux-arm64-gnu" = {
        "13.4.12" = {
          fetchInfo = {
            narHash = "sha256-72STnlk7dmwUi1cY9KLfI+dx/V18L0nw0FyYmgZkEKA=";
            type = "tarball";
            url = "https://registry.npmjs.org/@next/swc-linux-arm64-gnu/-/swc-linux-arm64-gnu-13.4.12.tgz";
          };
          ident = "@next/swc-linux-arm64-gnu";
          ltype = "file";
          sysInfo = {
            cpu = [
              "aarch64"
            ];
            os = [
              "linux"
            ];
          };
          treeInfo = { };
          version = "13.4.12";
        };
      };
      "@next/swc-linux-arm64-musl" = {
        "13.4.12" = {
          fetchInfo = {
            narHash = "sha256-+EBDWb2xjrA05ShwWJn28hAKRO3SELsUQjwLa20JZ+E=";
            type = "tarball";
            url = "https://registry.npmjs.org/@next/swc-linux-arm64-musl/-/swc-linux-arm64-musl-13.4.12.tgz";
          };
          ident = "@next/swc-linux-arm64-musl";
          ltype = "file";
          sysInfo = {
            cpu = [
              "aarch64"
            ];
            os = [
              "linux"
            ];
          };
          treeInfo = { };
          version = "13.4.12";
        };
      };
      "@next/swc-linux-x64-gnu" = {
        "13.4.12" = {
          fetchInfo = {
            narHash = "sha256-ou7XfUBE6GiRZ5RZV5OV0Kt18XFpuFf/cJn/FDRleUg=";
            type = "tarball";
            url = "https://registry.npmjs.org/@next/swc-linux-x64-gnu/-/swc-linux-x64-gnu-13.4.12.tgz";
          };
          ident = "@next/swc-linux-x64-gnu";
          ltype = "file";
          sysInfo = {
            cpu = [
              "x86_64"
            ];
            os = [
              "linux"
            ];
          };
          treeInfo = { };
          version = "13.4.12";
        };
      };
      "@next/swc-linux-x64-musl" = {
        "13.4.12" = {
          fetchInfo = {
            narHash = "sha256-bysokWHl+ab9vO8v3a8/jzETRmk5ZrKPdlMmV0rv+jg=";
            type = "tarball";
            url = "https://registry.npmjs.org/@next/swc-linux-x64-musl/-/swc-linux-x64-musl-13.4.12.tgz";
          };
          ident = "@next/swc-linux-x64-musl";
          ltype = "file";
          sysInfo = {
            cpu = [
              "x86_64"
            ];
            os = [
              "linux"
            ];
          };
          treeInfo = { };
          version = "13.4.12";
        };
      };
      "@next/swc-win32-arm64-msvc" = {
        "13.4.12" = {
          fetchInfo = {
            narHash = "sha256-zTVLyQ5uin3Zin7MGqc4IHpXMetDJr6+SzJeApdZZZs=";
            type = "tarball";
            url = "https://registry.npmjs.org/@next/swc-win32-arm64-msvc/-/swc-win32-arm64-msvc-13.4.12.tgz";
          };
          ident = "@next/swc-win32-arm64-msvc";
          ltype = "file";
          sysInfo = {
            cpu = [
              "aarch64"
            ];
            os = [
              "win32"
            ];
          };
          treeInfo = { };
          version = "13.4.12";
        };
      };
      "@next/swc-win32-ia32-msvc" = {
        "13.4.12" = {
          fetchInfo = {
            narHash = "sha256-MwTa50QgNlshoxByQUpv4mPOoBP4hYOKDla67O8Xv6w=";
            type = "tarball";
            url = "https://registry.npmjs.org/@next/swc-win32-ia32-msvc/-/swc-win32-ia32-msvc-13.4.12.tgz";
          };
          ident = "@next/swc-win32-ia32-msvc";
          ltype = "file";
          sysInfo = {
            cpu = [
              "i686"
            ];
            os = [
              "win32"
            ];
          };
          treeInfo = { };
          version = "13.4.12";
        };
      };
      "@next/swc-win32-x64-msvc" = {
        "13.4.12" = {
          fetchInfo = {
            narHash = "sha256-2bohi7ZEtIhvMUptsmVekmMkqwnCgZlAsQEVaeEGAgE=";
            type = "tarball";
            url = "https://registry.npmjs.org/@next/swc-win32-x64-msvc/-/swc-win32-x64-msvc-13.4.12.tgz";
          };
          ident = "@next/swc-win32-x64-msvc";
          ltype = "file";
          sysInfo = {
            cpu = [
              "x86_64"
            ];
            os = [
              "win32"
            ];
          };
          treeInfo = { };
          version = "13.4.12";
        };
      };
      "@nodelib/fs.scandir" = {
        "2.1.5" = {
          depInfo = {
            "@nodelib/fs.stat" = {
              descriptor = "2.0.5";
              pin = "2.0.5";
              runtime = true;
            };
            run-parallel = {
              descriptor = "^1.1.9";
              pin = "1.2.0";
              runtime = true;
            };
          };
          fetchInfo = {
            narHash = "sha256-XkaO6o9trImz7QHxNe8P0l09Kmn8rsFIP5W/s1+HV7w=";
            type = "tarball";
            url = "https://registry.npmjs.org/@nodelib/fs.scandir/-/fs.scandir-2.1.5.tgz";
          };
          ident = "@nodelib/fs.scandir";
          ltype = "file";
          version = "2.1.5";
        };
      };
      "@nodelib/fs.stat" = {
        "2.0.5" = {
          fetchInfo = {
            narHash = "sha256-9D6qDZ0i0QJCngfEgCsDkX1/BFc1UpQ7Yy8b3jMLDCk=";
            type = "tarball";
            url = "https://registry.npmjs.org/@nodelib/fs.stat/-/fs.stat-2.0.5.tgz";
          };
          ident = "@nodelib/fs.stat";
          ltype = "file";
          treeInfo = { };
          version = "2.0.5";
        };
      };
      "@nodelib/fs.walk" = {
        "1.2.8" = {
          depInfo = {
            "@nodelib/fs.scandir" = {
              descriptor = "2.1.5";
              pin = "2.1.5";
              runtime = true;
            };
            fastq = {
              descriptor = "^1.6.0";
              pin = "1.15.0";
              runtime = true;
            };
          };
          fetchInfo = {
            narHash = "sha256-kB5uDfcwF+SIjAkm1mY/corry0eyTrSmQsacQjtgf5U=";
            type = "tarball";
            url = "https://registry.npmjs.org/@nodelib/fs.walk/-/fs.walk-1.2.8.tgz";
          };
          ident = "@nodelib/fs.walk";
          ltype = "file";
          version = "1.2.8";
        };
      };
      "@orval/angular" = {
        "6.17.0" = {
          depInfo = {
            "@orval/core" = {
              descriptor = "6.17.0";
              pin = "6.17.0";
              runtime = true;
            };
          };
          fetchInfo = {
            narHash = "sha256-9PiUByD9SrmXkZ52fgok+bTKjiC7QSHlUdowWkuxw5c=";
            type = "tarball";
            url = "https://registry.npmjs.org/@orval/angular/-/angular-6.17.0.tgz";
          };
          ident = "@orval/angular";
          ltype = "file";
          version = "6.17.0";
        };
      };
      "@orval/axios" = {
        "6.17.0" = {
          depInfo = {
            "@orval/core" = {
              descriptor = "6.17.0";
              pin = "6.17.0";
              runtime = true;
            };
          };
          fetchInfo = {
            narHash = "sha256-mKnh+GOLl04Di2Xr7U01/u6AljRUuLPBRyO2rIVBcSw=";
            type = "tarball";
            url = "https://registry.npmjs.org/@orval/axios/-/axios-6.17.0.tgz";
          };
          ident = "@orval/axios";
          ltype = "file";
          version = "6.17.0";
        };
      };
      "@orval/core" = {
        "6.17.0" = {
          depInfo = {
            "@apidevtools/swagger-parser" = {
              descriptor = "^10.1.0";
              pin = "10.1.0";
              runtime = true;
            };
            acorn = {
              descriptor = "^8.8.0";
              pin = "8.10.0";
              runtime = true;
            };
            ajv = {
              descriptor = "^8.11.0";
              pin = "8.12.0";
              runtime = true;
            };
            chalk = {
              descriptor = "^4.1.2";
              pin = "4.1.2";
              runtime = true;
            };
            compare-versions = {
              descriptor = "^4.1.3";
              pin = "4.1.4";
              runtime = true;
            };
            debug = {
              descriptor = "^4.3.4";
              pin = "4.3.4";
              runtime = true;
            };
            esbuild = {
              descriptor = "^0.15.3";
              pin = "0.15.18";
              runtime = true;
            };
            esutils = {
              descriptor = "2.0.3";
              pin = "2.0.3";
              runtime = true;
            };
            fs-extra = {
              descriptor = "^10.1.0";
              pin = "10.1.0";
              runtime = true;
            };
            globby = {
              descriptor = "11.1.0";
              pin = "11.1.0";
              runtime = true;
            };
            ibm-openapi-validator = {
              descriptor = "^0.97.3";
              pin = "0.97.5";
              runtime = true;
            };
            "lodash.get" = {
              descriptor = "^4.4.2";
              pin = "4.4.2";
              runtime = true;
            };
            "lodash.isempty" = {
              descriptor = "^4.4.0";
              pin = "4.4.0";
              runtime = true;
            };
            "lodash.omit" = {
              descriptor = "^4.5.0";
              pin = "4.5.0";
              runtime = true;
            };
            "lodash.uniq" = {
              descriptor = "^4.5.0";
              pin = "4.5.0";
              runtime = true;
            };
            "lodash.uniqby" = {
              descriptor = "^4.7.0";
              pin = "4.7.0";
              runtime = true;
            };
            "lodash.uniqwith" = {
              descriptor = "^4.5.0";
              pin = "4.5.0";
              runtime = true;
            };
            micromatch = {
              descriptor = "^4.0.5";
              pin = "4.0.5";
              runtime = true;
            };
            openapi3-ts = {
              descriptor = "^3.0.0";
              pin = "3.2.0";
              runtime = true;
            };
            swagger2openapi = {
              descriptor = "^7.0.8";
              pin = "7.0.8";
              runtime = true;
            };
            validator = {
              descriptor = "^13.7.0";
              pin = "13.11.0";
              runtime = true;
            };
          };
          fetchInfo = {
            narHash = "sha256-Q/hhChTccpgK3eloejEztJQuyxA4DXH3wNfOeR2rNEE=";
            type = "tarball";
            url = "https://registry.npmjs.org/@orval/core/-/core-6.17.0.tgz";
          };
          ident = "@orval/core";
          ltype = "file";
          version = "6.17.0";
        };
      };
      "@orval/msw" = {
        "6.17.0" = {
          depInfo = {
            "@orval/core" = {
              descriptor = "6.17.0";
              pin = "6.17.0";
              runtime = true;
            };
            cuid = {
              descriptor = "^2.1.8";
              pin = "2.1.8";
              runtime = true;
            };
            "lodash.get" = {
              descriptor = "^4.4.2";
              pin = "4.4.2";
              runtime = true;
            };
            "lodash.omit" = {
              descriptor = "^4.5.0";
              pin = "4.5.0";
              runtime = true;
            };
            openapi3-ts = {
              descriptor = "^3.0.0";
              pin = "3.2.0";
              runtime = true;
            };
          };
          fetchInfo = {
            narHash = "sha256-n8F3ePb9ShoxSTRVc7xFpQgqhN5dhYezVlJKTdHXpWE=";
            type = "tarball";
            url = "https://registry.npmjs.org/@orval/msw/-/msw-6.17.0.tgz";
          };
          ident = "@orval/msw";
          ltype = "file";
          version = "6.17.0";
        };
      };
      "@orval/query" = {
        "6.17.0" = {
          depInfo = {
            "@orval/core" = {
              descriptor = "6.17.0";
              pin = "6.17.0";
              runtime = true;
            };
            "lodash.omitby" = {
              descriptor = "^4.6.0";
              pin = "4.6.0";
              runtime = true;
            };
          };
          fetchInfo = {
            narHash = "sha256-mtpsh7t4ByrU3Hy7K5rsJ88yH33lrGoPDPuoDNynG/E=";
            type = "tarball";
            url = "https://registry.npmjs.org/@orval/query/-/query-6.17.0.tgz";
          };
          ident = "@orval/query";
          ltype = "file";
          version = "6.17.0";
        };
      };
      "@orval/swr" = {
        "6.17.0" = {
          depInfo = {
            "@orval/core" = {
              descriptor = "6.17.0";
              pin = "6.17.0";
              runtime = true;
            };
          };
          fetchInfo = {
            narHash = "sha256-qC3Up4VztXfvXeqDuem4mdNv8B9SdHv61PRYCpBc8Rw=";
            type = "tarball";
            url = "https://registry.npmjs.org/@orval/swr/-/swr-6.17.0.tgz";
          };
          ident = "@orval/swr";
          ltype = "file";
          version = "6.17.0";
        };
      };
      "@orval/zod" = {
        "6.17.0" = {
          depInfo = {
            "@orval/core" = {
              descriptor = "6.17.0";
              pin = "6.17.0";
              runtime = true;
            };
            "lodash.uniq" = {
              descriptor = "^4.5.0";
              pin = "4.5.0";
              runtime = true;
            };
          };
          fetchInfo = {
            narHash = "sha256-s1spNtVUVZX/dbfpSiOSs7HZqxcFVcj+u7/Czjq1ACg=";
            type = "tarball";
            url = "https://registry.npmjs.org/@orval/zod/-/zod-6.17.0.tgz";
          };
          ident = "@orval/zod";
          ltype = "file";
          version = "6.17.0";
        };
      };
      "@popperjs/core" = {
        "2.11.8" = {
          fetchInfo = {
            narHash = "sha256-jS4xEBxSW+1dOEArwszzst82cxfP/bM/EZyj+WaeNfk=";
            type = "tarball";
            url = "https://registry.npmjs.org/@popperjs/core/-/core-2.11.8.tgz";
          };
          ident = "@popperjs/core";
          ltype = "file";
          treeInfo = { };
          version = "2.11.8";
        };
      };
      "@rollup/plugin-commonjs" = {
        "22.0.2" = {
          depInfo = {
            "@rollup/pluginutils" = {
              descriptor = "^3.1.0";
              pin = "3.1.0";
              runtime = true;
            };
            commondir = {
              descriptor = "^1.0.1";
              pin = "1.0.1";
              runtime = true;
            };
            estree-walker = {
              descriptor = "^2.0.1";
              pin = "2.0.2";
              runtime = true;
            };
            glob = {
              descriptor = "^7.1.6";
              pin = "7.1.7";
              runtime = true;
            };
            is-reference = {
              descriptor = "^1.2.1";
              pin = "1.2.1";
              runtime = true;
            };
            magic-string = {
              descriptor = "^0.25.7";
              pin = "0.25.9";
              runtime = true;
            };
            resolve = {
              descriptor = "^1.17.0";
              pin = "1.22.4";
              runtime = true;
            };
          };
          fetchInfo = {
            narHash = "sha256-++++fgRvBipDpRoY8X0K5jujlmo6C3cKnqL/bP2gmMk=";
            type = "tarball";
            url = "https://registry.npmjs.org/@rollup/plugin-commonjs/-/plugin-commonjs-22.0.2.tgz";
          };
          ident = "@rollup/plugin-commonjs";
          ltype = "file";
          peerInfo = {
            rollup = {
              descriptor = "^2.68.0";
            };
          };
          version = "22.0.2";
        };
      };
      "@rollup/pluginutils" = {
        "3.1.0" = {
          depInfo = {
            "@types/estree" = {
              descriptor = "0.0.39";
              pin = "0.0.39";
              runtime = true;
            };
            estree-walker = {
              descriptor = "^1.0.1";
              pin = "1.0.1";
              runtime = true;
            };
            picomatch = {
              descriptor = "^2.2.2";
              pin = "2.3.1";
              runtime = true;
            };
          };
          fetchInfo = {
            narHash = "sha256-iRDxdCJwp9C34omDvijP4+vK5Q9ROkf+GW5ImmQnTn8=";
            type = "tarball";
            url = "https://registry.npmjs.org/@rollup/pluginutils/-/pluginutils-3.1.0.tgz";
          };
          ident = "@rollup/pluginutils";
          ltype = "file";
          peerInfo = {
            rollup = {
              descriptor = "^1.20.0||^2.0.0";
            };
          };
          version = "3.1.0";
        };
      };
      "@rushstack/eslint-patch" = {
        "1.3.3" = {
          fetchInfo = {
            narHash = "sha256-d/AwDtJkslFMsEDvoR3AWINEaqq2VC/z9mmGbNuzdBI=";
            type = "tarball";
            url = "https://registry.npmjs.org/@rushstack/eslint-patch/-/eslint-patch-1.3.3.tgz";
          };
          ident = "@rushstack/eslint-patch";
          ltype = "file";
          treeInfo = { };
          version = "1.3.3";
        };
      };
      "@stoplight/better-ajv-errors" = {
        "1.0.3" = {
          depInfo = {
            jsonpointer = {
              descriptor = "^5.0.0";
              pin = "5.0.1";
              runtime = true;
            };
            leven = {
              descriptor = "^3.1.0";
              pin = "3.1.0";
              runtime = true;
            };
          };
          fetchInfo = {
            narHash = "sha256-VyW+2EclNo7AZEYSNDPO1pRg9e6WM6o17d9QY+3Zvck=";
            type = "tarball";
            url = "https://registry.npmjs.org/@stoplight/better-ajv-errors/-/better-ajv-errors-1.0.3.tgz";
          };
          ident = "@stoplight/better-ajv-errors";
          ltype = "file";
          peerInfo = {
            ajv = {
              descriptor = ">=8";
            };
          };
          version = "1.0.3";
        };
      };
      "@stoplight/json" = {
        "3.21.0" = {
          depInfo = {
            "@stoplight/ordered-object-literal" = {
              descriptor = "^1.0.3";
              pin = "1.0.4";
              runtime = true;
            };
            "@stoplight/path" = {
              descriptor = "^1.3.2";
              pin = "1.3.2";
              runtime = true;
            };
            "@stoplight/types" = {
              descriptor = "^13.6.0";
              pin = "13.19.0";
              runtime = true;
            };
            jsonc-parser = {
              descriptor = "~2.2.1";
              pin = "2.2.1";
              runtime = true;
            };
            lodash = {
              descriptor = "^4.17.21";
              pin = "4.17.21";
              runtime = true;
            };
            safe-stable-stringify = {
              descriptor = "^1.1";
              pin = "1.1.1";
              runtime = true;
            };
          };
          fetchInfo = {
            narHash = "sha256-+8QRrTIfOJlzFsdb4VFkq1YwpOkttxZHCbXivdo7Ots=";
            type = "tarball";
            url = "https://registry.npmjs.org/@stoplight/json/-/json-3.21.0.tgz";
          };
          ident = "@stoplight/json";
          ltype = "file";
          version = "3.21.0";
        };
      };
      "@stoplight/json-ref-readers" = {
        "1.2.2" = {
          depInfo = {
            node-fetch = {
              descriptor = "^2.6.0";
              pin = "2.7.0";
              runtime = true;
            };
            tslib = {
              descriptor = "^1.14.1";
              pin = "1.14.1";
              runtime = true;
            };
          };
          fetchInfo = {
            narHash = "sha256-xaVtNo9XGElGI6oKR6D6gA43DUMdED/6TH9oslJnKxw=";
            type = "tarball";
            url = "https://registry.npmjs.org/@stoplight/json-ref-readers/-/json-ref-readers-1.2.2.tgz";
          };
          ident = "@stoplight/json-ref-readers";
          ltype = "file";
          version = "1.2.2";
        };
      };
      "@stoplight/json-ref-resolver" = {
        "3.1.6" = {
          depInfo = {
            "@stoplight/json" = {
              descriptor = "^3.21.0";
              pin = "3.21.0";
              runtime = true;
            };
            "@stoplight/path" = {
              descriptor = "^1.3.2";
              pin = "1.3.2";
              runtime = true;
            };
            "@stoplight/types" = {
              descriptor = "^12.3.0 || ^13.0.0";
              pin = "13.19.0";
              runtime = true;
            };
            "@types/urijs" = {
              descriptor = "^1.19.19";
              pin = "1.19.19";
              runtime = true;
            };
            dependency-graph = {
              descriptor = "~0.11.0";
              pin = "0.11.0";
              runtime = true;
            };
            fast-memoize = {
              descriptor = "^2.5.2";
              pin = "2.5.2";
              runtime = true;
            };
            immer = {
              descriptor = "^9.0.6";
              pin = "9.0.21";
              runtime = true;
            };
            lodash = {
              descriptor = "^4.17.21";
              pin = "4.17.21";
              runtime = true;
            };
            tslib = {
              descriptor = "^2.6.0";
              pin = "2.6.1";
              runtime = true;
            };
            urijs = {
              descriptor = "^1.19.11";
              pin = "1.19.11";
              runtime = true;
            };
          };
          fetchInfo = {
            narHash = "sha256-vxSD+Pyq4VBz1RbUBsSqMUso5oM1tnOA+CpGeORUTZE=";
            type = "tarball";
            url = "https://registry.npmjs.org/@stoplight/json-ref-resolver/-/json-ref-resolver-3.1.6.tgz";
          };
          ident = "@stoplight/json-ref-resolver";
          ltype = "file";
          version = "3.1.6";
        };
      };
      "@stoplight/ordered-object-literal" = {
        "1.0.4" = {
          fetchInfo = {
            narHash = "sha256-zNape708uU2908acpoRGxAtRbwjsEe7Tu6luDv6TmLs=";
            type = "tarball";
            url = "https://registry.npmjs.org/@stoplight/ordered-object-literal/-/ordered-object-literal-1.0.4.tgz";
          };
          ident = "@stoplight/ordered-object-literal";
          ltype = "file";
          treeInfo = { };
          version = "1.0.4";
        };
      };
      "@stoplight/path" = {
        "1.3.2" = {
          fetchInfo = {
            narHash = "sha256-/ZSC/x4o+l9N2F3RORYz+PDS/TX6gClSIylgNb4eWgY=";
            type = "tarball";
            url = "https://registry.npmjs.org/@stoplight/path/-/path-1.3.2.tgz";
          };
          ident = "@stoplight/path";
          ltype = "file";
          treeInfo = { };
          version = "1.3.2";
        };
      };
      "@stoplight/spectral-cli" = {
        "6.10.1" = {
          binInfo = {
            binPairs = {
              spectral = "dist/index.js";
            };
          };
          depInfo = {
            "@stoplight/json" = {
              descriptor = "~3.21.0";
              pin = "3.21.0";
              runtime = true;
            };
            "@stoplight/path" = {
              descriptor = "1.3.2";
              pin = "1.3.2";
              runtime = true;
            };
            "@stoplight/spectral-core" = {
              descriptor = "^1.18.3";
              pin = "1.18.3";
              runtime = true;
            };
            "@stoplight/spectral-formatters" = {
              descriptor = "^1.2.0";
              pin = "1.2.0";
              runtime = true;
            };
            "@stoplight/spectral-parsers" = {
              descriptor = "^1.0.3";
              pin = "1.0.3";
              runtime = true;
            };
            "@stoplight/spectral-ref-resolver" = {
              descriptor = "^1.0.4";
              pin = "1.0.4";
              runtime = true;
            };
            "@stoplight/spectral-ruleset-bundler" = {
              descriptor = "^1.5.2";
              pin = "1.5.2";
              runtime = true;
            };
            "@stoplight/spectral-ruleset-migrator" = {
              descriptor = "^1.9.5";
              pin = "1.9.5";
              runtime = true;
            };
            "@stoplight/spectral-rulesets" = {
              descriptor = ">=1";
              pin = "1.16.0";
              runtime = true;
            };
            "@stoplight/spectral-runtime" = {
              descriptor = "^1.1.2";
              pin = "1.1.2";
              runtime = true;
            };
            "@stoplight/types" = {
              descriptor = "^13.6.0";
              pin = "13.19.0";
              runtime = true;
            };
            chalk = {
              descriptor = "4.1.2";
              pin = "4.1.2";
              runtime = true;
            };
            fast-glob = {
              descriptor = "~3.2.12";
              pin = "3.2.12";
              runtime = true;
            };
            hpagent = {
              descriptor = "~1.2.0";
              pin = "1.2.0";
              runtime = true;
            };
            lodash = {
              descriptor = "~4.17.21";
              pin = "4.17.21";
              runtime = true;
            };
            pony-cause = {
              descriptor = "^1.0.0";
              pin = "1.1.1";
              runtime = true;
            };
            stacktracey = {
              descriptor = "^2.1.7";
              pin = "2.1.8";
              runtime = true;
            };
            tslib = {
              descriptor = "^2.3.0";
              pin = "2.6.1";
              runtime = true;
            };
            yargs = {
              descriptor = "17.3.1";
              pin = "17.3.1";
              runtime = true;
            };
          };
          fetchInfo = {
            narHash = "sha256-UPTmGwkupKqTDv+BuqETt+/MAVpIDTgb+TC9sQQ99wE=";
            type = "tarball";
            url = "https://registry.npmjs.org/@stoplight/spectral-cli/-/spectral-cli-6.10.1.tgz";
          };
          ident = "@stoplight/spectral-cli";
          ltype = "file";
          version = "6.10.1";
        };
      };
      "@stoplight/spectral-core" = {
        "1.18.3" = {
          depInfo = {
            "@stoplight/better-ajv-errors" = {
              descriptor = "1.0.3";
              pin = "1.0.3";
              runtime = true;
            };
            "@stoplight/json" = {
              descriptor = "~3.21.0";
              pin = "3.21.0";
              runtime = true;
            };
            "@stoplight/path" = {
              descriptor = "1.3.2";
              pin = "1.3.2";
              runtime = true;
            };
            "@stoplight/spectral-parsers" = {
              descriptor = "^1.0.0";
              pin = "1.0.3";
              runtime = true;
            };
            "@stoplight/spectral-ref-resolver" = {
              descriptor = "^1.0.0";
              pin = "1.0.4";
              runtime = true;
            };
            "@stoplight/spectral-runtime" = {
              descriptor = "^1.0.0";
              pin = "1.1.2";
              runtime = true;
            };
            "@stoplight/types" = {
              descriptor = "~13.6.0";
              pin = "13.6.0";
              runtime = true;
            };
            "@types/es-aggregate-error" = {
              descriptor = "^1.0.2";
              pin = "1.0.2";
              runtime = true;
            };
            "@types/json-schema" = {
              descriptor = "^7.0.11";
              pin = "7.0.12";
              runtime = true;
            };
            ajv = {
              descriptor = "^8.6.0";
              pin = "8.12.0";
              runtime = true;
            };
            ajv-errors = {
              descriptor = "~3.0.0";
              pin = "3.0.0";
              runtime = true;
            };
            ajv-formats = {
              descriptor = "~2.1.0";
              pin = "2.1.1";
              runtime = true;
            };
            es-aggregate-error = {
              descriptor = "^1.0.7";
              pin = "1.0.9";
              runtime = true;
            };
            jsonpath-plus = {
              descriptor = "7.1.0";
              pin = "7.1.0";
              runtime = true;
            };
            lodash = {
              descriptor = "~4.17.21";
              pin = "4.17.21";
              runtime = true;
            };
            "lodash.topath" = {
              descriptor = "^4.5.2";
              pin = "4.5.2";
              runtime = true;
            };
            minimatch = {
              descriptor = "3.1.2";
              pin = "3.1.2";
              runtime = true;
            };
            nimma = {
              descriptor = "0.2.2";
              pin = "0.2.2";
              runtime = true;
            };
            pony-cause = {
              descriptor = "^1.0.0";
              pin = "1.1.1";
              runtime = true;
            };
            simple-eval = {
              descriptor = "1.0.0";
              pin = "1.0.0";
              runtime = true;
            };
            tslib = {
              descriptor = "^2.3.0";
              pin = "2.6.1";
              runtime = true;
            };
          };
          fetchInfo = {
            narHash = "sha256-QSKcmnM+xvFarJcPYTgiFg7m6rBQAu6allFFqqW5lLg=";
            type = "tarball";
            url = "https://registry.npmjs.org/@stoplight/spectral-core/-/spectral-core-1.18.3.tgz";
          };
          ident = "@stoplight/spectral-core";
          ltype = "file";
          version = "1.18.3";
        };
      };
      "@stoplight/spectral-formats" = {
        "1.5.0" = {
          depInfo = {
            "@stoplight/json" = {
              descriptor = "^3.17.0";
              pin = "3.21.0";
              runtime = true;
            };
            "@stoplight/spectral-core" = {
              descriptor = "^1.8.0";
              pin = "1.18.3";
              runtime = true;
            };
            "@types/json-schema" = {
              descriptor = "^7.0.7";
              pin = "7.0.12";
              runtime = true;
            };
            tslib = {
              descriptor = "^2.3.1";
              pin = "2.6.1";
              runtime = true;
            };
          };
          fetchInfo = {
            narHash = "sha256-/iv1UdWDMuUp/rX504pjD7O5JKbb0xFiA/iKV2lkaVA=";
            type = "tarball";
            url = "https://registry.npmjs.org/@stoplight/spectral-formats/-/spectral-formats-1.5.0.tgz";
          };
          ident = "@stoplight/spectral-formats";
          ltype = "file";
          version = "1.5.0";
        };
      };
      "@stoplight/spectral-formatters" = {
        "1.2.0" = {
          depInfo = {
            "@stoplight/path" = {
              descriptor = "^1.3.2";
              pin = "1.3.2";
              runtime = true;
            };
            "@stoplight/spectral-core" = {
              descriptor = "^1.15.1";
              pin = "1.18.3";
              runtime = true;
            };
            "@stoplight/spectral-runtime" = {
              descriptor = "^1.1.0";
              pin = "1.1.2";
              runtime = true;
            };
            "@stoplight/types" = {
              descriptor = "^13.15.0";
              pin = "13.19.0";
              runtime = true;
            };
            chalk = {
              descriptor = "4.1.2";
              pin = "4.1.2";
              runtime = true;
            };
            cliui = {
              descriptor = "7.0.4";
              pin = "7.0.4";
              runtime = true;
            };
            lodash = {
              descriptor = "^4.17.21";
              pin = "4.17.21";
              runtime = true;
            };
            strip-ansi = {
              descriptor = "6.0";
              pin = "6.0.1";
              runtime = true;
            };
            text-table = {
              descriptor = "^0.2.0";
              pin = "0.2.0";
              runtime = true;
            };
            tslib = {
              descriptor = "^2.5.0";
              pin = "2.6.1";
              runtime = true;
            };
          };
          fetchInfo = {
            narHash = "sha256-5T1uQ0uu10cyBF3wZzRn/npHYUcV+3CidZOQWweLlNQ=";
            type = "tarball";
            url = "https://registry.npmjs.org/@stoplight/spectral-formatters/-/spectral-formatters-1.2.0.tgz";
          };
          ident = "@stoplight/spectral-formatters";
          ltype = "file";
          version = "1.2.0";
        };
      };
      "@stoplight/spectral-functions" = {
        "1.7.2" = {
          depInfo = {
            "@stoplight/better-ajv-errors" = {
              descriptor = "1.0.3";
              pin = "1.0.3";
              runtime = true;
            };
            "@stoplight/json" = {
              descriptor = "^3.17.1";
              pin = "3.21.0";
              runtime = true;
            };
            "@stoplight/spectral-core" = {
              descriptor = "^1.7.0";
              pin = "1.18.3";
              runtime = true;
            };
            "@stoplight/spectral-formats" = {
              descriptor = "^1.0.0";
              pin = "1.5.0";
              runtime = true;
            };
            "@stoplight/spectral-runtime" = {
              descriptor = "^1.1.0";
              pin = "1.1.2";
              runtime = true;
            };
            ajv = {
              descriptor = "^8.6.3";
              pin = "8.12.0";
              runtime = true;
            };
            ajv-draft-04 = {
              descriptor = "~1.0.0";
              pin = "1.0.0";
              runtime = true;
            };
            ajv-errors = {
              descriptor = "~3.0.0";
              pin = "3.0.0";
              runtime = true;
            };
            ajv-formats = {
              descriptor = "~2.1.0";
              pin = "2.1.1";
              runtime = true;
            };
            lodash = {
              descriptor = "~4.17.21";
              pin = "4.17.21";
              runtime = true;
            };
            tslib = {
              descriptor = "^2.3.0";
              pin = "2.6.1";
              runtime = true;
            };
          };
          fetchInfo = {
            narHash = "sha256-MgVOmq2M8+r5mTfFhi8eRVcmAoC3NbS/csF2nf236Os=";
            type = "tarball";
            url = "https://registry.npmjs.org/@stoplight/spectral-functions/-/spectral-functions-1.7.2.tgz";
          };
          ident = "@stoplight/spectral-functions";
          ltype = "file";
          version = "1.7.2";
        };
      };
      "@stoplight/spectral-parsers" = {
        "1.0.3" = {
          depInfo = {
            "@stoplight/json" = {
              descriptor = "~3.21.0";
              pin = "3.21.0";
              runtime = true;
            };
            "@stoplight/types" = {
              descriptor = "^13.6.0";
              pin = "13.19.0";
              runtime = true;
            };
            "@stoplight/yaml" = {
              descriptor = "~4.2.3";
              pin = "4.2.3";
              runtime = true;
            };
            tslib = {
              descriptor = "^2.3.1";
              pin = "2.6.1";
              runtime = true;
            };
          };
          fetchInfo = {
            narHash = "sha256-X50Qo7L8Qhu7BVNw4bPJ8YpwiDwlkNkPunODXhr4Y/Q=";
            type = "tarball";
            url = "https://registry.npmjs.org/@stoplight/spectral-parsers/-/spectral-parsers-1.0.3.tgz";
          };
          ident = "@stoplight/spectral-parsers";
          ltype = "file";
          version = "1.0.3";
        };
      };
      "@stoplight/spectral-ref-resolver" = {
        "1.0.4" = {
          depInfo = {
            "@stoplight/json-ref-readers" = {
              descriptor = "1.2.2";
              pin = "1.2.2";
              runtime = true;
            };
            "@stoplight/json-ref-resolver" = {
              descriptor = "~3.1.6";
              pin = "3.1.6";
              runtime = true;
            };
            "@stoplight/spectral-runtime" = {
              descriptor = "^1.1.2";
              pin = "1.1.2";
              runtime = true;
            };
            dependency-graph = {
              descriptor = "0.11.0";
              pin = "0.11.0";
              runtime = true;
            };
            tslib = {
              descriptor = "^2.3.1";
              pin = "2.6.1";
              runtime = true;
            };
          };
          fetchInfo = {
            narHash = "sha256-p/mvm5Suo7g0FOZriHaw4wZNubyfjJ/M56RAkQr8hh4=";
            type = "tarball";
            url = "https://registry.npmjs.org/@stoplight/spectral-ref-resolver/-/spectral-ref-resolver-1.0.4.tgz";
          };
          ident = "@stoplight/spectral-ref-resolver";
          ltype = "file";
          version = "1.0.4";
        };
      };
      "@stoplight/spectral-ruleset-bundler" = {
        "1.5.2" = {
          depInfo = {
            "@rollup/plugin-commonjs" = {
              descriptor = "~22.0.2";
              pin = "22.0.2";
              runtime = true;
            };
            "@stoplight/path" = {
              descriptor = "1.3.2";
              pin = "1.3.2";
              runtime = true;
            };
            "@stoplight/spectral-core" = {
              descriptor = ">=1";
              pin = "1.18.3";
              runtime = true;
            };
            "@stoplight/spectral-formats" = {
              descriptor = ">=1";
              pin = "1.5.0";
              runtime = true;
            };
            "@stoplight/spectral-functions" = {
              descriptor = ">=1";
              pin = "1.7.2";
              runtime = true;
            };
            "@stoplight/spectral-parsers" = {
              descriptor = ">=1";
              pin = "1.0.3";
              runtime = true;
            };
            "@stoplight/spectral-ref-resolver" = {
              descriptor = ">=1";
              pin = "1.0.4";
              runtime = true;
            };
            "@stoplight/spectral-ruleset-migrator" = {
              descriptor = "^1.7.4";
              pin = "1.9.5";
              runtime = true;
            };
            "@stoplight/spectral-rulesets" = {
              descriptor = ">=1";
              pin = "1.16.0";
              runtime = true;
            };
            "@stoplight/spectral-runtime" = {
              descriptor = "^1.1.0";
              pin = "1.1.2";
              runtime = true;
            };
            "@stoplight/types" = {
              descriptor = "^13.6.0";
              pin = "13.19.0";
              runtime = true;
            };
            "@types/node" = {
              descriptor = "*";
              pin = "20.4.7";
              runtime = true;
            };
            pony-cause = {
              descriptor = "1.1.1";
              pin = "1.1.1";
              runtime = true;
            };
            rollup = {
              descriptor = "~2.79.0";
              pin = "2.79.1";
              runtime = true;
            };
            tslib = {
              descriptor = "^2.3.1";
              pin = "2.6.1";
              runtime = true;
            };
            validate-npm-package-name = {
              descriptor = "3.0.0";
              pin = "3.0.0";
              runtime = true;
            };
          };
          fetchInfo = {
            narHash = "sha256-WE13WtXKERHwBcSbkjmF5i3+0mII9KT73+5CuYO6FKY=";
            type = "tarball";
            url = "https://registry.npmjs.org/@stoplight/spectral-ruleset-bundler/-/spectral-ruleset-bundler-1.5.2.tgz";
          };
          ident = "@stoplight/spectral-ruleset-bundler";
          ltype = "file";
          version = "1.5.2";
        };
      };
      "@stoplight/spectral-ruleset-migrator" = {
        "1.9.5" = {
          depInfo = {
            "@stoplight/json" = {
              descriptor = "~3.21.0";
              pin = "3.21.0";
              runtime = true;
            };
            "@stoplight/ordered-object-literal" = {
              descriptor = "~1.0.4";
              pin = "1.0.4";
              runtime = true;
            };
            "@stoplight/path" = {
              descriptor = "1.3.2";
              pin = "1.3.2";
              runtime = true;
            };
            "@stoplight/spectral-functions" = {
              descriptor = "^1.0.0";
              pin = "1.7.2";
              runtime = true;
            };
            "@stoplight/spectral-runtime" = {
              descriptor = "^1.1.0";
              pin = "1.1.2";
              runtime = true;
            };
            "@stoplight/types" = {
              descriptor = "^13.6.0";
              pin = "13.19.0";
              runtime = true;
            };
            "@stoplight/yaml" = {
              descriptor = "~4.2.3";
              pin = "4.2.3";
              runtime = true;
            };
            "@types/node" = {
              descriptor = "*";
              pin = "20.4.7";
              runtime = true;
            };
            ajv = {
              descriptor = "^8.6.0";
              pin = "8.12.0";
              runtime = true;
            };
            ast-types = {
              descriptor = "0.14.2";
              pin = "0.14.2";
              runtime = true;
            };
            astring = {
              descriptor = "^1.7.5";
              pin = "1.8.6";
              runtime = true;
            };
            reserved = {
              descriptor = "0.1.2";
              pin = "0.1.2";
              runtime = true;
            };
            tslib = {
              descriptor = "^2.3.1";
              pin = "2.6.1";
              runtime = true;
            };
            validate-npm-package-name = {
              descriptor = "3.0.0";
              pin = "3.0.0";
              runtime = true;
            };
          };
          fetchInfo = {
            narHash = "sha256-9Ff7hx3wnEAJiEv6Imsbn1xamtB1kYeDMmCTnKokCFw=";
            type = "tarball";
            url = "https://registry.npmjs.org/@stoplight/spectral-ruleset-migrator/-/spectral-ruleset-migrator-1.9.5.tgz";
          };
          ident = "@stoplight/spectral-ruleset-migrator";
          ltype = "file";
          version = "1.9.5";
        };
      };
      "@stoplight/spectral-rulesets" = {
        "1.16.0" = {
          depInfo = {
            "@asyncapi/specs" = {
              descriptor = "^4.1.0";
              pin = "4.3.1";
              runtime = true;
            };
            "@stoplight/better-ajv-errors" = {
              descriptor = "1.0.3";
              pin = "1.0.3";
              runtime = true;
            };
            "@stoplight/json" = {
              descriptor = "^3.17.0";
              pin = "3.21.0";
              runtime = true;
            };
            "@stoplight/spectral-core" = {
              descriptor = "^1.8.1";
              pin = "1.18.3";
              runtime = true;
            };
            "@stoplight/spectral-formats" = {
              descriptor = "^1.5.0";
              pin = "1.5.0";
              runtime = true;
            };
            "@stoplight/spectral-functions" = {
              descriptor = "^1.5.1";
              pin = "1.7.2";
              runtime = true;
            };
            "@stoplight/spectral-runtime" = {
              descriptor = "^1.1.1";
              pin = "1.1.2";
              runtime = true;
            };
            "@stoplight/types" = {
              descriptor = "^13.6.0";
              pin = "13.19.0";
              runtime = true;
            };
            "@types/json-schema" = {
              descriptor = "^7.0.7";
              pin = "7.0.12";
              runtime = true;
            };
            ajv = {
              descriptor = "^8.8.2";
              pin = "8.12.0";
              runtime = true;
            };
            ajv-formats = {
              descriptor = "~2.1.0";
              pin = "2.1.1";
              runtime = true;
            };
            json-schema-traverse = {
              descriptor = "^1.0.0";
              pin = "1.0.0";
              runtime = true;
            };
            lodash = {
              descriptor = "~4.17.21";
              pin = "4.17.21";
              runtime = true;
            };
            tslib = {
              descriptor = "^2.3.0";
              pin = "2.6.1";
              runtime = true;
            };
          };
          fetchInfo = {
            narHash = "sha256-W5Fbyj+lo+ywNYWDlJtM3Z1TjLEO1+XVWT0rtdVN/ro=";
            type = "tarball";
            url = "https://registry.npmjs.org/@stoplight/spectral-rulesets/-/spectral-rulesets-1.16.0.tgz";
          };
          ident = "@stoplight/spectral-rulesets";
          ltype = "file";
          version = "1.16.0";
        };
      };
      "@stoplight/spectral-runtime" = {
        "1.1.2" = {
          depInfo = {
            "@stoplight/json" = {
              descriptor = "^3.17.0";
              pin = "3.21.0";
              runtime = true;
            };
            "@stoplight/path" = {
              descriptor = "^1.3.2";
              pin = "1.3.2";
              runtime = true;
            };
            "@stoplight/types" = {
              descriptor = "^12.3.0";
              pin = "12.5.0";
              runtime = true;
            };
            abort-controller = {
              descriptor = "^3.0.0";
              pin = "3.0.0";
              runtime = true;
            };
            lodash = {
              descriptor = "^4.17.21";
              pin = "4.17.21";
              runtime = true;
            };
            node-fetch = {
              descriptor = "^2.6.7";
              pin = "2.7.0";
              runtime = true;
            };
            tslib = {
              descriptor = "^2.3.1";
              pin = "2.6.1";
              runtime = true;
            };
          };
          fetchInfo = {
            narHash = "sha256-w5t5KQyxAL8N6Dz4kLrWzvq7fnNNDzl7Dsl0rP2B0x8=";
            type = "tarball";
            url = "https://registry.npmjs.org/@stoplight/spectral-runtime/-/spectral-runtime-1.1.2.tgz";
          };
          ident = "@stoplight/spectral-runtime";
          ltype = "file";
          version = "1.1.2";
        };
      };
      "@stoplight/types" = {
        "12.5.0" = {
          depInfo = {
            "@types/json-schema" = {
              descriptor = "^7.0.4";
              pin = "7.0.12";
              runtime = true;
            };
            utility-types = {
              descriptor = "^3.10.0";
              pin = "3.10.0";
              runtime = true;
            };
          };
          fetchInfo = {
            narHash = "sha256-CV7s1G6PR1fCZXZhDKAi4Nx9m19h9xFyQyCbSRlwZ1Q=";
            type = "tarball";
            url = "https://registry.npmjs.org/@stoplight/types/-/types-12.5.0.tgz";
          };
          ident = "@stoplight/types";
          ltype = "file";
          version = "12.5.0";
        };
        "13.19.0" = {
          depInfo = {
            "@types/json-schema" = {
              descriptor = "^7.0.4";
              pin = "7.0.12";
              runtime = true;
            };
            utility-types = {
              descriptor = "^3.10.0";
              pin = "3.10.0";
              runtime = true;
            };
          };
          fetchInfo = {
            narHash = "sha256-SQHH5Z/VFWZQsq56+WYLTCNSUAIe9PqLHbmSBDA5uXY=";
            type = "tarball";
            url = "https://registry.npmjs.org/@stoplight/types/-/types-13.19.0.tgz";
          };
          ident = "@stoplight/types";
          ltype = "file";
          version = "13.19.0";
        };
        "13.6.0" = {
          depInfo = {
            "@types/json-schema" = {
              descriptor = "^7.0.4";
              pin = "7.0.12";
              runtime = true;
            };
            utility-types = {
              descriptor = "^3.10.0";
              pin = "3.10.0";
              runtime = true;
            };
          };
          fetchInfo = {
            narHash = "sha256-vXQoG83Ja65ftoGnuDrqsPva2Ll/ynXX+d9w0eCiEYU=";
            type = "tarball";
            url = "https://registry.npmjs.org/@stoplight/types/-/types-13.6.0.tgz";
          };
          ident = "@stoplight/types";
          ltype = "file";
          version = "13.6.0";
        };
      };
      "@stoplight/yaml" = {
        "4.2.3" = {
          depInfo = {
            "@stoplight/ordered-object-literal" = {
              descriptor = "^1.0.1";
              pin = "1.0.4";
              runtime = true;
            };
            "@stoplight/types" = {
              descriptor = "^13.0.0";
              pin = "13.19.0";
              runtime = true;
            };
            "@stoplight/yaml-ast-parser" = {
              descriptor = "0.0.48";
              pin = "0.0.48";
              runtime = true;
            };
            tslib = {
              descriptor = "^2.2.0";
              pin = "2.6.1";
              runtime = true;
            };
          };
          fetchInfo = {
            narHash = "sha256-2ts6W2U11hTePgL+lWMYzpituW1/lzO4lhTFjEeD3p4=";
            type = "tarball";
            url = "https://registry.npmjs.org/@stoplight/yaml/-/yaml-4.2.3.tgz";
          };
          ident = "@stoplight/yaml";
          ltype = "file";
          version = "4.2.3";
        };
      };
      "@stoplight/yaml-ast-parser" = {
        "0.0.48" = {
          fetchInfo = {
            narHash = "sha256-pftuxF//MmaZtMXnE5VZFN770+jPTnFRJrJMWCfFkh8=";
            type = "tarball";
            url = "https://registry.npmjs.org/@stoplight/yaml-ast-parser/-/yaml-ast-parser-0.0.48.tgz";
          };
          ident = "@stoplight/yaml-ast-parser";
          ltype = "file";
          treeInfo = { };
          version = "0.0.48";
        };
      };
      "@swc/helpers" = {
        "0.5.1" = {
          depInfo = {
            tslib = {
              descriptor = "^2.4.0";
              pin = "2.6.1";
              runtime = true;
            };
          };
          fetchInfo = {
            narHash = "sha256-e6uNDkWPLiCuMiT5lMUVFXk8GDCImtN9htTCskedQU0=";
            type = "tarball";
            url = "https://registry.npmjs.org/@swc/helpers/-/helpers-0.5.1.tgz";
          };
          ident = "@swc/helpers";
          ltype = "file";
          version = "0.5.1";
        };
      };
      "@types/d3-array" = {
        "3.0.5" = {
          fetchInfo = {
            narHash = "sha256-3VqHxw1kZfF0yksBb2gZDXbAcu3t2ZxKCtCl4ZMDpYw=";
            type = "tarball";
            url = "https://registry.npmjs.org/@types/d3-array/-/d3-array-3.0.5.tgz";
          };
          ident = "@types/d3-array";
          ltype = "file";
          treeInfo = { };
          version = "3.0.5";
        };
      };
      "@types/d3-color" = {
        "3.1.0" = {
          fetchInfo = {
            narHash = "sha256-gSpAzjDJ2OFuEy50u/co7g0dh0xy4d0eHxO5ITyyPuA=";
            type = "tarball";
            url = "https://registry.npmjs.org/@types/d3-color/-/d3-color-3.1.0.tgz";
          };
          ident = "@types/d3-color";
          ltype = "file";
          treeInfo = { };
          version = "3.1.0";
        };
      };
      "@types/d3-ease" = {
        "3.0.0" = {
          fetchInfo = {
            narHash = "sha256-uE2jMNzdONG18pmITFEumZiZn/ZCaxdz+jWtBCi86rU=";
            type = "tarball";
            url = "https://registry.npmjs.org/@types/d3-ease/-/d3-ease-3.0.0.tgz";
          };
          ident = "@types/d3-ease";
          ltype = "file";
          treeInfo = { };
          version = "3.0.0";
        };
      };
      "@types/d3-interpolate" = {
        "3.0.1" = {
          depInfo = {
            "@types/d3-color" = {
              descriptor = "*";
              pin = "3.1.0";
              runtime = true;
            };
          };
          fetchInfo = {
            narHash = "sha256-SGGIxRybD9g8UNPEpKwabOk1t4m7+Fmyx90FK5EZbFc=";
            type = "tarball";
            url = "https://registry.npmjs.org/@types/d3-interpolate/-/d3-interpolate-3.0.1.tgz";
          };
          ident = "@types/d3-interpolate";
          ltype = "file";
          version = "3.0.1";
        };
      };
      "@types/d3-path" = {
        "3.0.0" = {
          fetchInfo = {
            narHash = "sha256-nGfh3ICPwaWi/BROv3FbfjtoTH5Y38lCCc8yLoge0P0=";
            type = "tarball";
            url = "https://registry.npmjs.org/@types/d3-path/-/d3-path-3.0.0.tgz";
          };
          ident = "@types/d3-path";
          ltype = "file";
          treeInfo = { };
          version = "3.0.0";
        };
      };
      "@types/d3-scale" = {
        "4.0.3" = {
          depInfo = {
            "@types/d3-time" = {
              descriptor = "*";
              pin = "3.0.0";
              runtime = true;
            };
          };
          fetchInfo = {
            narHash = "sha256-4tobC8+az2jlyuW/CIDjfGVw8wNNPUglbxJogRnQWyI=";
            type = "tarball";
            url = "https://registry.npmjs.org/@types/d3-scale/-/d3-scale-4.0.3.tgz";
          };
          ident = "@types/d3-scale";
          ltype = "file";
          version = "4.0.3";
        };
      };
      "@types/d3-shape" = {
        "3.1.1" = {
          depInfo = {
            "@types/d3-path" = {
              descriptor = "*";
              pin = "3.0.0";
              runtime = true;
            };
          };
          fetchInfo = {
            narHash = "sha256-ay+PgE+eOuS6tgb9sZQLBNfHRPeemdXyy4BsfOeeXRw=";
            type = "tarball";
            url = "https://registry.npmjs.org/@types/d3-shape/-/d3-shape-3.1.1.tgz";
          };
          ident = "@types/d3-shape";
          ltype = "file";
          version = "3.1.1";
        };
      };
      "@types/d3-time" = {
        "3.0.0" = {
          fetchInfo = {
            narHash = "sha256-bUFsKe+dR2yzv7aFF/AjL079CyRI7Wib038mtxnoRZU=";
            type = "tarball";
            url = "https://registry.npmjs.org/@types/d3-time/-/d3-time-3.0.0.tgz";
          };
          ident = "@types/d3-time";
          ltype = "file";
          treeInfo = { };
          version = "3.0.0";
        };
      };
      "@types/d3-timer" = {
        "3.0.0" = {
          fetchInfo = {
            narHash = "sha256-ntGqK9FRoPY1ID8yERaEF5/2ZPxs8VzNINzpBONlTD8=";
            type = "tarball";
            url = "https://registry.npmjs.org/@types/d3-timer/-/d3-timer-3.0.0.tgz";
          };
          ident = "@types/d3-timer";
          ltype = "file";
          treeInfo = { };
          version = "3.0.0";
        };
      };
      "@types/es-aggregate-error" = {
        "1.0.2" = {
          depInfo = {
            "@types/node" = {
              descriptor = "*";
              pin = "20.4.7";
              runtime = true;
            };
          };
          fetchInfo = {
            narHash = "sha256-TobP6QKmlWk8IzUqjjXh7vwlFczGRDM2vkg08fN3uRg=";
            type = "tarball";
            url = "https://registry.npmjs.org/@types/es-aggregate-error/-/es-aggregate-error-1.0.2.tgz";
          };
          ident = "@types/es-aggregate-error";
          ltype = "file";
          version = "1.0.2";
        };
      };
      "@types/estree" = {
        "0.0.39" = {
          fetchInfo = {
            narHash = "sha256-iQQPh02C6exzFYVOFhUY1FuwYO4QNJp7jIIbmp/+kFI=";
            type = "tarball";
            url = "https://registry.npmjs.org/@types/estree/-/estree-0.0.39.tgz";
          };
          ident = "@types/estree";
          ltype = "file";
          treeInfo = { };
          version = "0.0.39";
        };
      };
      "@types/json-schema" = {
        "7.0.12" = {
          fetchInfo = {
            narHash = "sha256-SzX/nP09FBtACXo+Sbm17+d6Azvd8jgN5kspvzW7Ad4=";
            type = "tarball";
            url = "https://registry.npmjs.org/@types/json-schema/-/json-schema-7.0.12.tgz";
          };
          ident = "@types/json-schema";
          ltype = "file";
          treeInfo = { };
          version = "7.0.12";
        };
      };
      "@types/json5" = {
        "0.0.29" = {
          fetchInfo = {
            narHash = "sha256-ue+RJD8oMMzvouy4/nkfTgtKZsVs9U6YR3XbWAXsuBA=";
            type = "tarball";
            url = "https://registry.npmjs.org/@types/json5/-/json5-0.0.29.tgz";
          };
          ident = "@types/json5";
          ltype = "file";
          treeInfo = { };
          version = "0.0.29";
        };
      };
      "@types/node" = {
        "20.4.7" = {
          fetchInfo = {
            narHash = "sha256-YehDZb2j94v8Qk2+xukUdy05lvge3Q9Rdk/zZI41+Qw=";
            type = "tarball";
            url = "https://registry.npmjs.org/@types/node/-/node-20.4.7.tgz";
          };
          ident = "@types/node";
          ltype = "file";
          treeInfo = { };
          version = "20.4.7";
        };
      };
      "@types/parse-json" = {
        "4.0.0" = {
          fetchInfo = {
            narHash = "sha256-xZ8I656yZfg8U8CJFzcyJ1vRoa3zUsB/xti1O/x8fPU=";
            type = "tarball";
            url = "https://registry.npmjs.org/@types/parse-json/-/parse-json-4.0.0.tgz";
          };
          ident = "@types/parse-json";
          ltype = "file";
          treeInfo = { };
          version = "4.0.0";
        };
      };
      "@types/prop-types" = {
        "15.7.5" = {
          fetchInfo = {
            narHash = "sha256-IIwBpZ3ztJ6m80W2eTuNe8LLkxICa2AL0kbAZoLyMEA=";
            type = "tarball";
            url = "https://registry.npmjs.org/@types/prop-types/-/prop-types-15.7.5.tgz";
          };
          ident = "@types/prop-types";
          ltype = "file";
          treeInfo = { };
          version = "15.7.5";
        };
      };
      "@types/react" = {
        "18.2.18" = {
          depInfo = {
            "@types/prop-types" = {
              descriptor = "*";
              pin = "15.7.5";
              runtime = true;
            };
            "@types/scheduler" = {
              descriptor = "*";
              pin = "0.16.3";
              runtime = true;
            };
            csstype = {
              descriptor = "^3.0.2";
              pin = "3.1.2";
              runtime = true;
            };
          };
          fetchInfo = {
            narHash = "sha256-366X5ZNfkdBEwyOCIId+u0uI0+nruKEsF6iCJbdudfY=";
            type = "tarball";
            url = "https://registry.npmjs.org/@types/react/-/react-18.2.18.tgz";
          };
          ident = "@types/react";
          ltype = "file";
          version = "18.2.18";
        };
      };
      "@types/react-dom" = {
        "18.2.7" = {
          depInfo = {
            "@types/react" = {
              descriptor = "*";
              pin = "18.2.18";
              runtime = true;
            };
          };
          fetchInfo = {
            narHash = "sha256-SKFTBlUIW/IrFytP9iaXtDTPfPk5nUPaoVuT+04sMtI=";
            type = "tarball";
            url = "https://registry.npmjs.org/@types/react-dom/-/react-dom-18.2.7.tgz";
          };
          ident = "@types/react-dom";
          ltype = "file";
          version = "18.2.7";
        };
      };
      "@types/react-is" = {
        "18.2.1" = {
          depInfo = {
            "@types/react" = {
              descriptor = "*";
              pin = "18.2.18";
              runtime = true;
            };
          };
          fetchInfo = {
            narHash = "sha256-1xm0n6dI9PDdsr0XpeGmf6ENbr8R/T7Svpz8xwRGnHo=";
            type = "tarball";
            url = "https://registry.npmjs.org/@types/react-is/-/react-is-18.2.1.tgz";
          };
          ident = "@types/react-is";
          ltype = "file";
          version = "18.2.1";
        };
      };
      "@types/react-transition-group" = {
        "4.4.6" = {
          depInfo = {
            "@types/react" = {
              descriptor = "*";
              pin = "18.2.18";
              runtime = true;
            };
          };
          fetchInfo = {
            narHash = "sha256-RaUiVT0OsMFyS9eFMPm2U5H1XFTFSAUX+7sHcX0dBC4=";
            type = "tarball";
            url = "https://registry.npmjs.org/@types/react-transition-group/-/react-transition-group-4.4.6.tgz";
          };
          ident = "@types/react-transition-group";
          ltype = "file";
          version = "4.4.6";
        };
      };
      "@types/scheduler" = {
        "0.16.3" = {
          fetchInfo = {
            narHash = "sha256-Z+HwN1OmIg46OSUi2mHroHpEfCl+7tq5icwwUmJiKrU=";
            type = "tarball";
            url = "https://registry.npmjs.org/@types/scheduler/-/scheduler-0.16.3.tgz";
          };
          ident = "@types/scheduler";
          ltype = "file";
          treeInfo = { };
          version = "0.16.3";
        };
      };
      "@types/urijs" = {
        "1.19.19" = {
          fetchInfo = {
            narHash = "sha256-Hr/DekYZPufml1QmwJVssTMpfn40hINbB1Rvh4zpRoo=";
            type = "tarball";
            url = "https://registry.npmjs.org/@types/urijs/-/urijs-1.19.19.tgz";
          };
          ident = "@types/urijs";
          ltype = "file";
          treeInfo = { };
          version = "1.19.19";
        };
      };
      "@types/w3c-web-usb" = {
        "1.0.6" = {
          fetchInfo = {
            narHash = "sha256-Y1oAKTdkKcK4fCbdZnHIhoFXIHsQVxnp83X8qXt6ygI=";
            type = "tarball";
            url = "https://registry.npmjs.org/@types/w3c-web-usb/-/w3c-web-usb-1.0.6.tgz";
          };
          ident = "@types/w3c-web-usb";
          ltype = "file";
          treeInfo = { };
          version = "1.0.6";
        };
      };
      "@typescript-eslint/parser" = {
        "5.62.0" = {
          depInfo = {
            "@typescript-eslint/scope-manager" = {
              descriptor = "5.62.0";
              pin = "5.62.0";
              runtime = true;
            };
            "@typescript-eslint/types" = {
              descriptor = "5.62.0";
              pin = "5.62.0";
              runtime = true;
            };
            "@typescript-eslint/typescript-estree" = {
              descriptor = "5.62.0";
              pin = "5.62.0";
              runtime = true;
            };
            debug = {
              descriptor = "^4.3.4";
              pin = "4.3.4";
              runtime = true;
            };
          };
          fetchInfo = {
            narHash = "sha256-mF2E8M9Eso9Gnha+fS58GLGtwX4G6R+1WGdrm/7+/gc=";
            type = "tarball";
            url = "https://registry.npmjs.org/@typescript-eslint/parser/-/parser-5.62.0.tgz";
          };
          ident = "@typescript-eslint/parser";
          ltype = "file";
          peerInfo = {
            eslint = {
              descriptor = "^6.0.0 || ^7.0.0 || ^8.0.0";
            };
            typescript = {
              descriptor = "*";
              optional = true;
            };
          };
          version = "5.62.0";
        };
      };
      "@typescript-eslint/scope-manager" = {
        "5.62.0" = {
          depInfo = {
            "@typescript-eslint/types" = {
              descriptor = "5.62.0";
              pin = "5.62.0";
              runtime = true;
            };
            "@typescript-eslint/visitor-keys" = {
              descriptor = "5.62.0";
              pin = "5.62.0";
              runtime = true;
            };
          };
          fetchInfo = {
            narHash = "sha256-ot9PqZsxHfhTpu3JqID6MSdRyEoLk820w3CPylSyvEU=";
            type = "tarball";
            url = "https://registry.npmjs.org/@typescript-eslint/scope-manager/-/scope-manager-5.62.0.tgz";
          };
          ident = "@typescript-eslint/scope-manager";
          ltype = "file";
          version = "5.62.0";
        };
      };
      "@typescript-eslint/types" = {
        "5.62.0" = {
          fetchInfo = {
            narHash = "sha256-yC406tjb2QRPhmEklyg2kKBnCT6nT890i9zv+71ZgtE=";
            type = "tarball";
            url = "https://registry.npmjs.org/@typescript-eslint/types/-/types-5.62.0.tgz";
          };
          ident = "@typescript-eslint/types";
          ltype = "file";
          treeInfo = { };
          version = "5.62.0";
        };
      };
      "@typescript-eslint/typescript-estree" = {
        "5.62.0" = {
          depInfo = {
            "@typescript-eslint/types" = {
              descriptor = "5.62.0";
              pin = "5.62.0";
              runtime = true;
            };
            "@typescript-eslint/visitor-keys" = {
              descriptor = "5.62.0";
              pin = "5.62.0";
              runtime = true;
            };
            debug = {
              descriptor = "^4.3.4";
              pin = "4.3.4";
              runtime = true;
            };
            globby = {
              descriptor = "^11.1.0";
              pin = "11.1.0";
              runtime = true;
            };
            is-glob = {
              descriptor = "^4.0.3";
              pin = "4.0.3";
              runtime = true;
            };
            semver = {
              descriptor = "^7.3.7";
              pin = "7.5.4";
              runtime = true;
            };
            tsutils = {
              descriptor = "^3.21.0";
              pin = "3.21.0";
              runtime = true;
            };
          };
          fetchInfo = {
            narHash = "sha256-UHTG/QcafwUqXS+omn/jUtGuQCElc0NtxGgZwR+jWnA=";
            type = "tarball";
            url = "https://registry.npmjs.org/@typescript-eslint/typescript-estree/-/typescript-estree-5.62.0.tgz";
          };
          ident = "@typescript-eslint/typescript-estree";
          ltype = "file";
          peerInfo = {
            typescript = {
              descriptor = "*";
              optional = true;
            };
          };
          version = "5.62.0";
        };
      };
      "@typescript-eslint/visitor-keys" = {
        "5.62.0" = {
          depInfo = {
            "@typescript-eslint/types" = {
              descriptor = "5.62.0";
              pin = "5.62.0";
              runtime = true;
            };
            eslint-visitor-keys = {
              descriptor = "^3.3.0";
              pin = "3.4.3";
              runtime = true;
            };
          };
          fetchInfo = {
            narHash = "sha256-0NB2VKFQhN2WAQADY2RgaT8EuYoBvZPEP/LQ9188HbU=";
            type = "tarball";
            url = "https://registry.npmjs.org/@typescript-eslint/visitor-keys/-/visitor-keys-5.62.0.tgz";
          };
          ident = "@typescript-eslint/visitor-keys";
          ltype = "file";
          version = "5.62.0";
        };
      };
      abort-controller = {
        "3.0.0" = {
          depInfo = {
            event-target-shim = {
              descriptor = "^5.0.0";
              pin = "5.0.1";
              runtime = true;
            };
          };
          fetchInfo = {
            narHash = "sha256-8iDKo2rTwnYtzjP8LMIiR+7lAZz33Lwm1eMIZUf1KfU=";
            type = "tarball";
            url = "https://registry.npmjs.org/abort-controller/-/abort-controller-3.0.0.tgz";
          };
          ident = "abort-controller";
          ltype = "file";
          version = "3.0.0";
        };
      };
      acorn = {
        "8.10.0" = {
          binInfo = {
            binPairs = {
              acorn = "bin/acorn";
            };
          };
          fetchInfo = {
            narHash = "sha256-vmLiR0CeNXcvOY/qgxmfBWzUOTxz6rXJcp5EMe7rR3o=";
            type = "tarball";
            url = "https://registry.npmjs.org/acorn/-/acorn-8.10.0.tgz";
          };
          ident = "acorn";
          ltype = "file";
          treeInfo = { };
          version = "8.10.0";
        };
      };
      acorn-jsx = {
        "5.3.2" = {
          fetchInfo = {
            narHash = "sha256-AleG2zYzv9doV8blgXmOhx7ExOUJ+0hofIUgxOID8Q8=";
            type = "tarball";
            url = "https://registry.npmjs.org/acorn-jsx/-/acorn-jsx-5.3.2.tgz";
          };
          ident = "acorn-jsx";
          ltype = "file";
          peerInfo = {
            acorn = {
              descriptor = "^6.0.0 || ^7.0.0 || ^8.0.0";
            };
          };
          treeInfo = { };
          version = "5.3.2";
        };
      };
      ajv = {
        "6.12.6" = {
          depInfo = {
            fast-deep-equal = {
              descriptor = "^3.1.1";
              pin = "3.1.3";
              runtime = true;
            };
            fast-json-stable-stringify = {
              descriptor = "^2.0.0";
              pin = "2.1.0";
              runtime = true;
            };
            json-schema-traverse = {
              descriptor = "^0.4.1";
              pin = "0.4.1";
              runtime = true;
            };
            uri-js = {
              descriptor = "^4.2.2";
              pin = "4.4.1";
              runtime = true;
            };
          };
          fetchInfo = {
            narHash = "sha256-J73Yar5PwP9cRfKNYKEbHIVHuvfSEfLuSmkdbF8WeYI=";
            type = "tarball";
            url = "https://registry.npmjs.org/ajv/-/ajv-6.12.6.tgz";
          };
          ident = "ajv";
          ltype = "file";
          version = "6.12.6";
        };
        "8.12.0" = {
          depInfo = {
            fast-deep-equal = {
              descriptor = "^3.1.1";
              pin = "3.1.3";
              runtime = true;
            };
            json-schema-traverse = {
              descriptor = "^1.0.0";
              pin = "1.0.0";
              runtime = true;
            };
            require-from-string = {
              descriptor = "^2.0.2";
              pin = "2.0.2";
              runtime = true;
            };
            uri-js = {
              descriptor = "^4.2.2";
              pin = "4.4.1";
              runtime = true;
            };
          };
          fetchInfo = {
            narHash = "sha256-/h14AT12yDEt5tAp5pGWv5Lmy7T6JZ6SdEq9gJ8r3cE=";
            type = "tarball";
            url = "https://registry.npmjs.org/ajv/-/ajv-8.12.0.tgz";
          };
          ident = "ajv";
          ltype = "file";
          version = "8.12.0";
        };
      };
      ajv-draft-04 = {
        "1.0.0" = {
          fetchInfo = {
            narHash = "sha256-bItvp09aLvDTdXbJUE0pBDCdFhpoHqd80qG4ZICXBzE=";
            type = "tarball";
            url = "https://registry.npmjs.org/ajv-draft-04/-/ajv-draft-04-1.0.0.tgz";
          };
          ident = "ajv-draft-04";
          ltype = "file";
          peerInfo = {
            ajv = {
              descriptor = "^8.5.0";
              optional = true;
            };
          };
          treeInfo = { };
          version = "1.0.0";
        };
      };
      ajv-errors = {
        "3.0.0" = {
          fetchInfo = {
            narHash = "sha256-E51mutq3zqBmdb70wpDnqX4cG0NKBwUv4p8CSpwhN6k=";
            type = "tarball";
            url = "https://registry.npmjs.org/ajv-errors/-/ajv-errors-3.0.0.tgz";
          };
          ident = "ajv-errors";
          ltype = "file";
          peerInfo = {
            ajv = {
              descriptor = "^8.0.1";
            };
          };
          treeInfo = { };
          version = "3.0.0";
        };
      };
      ajv-formats = {
        "2.1.1" = {
          depInfo = {
            ajv = {
              descriptor = "^8.0.0";
              pin = "8.12.0";
              runtime = true;
            };
          };
          fetchInfo = {
            narHash = "sha256-u71olSGuc0KRZMh4pVjB+dlYddiiJJ6wF5v4i4TL5Sg=";
            type = "tarball";
            url = "https://registry.npmjs.org/ajv-formats/-/ajv-formats-2.1.1.tgz";
          };
          ident = "ajv-formats";
          ltype = "file";
          peerInfo = {
            ajv = {
              descriptor = "^8.0.0";
              optional = true;
            };
          };
          version = "2.1.1";
        };
      };
      ansi-colors = {
        "4.1.3" = {
          fetchInfo = {
            narHash = "sha256-fNOK3LUQW/zhDixzUciypsFVPSK+15WBZXyF19Nsp8s=";
            type = "tarball";
            url = "https://registry.npmjs.org/ansi-colors/-/ansi-colors-4.1.3.tgz";
          };
          ident = "ansi-colors";
          ltype = "file";
          treeInfo = { };
          version = "4.1.3";
        };
      };
      ansi-regex = {
        "5.0.1" = {
          fetchInfo = {
            narHash = "sha256-8FjueDq8OfpA4/cbcsda1vVcNseZPDYf+YqM56zD03Y=";
            type = "tarball";
            url = "https://registry.npmjs.org/ansi-regex/-/ansi-regex-5.0.1.tgz";
          };
          ident = "ansi-regex";
          ltype = "file";
          treeInfo = { };
          version = "5.0.1";
        };
      };
      ansi-styles = {
        "3.2.1" = {
          depInfo = {
            color-convert = {
              descriptor = "^1.9.0";
              pin = "1.9.3";
              runtime = true;
            };
          };
          fetchInfo = {
            narHash = "sha256-3VeRGkKqu2VUHvybLgjuzuTVZIYL6b4bwCEAhRF/Fzw=";
            type = "tarball";
            url = "https://registry.npmjs.org/ansi-styles/-/ansi-styles-3.2.1.tgz";
          };
          ident = "ansi-styles";
          ltype = "file";
          version = "3.2.1";
        };
        "4.3.0" = {
          depInfo = {
            color-convert = {
              descriptor = "^2.0.1";
              pin = "2.0.1";
              runtime = true;
            };
          };
          fetchInfo = {
            narHash = "sha256-Kqu6XFQU9/7zx/Nryl7Asi5QsyP1By7Ig4Sn1HbFfdc=";
            type = "tarball";
            url = "https://registry.npmjs.org/ansi-styles/-/ansi-styles-4.3.0.tgz";
          };
          ident = "ansi-styles";
          ltype = "file";
          version = "4.3.0";
        };
      };
      any-promise = {
        "1.3.0" = {
          fetchInfo = {
            narHash = "sha256-8J0LtdQu4uXN/8jgvSBlEr8RWnJ+VbtTRHpG3M1Ccag=";
            type = "tarball";
            url = "https://registry.npmjs.org/any-promise/-/any-promise-1.3.0.tgz";
          };
          ident = "any-promise";
          ltype = "file";
          treeInfo = { };
          version = "1.3.0";
        };
      };
      anymatch = {
        "3.1.3" = {
          depInfo = {
            normalize-path = {
              descriptor = "^3.0.0";
              pin = "3.0.0";
              runtime = true;
            };
            picomatch = {
              descriptor = "^2.0.4";
              pin = "2.3.1";
              runtime = true;
            };
          };
          fetchInfo = {
            narHash = "sha256-h1DssnLsJ6TCWFgkMh8DXoVT/2gZaywg0B2sseGv5eU=";
            type = "tarball";
            url = "https://registry.npmjs.org/anymatch/-/anymatch-3.1.3.tgz";
          };
          ident = "anymatch";
          ltype = "file";
          version = "3.1.3";
        };
      };
      arg = {
        "5.0.2" = {
          fetchInfo = {
            narHash = "sha256-259E4/q7az8EiYV8tzFpYZyYbtKK87+CgJjRAOa0Um4=";
            type = "tarball";
            url = "https://registry.npmjs.org/arg/-/arg-5.0.2.tgz";
          };
          ident = "arg";
          ltype = "file";
          treeInfo = { };
          version = "5.0.2";
        };
      };
      argparse = {
        "1.0.10" = {
          depInfo = {
            sprintf-js = {
              descriptor = "~1.0.2";
              pin = "1.0.3";
              runtime = true;
            };
          };
          fetchInfo = {
            narHash = "sha256-6xIfdvWgo7qjBYOsYb2ONE1VoJTC1+6TSooyZlqqhVM=";
            type = "tarball";
            url = "https://registry.npmjs.org/argparse/-/argparse-1.0.10.tgz";
          };
          ident = "argparse";
          ltype = "file";
          version = "1.0.10";
        };
        "2.0.1" = {
          fetchInfo = {
            narHash = "sha256-+v7oJKHcy2HR8XoEtVbDpl5zL5DeGcDB2Q3HO7xJaLc=";
            type = "tarball";
            url = "https://registry.npmjs.org/argparse/-/argparse-2.0.1.tgz";
          };
          ident = "argparse";
          ltype = "file";
          treeInfo = { };
          version = "2.0.1";
        };
      };
      aria-query = {
        "5.3.0" = {
          depInfo = {
            dequal = {
              descriptor = "^2.0.3";
              pin = "2.0.3";
              runtime = true;
            };
          };
          fetchInfo = {
            narHash = "sha256-TkGqLMLh6DwC+zg7RUaNyf6b3SgK+0ylZy4v3n0tgAQ=";
            type = "tarball";
            url = "https://registry.npmjs.org/aria-query/-/aria-query-5.3.0.tgz";
          };
          ident = "aria-query";
          ltype = "file";
          version = "5.3.0";
        };
      };
      array-buffer-byte-length = {
        "1.0.0" = {
          depInfo = {
            call-bind = {
              descriptor = "^1.0.2";
              pin = "1.0.2";
              runtime = true;
            };
            is-array-buffer = {
              descriptor = "^3.0.1";
              pin = "3.0.2";
              runtime = true;
            };
          };
          fetchInfo = {
            narHash = "sha256-zRY5ti2uSzFiExmvZ4msX/ze2+WOLm4HCO3RrbQOJaE=";
            type = "tarball";
            url = "https://registry.npmjs.org/array-buffer-byte-length/-/array-buffer-byte-length-1.0.0.tgz";
          };
          ident = "array-buffer-byte-length";
          ltype = "file";
          version = "1.0.0";
        };
      };
      array-includes = {
        "3.1.6" = {
          depInfo = {
            call-bind = {
              descriptor = "^1.0.2";
              pin = "1.0.2";
              runtime = true;
            };
            define-properties = {
              descriptor = "^1.1.4";
              pin = "1.2.0";
              runtime = true;
            };
            es-abstract = {
              descriptor = "^1.20.4";
              pin = "1.22.1";
              runtime = true;
            };
            get-intrinsic = {
              descriptor = "^1.1.3";
              pin = "1.2.1";
              runtime = true;
            };
            is-string = {
              descriptor = "^1.0.7";
              pin = "1.0.7";
              runtime = true;
            };
          };
          fetchInfo = {
            narHash = "sha256-dUWv9Vpkm9Q+bTJmKzlqI+YMYLoRdPikvELz3IiPjWY=";
            type = "tarball";
            url = "https://registry.npmjs.org/array-includes/-/array-includes-3.1.6.tgz";
          };
          ident = "array-includes";
          ltype = "file";
          version = "3.1.6";
        };
      };
      array-union = {
        "2.1.0" = {
          fetchInfo = {
            narHash = "sha256-bmQXg345RYsXeeq7IwVxYDrzUr9rWTXu9b8usPViYkk=";
            type = "tarball";
            url = "https://registry.npmjs.org/array-union/-/array-union-2.1.0.tgz";
          };
          ident = "array-union";
          ltype = "file";
          treeInfo = { };
          version = "2.1.0";
        };
      };
      "array.prototype.findlastindex" = {
        "1.2.2" = {
          depInfo = {
            call-bind = {
              descriptor = "^1.0.2";
              pin = "1.0.2";
              runtime = true;
            };
            define-properties = {
              descriptor = "^1.1.4";
              pin = "1.2.0";
              runtime = true;
            };
            es-abstract = {
              descriptor = "^1.20.4";
              pin = "1.22.1";
              runtime = true;
            };
            es-shim-unscopables = {
              descriptor = "^1.0.0";
              pin = "1.0.0";
              runtime = true;
            };
            get-intrinsic = {
              descriptor = "^1.1.3";
              pin = "1.2.1";
              runtime = true;
            };
          };
          fetchInfo = {
            narHash = "sha256-8T64XbO0bNE1gylkYhmGlCbVCYY1DaKmzufjuV1VB2k=";
            type = "tarball";
            url = "https://registry.npmjs.org/array.prototype.findlastindex/-/array.prototype.findlastindex-1.2.2.tgz";
          };
          ident = "array.prototype.findlastindex";
          ltype = "file";
          version = "1.2.2";
        };
      };
      "array.prototype.flat" = {
        "1.3.1" = {
          depInfo = {
            call-bind = {
              descriptor = "^1.0.2";
              pin = "1.0.2";
              runtime = true;
            };
            define-properties = {
              descriptor = "^1.1.4";
              pin = "1.2.0";
              runtime = true;
            };
            es-abstract = {
              descriptor = "^1.20.4";
              pin = "1.22.1";
              runtime = true;
            };
            es-shim-unscopables = {
              descriptor = "^1.0.0";
              pin = "1.0.0";
              runtime = true;
            };
          };
          fetchInfo = {
            narHash = "sha256-WOXmh1ZNKurEfwLXMLzB2GZksE06eMGV1GlGY9hC2n8=";
            type = "tarball";
            url = "https://registry.npmjs.org/array.prototype.flat/-/array.prototype.flat-1.3.1.tgz";
          };
          ident = "array.prototype.flat";
          ltype = "file";
          version = "1.3.1";
        };
      };
      "array.prototype.flatmap" = {
        "1.3.1" = {
          depInfo = {
            call-bind = {
              descriptor = "^1.0.2";
              pin = "1.0.2";
              runtime = true;
            };
            define-properties = {
              descriptor = "^1.1.4";
              pin = "1.2.0";
              runtime = true;
            };
            es-abstract = {
              descriptor = "^1.20.4";
              pin = "1.22.1";
              runtime = true;
            };
            es-shim-unscopables = {
              descriptor = "^1.0.0";
              pin = "1.0.0";
              runtime = true;
            };
          };
          fetchInfo = {
            narHash = "sha256-ZwXYyM+OQO61VKBHaokjjwr9dXaGO3lHfoSE+AzqxUU=";
            type = "tarball";
            url = "https://registry.npmjs.org/array.prototype.flatmap/-/array.prototype.flatmap-1.3.1.tgz";
          };
          ident = "array.prototype.flatmap";
          ltype = "file";
          version = "1.3.1";
        };
      };
      "array.prototype.tosorted" = {
        "1.1.1" = {
          depInfo = {
            call-bind = {
              descriptor = "^1.0.2";
              pin = "1.0.2";
              runtime = true;
            };
            define-properties = {
              descriptor = "^1.1.4";
              pin = "1.2.0";
              runtime = true;
            };
            es-abstract = {
              descriptor = "^1.20.4";
              pin = "1.22.1";
              runtime = true;
            };
            es-shim-unscopables = {
              descriptor = "^1.0.0";
              pin = "1.0.0";
              runtime = true;
            };
            get-intrinsic = {
              descriptor = "^1.1.3";
              pin = "1.2.1";
              runtime = true;
            };
          };
          fetchInfo = {
            narHash = "sha256-BmPvOnBhiwAc7dW20xzrDdXZMkjpoAfDSTIbeYT6Qfk=";
            type = "tarball";
            url = "https://registry.npmjs.org/array.prototype.tosorted/-/array.prototype.tosorted-1.1.1.tgz";
          };
          ident = "array.prototype.tosorted";
          ltype = "file";
          version = "1.1.1";
        };
      };
      "arraybuffer.prototype.slice" = {
        "1.0.1" = {
          depInfo = {
            array-buffer-byte-length = {
              descriptor = "^1.0.0";
              pin = "1.0.0";
              runtime = true;
            };
            call-bind = {
              descriptor = "^1.0.2";
              pin = "1.0.2";
              runtime = true;
            };
            define-properties = {
              descriptor = "^1.2.0";
              pin = "1.2.0";
              runtime = true;
            };
            get-intrinsic = {
              descriptor = "^1.2.1";
              pin = "1.2.1";
              runtime = true;
            };
            is-array-buffer = {
              descriptor = "^3.0.2";
              pin = "3.0.2";
              runtime = true;
            };
            is-shared-array-buffer = {
              descriptor = "^1.0.2";
              pin = "1.0.2";
              runtime = true;
            };
          };
          fetchInfo = {
            narHash = "sha256-ZAfDsjucuiZNdyXggR0vttM+DozrBRC+VVYRFfzsisE=";
            type = "tarball";
            url = "https://registry.npmjs.org/arraybuffer.prototype.slice/-/arraybuffer.prototype.slice-1.0.1.tgz";
          };
          ident = "arraybuffer.prototype.slice";
          ltype = "file";
          version = "1.0.1";
        };
      };
      as-table = {
        "1.0.55" = {
          depInfo = {
            printable-characters = {
              descriptor = "^1.0.42";
              pin = "1.0.42";
              runtime = true;
            };
          };
          fetchInfo = {
            narHash = "sha256-qfON5YFEaKCqTSp1sf9p14GioFiasSTLmGc4fmPDpJU=";
            type = "tarball";
            url = "https://registry.npmjs.org/as-table/-/as-table-1.0.55.tgz";
          };
          ident = "as-table";
          ltype = "file";
          version = "1.0.55";
        };
      };
      ast-types = {
        "0.14.2" = {
          depInfo = {
            tslib = {
              descriptor = "^2.0.1";
              pin = "2.6.1";
              runtime = true;
            };
          };
          fetchInfo = {
            narHash = "sha256-7oXV7cfWx1xFvFx42qYVVc6T+c9DdAxC2U3Jj51ZKko=";
            type = "tarball";
            url = "https://registry.npmjs.org/ast-types/-/ast-types-0.14.2.tgz";
          };
          ident = "ast-types";
          ltype = "file";
          version = "0.14.2";
        };
      };
      ast-types-flow = {
        "0.0.7" = {
          fetchInfo = {
            narHash = "sha256-UcLvjFpq+yr7zoyF1RcMr8cip2SZz+AumqFtZATN3aA=";
            type = "tarball";
            url = "https://registry.npmjs.org/ast-types-flow/-/ast-types-flow-0.0.7.tgz";
          };
          ident = "ast-types-flow";
          ltype = "file";
          treeInfo = { };
          version = "0.0.7";
        };
      };
      astring = {
        "1.8.6" = {
          binInfo = {
            binPairs = {
              astring = "bin/astring";
            };
          };
          fetchInfo = {
            narHash = "sha256-J/rRNKLX2+0MK/WSuh3rmiZ6l8a0TSQ1dntlvTICWhM=";
            type = "tarball";
            url = "https://registry.npmjs.org/astring/-/astring-1.8.6.tgz";
          };
          ident = "astring";
          ltype = "file";
          treeInfo = { };
          version = "1.8.6";
        };
      };
      asynckit = {
        "0.4.0" = {
          fetchInfo = {
            narHash = "sha256-ySX1KUru2VwlCX4xMQynwHNOtbX8yyqtirHD2ILEuyc=";
            type = "tarball";
            url = "https://registry.npmjs.org/asynckit/-/asynckit-0.4.0.tgz";
          };
          ident = "asynckit";
          ltype = "file";
          treeInfo = { };
          version = "0.4.0";
        };
      };
      autoprefixer = {
        "10.4.14" = {
          binInfo = {
            binPairs = {
              autoprefixer = "bin/autoprefixer";
            };
          };
          depInfo = {
            browserslist = {
              descriptor = "^4.21.5";
              pin = "4.21.10";
              runtime = true;
            };
            caniuse-lite = {
              descriptor = "^1.0.30001464";
              pin = "1.0.30001520";
              runtime = true;
            };
            "fraction.js" = {
              descriptor = "^4.2.0";
              pin = "4.2.0";
              runtime = true;
            };
            normalize-range = {
              descriptor = "^0.1.2";
              pin = "0.1.2";
              runtime = true;
            };
            picocolors = {
              descriptor = "^1.0.0";
              pin = "1.0.0";
              runtime = true;
            };
            postcss-value-parser = {
              descriptor = "^4.2.0";
              pin = "4.2.0";
              runtime = true;
            };
          };
          fetchInfo = {
            narHash = "sha256-CqH38gYJ6YFBDha//mI7Y6Og8CxALEB5/1ndK+WEV4M=";
            type = "tarball";
            url = "https://registry.npmjs.org/autoprefixer/-/autoprefixer-10.4.14.tgz";
          };
          ident = "autoprefixer";
          ltype = "file";
          peerInfo = {
            postcss = {
              descriptor = "^8.1.0";
            };
          };
          version = "10.4.14";
        };
      };
      available-typed-arrays = {
        "1.0.5" = {
          fetchInfo = {
            narHash = "sha256-2Mhjdq/W76GxYD8IyzTn23Co5WQrIDa0uXHar7RMu0s=";
            type = "tarball";
            url = "https://registry.npmjs.org/available-typed-arrays/-/available-typed-arrays-1.0.5.tgz";
          };
          ident = "available-typed-arrays";
          ltype = "file";
          treeInfo = { };
          version = "1.0.5";
        };
      };
      axe-core = {
        "4.7.2" = {
          fetchInfo = {
            narHash = "sha256-p45DRmMRWp3U8oNw5hvu/Me4rf1pTnJQPu5z2LN/FKQ=";
            type = "tarball";
            url = "https://registry.npmjs.org/axe-core/-/axe-core-4.7.2.tgz";
          };
          ident = "axe-core";
          ltype = "file";
          treeInfo = { };
          version = "4.7.2";
        };
      };
      axios = {
        "1.4.0" = {
          depInfo = {
            follow-redirects = {
              descriptor = "^1.15.0";
              pin = "1.15.2";
              runtime = true;
            };
            form-data = {
              descriptor = "^4.0.0";
              pin = "4.0.0";
              runtime = true;
            };
            proxy-from-env = {
              descriptor = "^1.1.0";
              pin = "1.1.0";
              runtime = true;
            };
          };
          fetchInfo = {
            narHash = "sha256-VGSUaFLJbsQKbxZaqktQktzztZ6TMHbEJ5Lpyuzrihs=";
            type = "tarball";
            url = "https://registry.npmjs.org/axios/-/axios-1.4.0.tgz";
          };
          ident = "axios";
          ltype = "file";
          version = "1.4.0";
        };
      };
      axobject-query = {
        "3.2.1" = {
          depInfo = {
            dequal = {
              descriptor = "^2.0.3";
              pin = "2.0.3";
              runtime = true;
            };
          };
          fetchInfo = {
            narHash = "sha256-26bT+62Cse7aRF6ttHjrTVo270PRZwJLQrYVG83TeGE=";
            type = "tarball";
            url = "https://registry.npmjs.org/axobject-query/-/axobject-query-3.2.1.tgz";
          };
          ident = "axobject-query";
          ltype = "file";
          version = "3.2.1";
        };
      };
      babel-plugin-macros = {
        "3.1.0" = {
          depInfo = {
            "@babel/runtime" = {
              descriptor = "^7.12.5";
              pin = "7.22.10";
              runtime = true;
            };
            cosmiconfig = {
              descriptor = "^7.0.0";
              pin = "7.1.0";
              runtime = true;
            };
            resolve = {
              descriptor = "^1.19.0";
              pin = "1.22.4";
              runtime = true;
            };
          };
          fetchInfo = {
            narHash = "sha256-iQ2TOwutifOLnyoUkOPUwHtd4Wq79eGpyFUqJZ2GUNY=";
            type = "tarball";
            url = "https://registry.npmjs.org/babel-plugin-macros/-/babel-plugin-macros-3.1.0.tgz";
          };
          ident = "babel-plugin-macros";
          ltype = "file";
          version = "3.1.0";
        };
      };
      backslash = {
        "0.2.0" = {
          fetchInfo = {
            narHash = "sha256-AOKRz4BTLamEpeP5v5586q/BCFDfo0um1AfozRQB6Og=";
            type = "tarball";
            url = "https://registry.npmjs.org/backslash/-/backslash-0.2.0.tgz";
          };
          ident = "backslash";
          ltype = "file";
          treeInfo = { };
          version = "0.2.0";
        };
      };
      balanced-match = {
        "1.0.2" = {
          fetchInfo = {
            narHash = "sha256-YH1+osaAiJvWUUR4VCe/Hh4eHhXS0gN3Lnr+Xd3cCzg=";
            type = "tarball";
            url = "https://registry.npmjs.org/balanced-match/-/balanced-match-1.0.2.tgz";
          };
          ident = "balanced-match";
          ltype = "file";
          treeInfo = { };
          version = "1.0.2";
        };
      };
      binary-extensions = {
        "2.2.0" = {
          fetchInfo = {
            narHash = "sha256-kDL1HV8+/e0b6CoYfVTpZymjgnwJW/QYAHRHf0R6Ih8=";
            type = "tarball";
            url = "https://registry.npmjs.org/binary-extensions/-/binary-extensions-2.2.0.tgz";
          };
          ident = "binary-extensions";
          ltype = "file";
          treeInfo = { };
          version = "2.2.0";
        };
      };
      brace-expansion = {
        "1.1.11" = {
          depInfo = {
            balanced-match = {
              descriptor = "^1.0.0";
              pin = "1.0.2";
              runtime = true;
            };
            concat-map = {
              descriptor = "0.0.1";
              pin = "0.0.1";
              runtime = true;
            };
          };
          fetchInfo = {
            narHash = "sha256-3iQ502QjW10IEFOh3qnkAIivIbQ1TO1pgQTi7p9eado=";
            type = "tarball";
            url = "https://registry.npmjs.org/brace-expansion/-/brace-expansion-1.1.11.tgz";
          };
          ident = "brace-expansion";
          ltype = "file";
          version = "1.1.11";
        };
      };
      braces = {
        "3.0.2" = {
          depInfo = {
            fill-range = {
              descriptor = "^7.0.1";
              pin = "7.0.1";
              runtime = true;
            };
          };
          fetchInfo = {
            narHash = "sha256-x3Cs+dWp0z2CXH2OaHCHtF2aWMrrV5/kFWM4+JCkcZ4=";
            type = "tarball";
            url = "https://registry.npmjs.org/braces/-/braces-3.0.2.tgz";
          };
          ident = "braces";
          ltype = "file";
          version = "3.0.2";
        };
      };
      browserslist = {
        "4.21.10" = {
          binInfo = {
            binPairs = {
              browserslist = "cli.js";
            };
          };
          depInfo = {
            caniuse-lite = {
              descriptor = "^1.0.30001517";
              pin = "1.0.30001520";
              runtime = true;
            };
            electron-to-chromium = {
              descriptor = "^1.4.477";
              pin = "1.4.491";
              runtime = true;
            };
            node-releases = {
              descriptor = "^2.0.13";
              pin = "2.0.13";
              runtime = true;
            };
            update-browserslist-db = {
              descriptor = "^1.0.11";
              pin = "1.0.11";
              runtime = true;
            };
          };
          fetchInfo = {
            narHash = "sha256-wwfld566bLYF4J9/q8Ny8Nl/O0D3TgGanEVMFC3QiVA=";
            type = "tarball";
            url = "https://registry.npmjs.org/browserslist/-/browserslist-4.21.10.tgz";
          };
          ident = "browserslist";
          ltype = "file";
          version = "4.21.10";
        };
      };
      builtins = {
        "1.0.3" = {
          fetchInfo = {
            narHash = "sha256-hgxu58fvb9EoByPI1uC7HBIp9rXxBldcOyHtBDBVBrg=";
            type = "tarball";
            url = "https://registry.npmjs.org/builtins/-/builtins-1.0.3.tgz";
          };
          ident = "builtins";
          ltype = "file";
          treeInfo = { };
          version = "1.0.3";
        };
      };
      busboy = {
        "1.6.0" = {
          depInfo = {
            streamsearch = {
              descriptor = "^1.1.0";
              pin = "1.1.0";
              runtime = true;
            };
          };
          fetchInfo = {
            narHash = "sha256-UaGI2Jzv6/ULQAuchHh60T4NNzt04S3Zeh6cenNGXlo=";
            type = "tarball";
            url = "https://registry.npmjs.org/busboy/-/busboy-1.6.0.tgz";
          };
          ident = "busboy";
          ltype = "file";
          version = "1.6.0";
        };
      };
      cac = {
        "6.7.14" = {
          fetchInfo = {
            narHash = "sha256-1yV+SKzq+aeEBSgCkin0YzxcbLVCYMYWUDocXv2BvbU=";
            type = "tarball";
            url = "https://registry.npmjs.org/cac/-/cac-6.7.14.tgz";
          };
          ident = "cac";
          ltype = "file";
          treeInfo = { };
          version = "6.7.14";
        };
      };
      call-bind = {
        "1.0.2" = {
          depInfo = {
            function-bind = {
              descriptor = "^1.1.1";
              pin = "1.1.1";
              runtime = true;
            };
            get-intrinsic = {
              descriptor = "^1.0.2";
              pin = "1.2.1";
              runtime = true;
            };
          };
          fetchInfo = {
            narHash = "sha256-CPVK05lbDE13hYj/VV8H6ZqkqCgqqP2XQL+amU5arbI=";
            type = "tarball";
            url = "https://registry.npmjs.org/call-bind/-/call-bind-1.0.2.tgz";
          };
          ident = "call-bind";
          ltype = "file";
          version = "1.0.2";
        };
      };
      call-me-maybe = {
        "1.0.2" = {
          fetchInfo = {
            narHash = "sha256-tZy2JWLzj0tMMd+lWMiaxcyqKQvpKo3yf+qVGh3s+B0=";
            type = "tarball";
            url = "https://registry.npmjs.org/call-me-maybe/-/call-me-maybe-1.0.2.tgz";
          };
          ident = "call-me-maybe";
          ltype = "file";
          treeInfo = { };
          version = "1.0.2";
        };
      };
      callsites = {
        "3.1.0" = {
          fetchInfo = {
            narHash = "sha256-1p0bBJdAZstGAys+wy86rAwOMZr6w8gyM4+dFOe62Ao=";
            type = "tarball";
            url = "https://registry.npmjs.org/callsites/-/callsites-3.1.0.tgz";
          };
          ident = "callsites";
          ltype = "file";
          treeInfo = { };
          version = "3.1.0";
        };
      };
      camelcase-css = {
        "2.0.1" = {
          fetchInfo = {
            narHash = "sha256-lvogRTyCpx97LNWNMaS3m9cQzRwxgWHmbXBryf0fXc8=";
            type = "tarball";
            url = "https://registry.npmjs.org/camelcase-css/-/camelcase-css-2.0.1.tgz";
          };
          ident = "camelcase-css";
          ltype = "file";
          treeInfo = { };
          version = "2.0.1";
        };
      };
      caniuse-lite = {
        "1.0.30001520" = {
          fetchInfo = {
            narHash = "sha256-Pq9BZ8bC5P7EdhtPfftKBmrH/9YPxHaqFDicnddxues=";
            type = "tarball";
            url = "https://registry.npmjs.org/caniuse-lite/-/caniuse-lite-1.0.30001520.tgz";
          };
          ident = "caniuse-lite";
          ltype = "file";
          treeInfo = { };
          version = "1.0.30001520";
        };
      };
      chalk = {
        "2.4.2" = {
          depInfo = {
            ansi-styles = {
              descriptor = "^3.2.1";
              pin = "3.2.1";
              runtime = true;
            };
            escape-string-regexp = {
              descriptor = "^1.0.5";
              pin = "1.0.5";
              runtime = true;
            };
            supports-color = {
              descriptor = "^5.3.0";
              pin = "5.5.0";
              runtime = true;
            };
          };
          fetchInfo = {
            narHash = "sha256-epyiOfJKhuYWuMNymawywjS+lFfsQvbhON+b8du38TQ=";
            type = "tarball";
            url = "https://registry.npmjs.org/chalk/-/chalk-2.4.2.tgz";
          };
          ident = "chalk";
          ltype = "file";
          version = "2.4.2";
        };
        "4.1.2" = {
          depInfo = {
            ansi-styles = {
              descriptor = "^4.1.0";
              pin = "4.3.0";
              runtime = true;
            };
            supports-color = {
              descriptor = "^7.1.0";
              pin = "7.2.0";
              runtime = true;
            };
          };
          fetchInfo = {
            narHash = "sha256-dxAbdhq8BxCb4ae3E1eYjt6zC/nsq3c18/ZAOIXKiT8=";
            type = "tarball";
            url = "https://registry.npmjs.org/chalk/-/chalk-4.1.2.tgz";
          };
          ident = "chalk";
          ltype = "file";
          version = "4.1.2";
        };
      };
      chokidar = {
        "3.5.3" = {
          depInfo = {
            anymatch = {
              descriptor = "~3.1.2";
              pin = "3.1.3";
              runtime = true;
            };
            braces = {
              descriptor = "~3.0.2";
              pin = "3.0.2";
              runtime = true;
            };
            fsevents = {
              descriptor = "~2.3.2";
              optional = true;
              pin = "2.3.2";
              runtime = true;
            };
            glob-parent = {
              descriptor = "~5.1.2";
              pin = "5.1.2";
              runtime = true;
            };
            is-binary-path = {
              descriptor = "~2.1.0";
              pin = "2.1.0";
              runtime = true;
            };
            is-glob = {
              descriptor = "~4.0.1";
              pin = "4.0.3";
              runtime = true;
            };
            normalize-path = {
              descriptor = "~3.0.0";
              pin = "3.0.0";
              runtime = true;
            };
            readdirp = {
              descriptor = "~3.6.0";
              pin = "3.6.0";
              runtime = true;
            };
          };
          fetchInfo = {
            narHash = "sha256-Slx/Vr6FfBtIiUULU8r/PEk+1bbG0Tcvc86kaRVwHiM=";
            type = "tarball";
            url = "https://registry.npmjs.org/chokidar/-/chokidar-3.5.3.tgz";
          };
          ident = "chokidar";
          ltype = "file";
          version = "3.5.3";
        };
      };
      classnames = {
        "2.3.2" = {
          fetchInfo = {
            narHash = "sha256-PM4QE/Ym1xswnjd2ial3mPOOMy/6bOxa1zU07RyvJR8=";
            type = "tarball";
            url = "https://registry.npmjs.org/classnames/-/classnames-2.3.2.tgz";
          };
          ident = "classnames";
          ltype = "file";
          treeInfo = { };
          version = "2.3.2";
        };
      };
      client-only = {
        "0.0.1" = {
          fetchInfo = {
            narHash = "sha256-3KQxAPiD7OwuAQLV0+nIKTdzdufYucw4OT1mcv2lhUA=";
            type = "tarball";
            url = "https://registry.npmjs.org/client-only/-/client-only-0.0.1.tgz";
          };
          ident = "client-only";
          ltype = "file";
          treeInfo = { };
          version = "0.0.1";
        };
      };
      cliui = {
        "7.0.4" = {
          depInfo = {
            string-width = {
              descriptor = "^4.2.0";
              pin = "4.2.3";
              runtime = true;
            };
            strip-ansi = {
              descriptor = "^6.0.0";
              pin = "6.0.1";
              runtime = true;
            };
            wrap-ansi = {
              descriptor = "^7.0.0";
              pin = "7.0.0";
              runtime = true;
            };
          };
          fetchInfo = {
            narHash = "sha256-nV2Fqd/nLmnxgtfDp4NuMDtAHVGsnGUVjtyNjDBmqvU=";
            type = "tarball";
            url = "https://registry.npmjs.org/cliui/-/cliui-7.0.4.tgz";
          };
          ident = "cliui";
          ltype = "file";
          version = "7.0.4";
        };
      };
      clone = {
        "1.0.4" = {
          fetchInfo = {
            narHash = "sha256-6RB8/hX1OY5L6zTOHHoUXfD/Y27sjA5C0azbpCEFV8M=";
            type = "tarball";
            url = "https://registry.npmjs.org/clone/-/clone-1.0.4.tgz";
          };
          ident = "clone";
          ltype = "file";
          treeInfo = { };
          version = "1.0.4";
        };
      };
      clsx = {
        "2.0.0" = {
          fetchInfo = {
            narHash = "sha256-p5l3z48Wal/uauFo+vlLuGF1h0go8ImS6BrVOJnG6kM=";
            type = "tarball";
            url = "https://registry.npmjs.org/clsx/-/clsx-2.0.0.tgz";
          };
          ident = "clsx";
          ltype = "file";
          treeInfo = { };
          version = "2.0.0";
        };
      };
      color-convert = {
        "1.9.3" = {
          depInfo = {
            color-name = {
              descriptor = "1.1.3";
              pin = "1.1.3";
              runtime = true;
            };
          };
          fetchInfo = {
            narHash = "sha256-o/p0tqrXMvGg2VduYwUNx05gEWI11GuHgyq9nrd6khM=";
            type = "tarball";
            url = "https://registry.npmjs.org/color-convert/-/color-convert-1.9.3.tgz";
          };
          ident = "color-convert";
          ltype = "file";
          version = "1.9.3";
        };
        "2.0.1" = {
          depInfo = {
            color-name = {
              descriptor = "~1.1.4";
              pin = "1.1.4";
              runtime = true;
            };
          };
          fetchInfo = {
            narHash = "sha256-EU7d3q55UXpfbMmk+wu8nYaxXGBK3Pwu2pIe5TVZiwc=";
            type = "tarball";
            url = "https://registry.npmjs.org/color-convert/-/color-convert-2.0.1.tgz";
          };
          ident = "color-convert";
          ltype = "file";
          version = "2.0.1";
        };
      };
      color-name = {
        "1.1.3" = {
          fetchInfo = {
            narHash = "sha256-Z7+qlowBfxZNeitMCENEfKBRnaxqLWi4+ms5SIKafc0=";
            type = "tarball";
            url = "https://registry.npmjs.org/color-name/-/color-name-1.1.3.tgz";
          };
          ident = "color-name";
          ltype = "file";
          treeInfo = { };
          version = "1.1.3";
        };
        "1.1.4" = {
          fetchInfo = {
            narHash = "sha256-mAOvtcDAZ05q6KP5tRgaO5D4jeb+/AcbIE1Z2nBG1uk=";
            type = "tarball";
            url = "https://registry.npmjs.org/color-name/-/color-name-1.1.4.tgz";
          };
          ident = "color-name";
          ltype = "file";
          treeInfo = { };
          version = "1.1.4";
        };
      };
      combined-stream = {
        "1.0.8" = {
          depInfo = {
            delayed-stream = {
              descriptor = "~1.0.0";
              pin = "1.0.0";
              runtime = true;
            };
          };
          fetchInfo = {
            narHash = "sha256-+RCvzsa/ScK8HQNe6L6WRdxOuiJuqU1cRvV7qUfEbks=";
            type = "tarball";
            url = "https://registry.npmjs.org/combined-stream/-/combined-stream-1.0.8.tgz";
          };
          ident = "combined-stream";
          ltype = "file";
          version = "1.0.8";
        };
      };
      commander = {
        "2.20.3" = {
          fetchInfo = {
            narHash = "sha256-Lhil45v7SD12GmCv/klyoXGnkisKbobmN4XYw1g8l54=";
            type = "tarball";
            url = "https://registry.npmjs.org/commander/-/commander-2.20.3.tgz";
          };
          ident = "commander";
          ltype = "file";
          treeInfo = { };
          version = "2.20.3";
        };
        "4.1.1" = {
          fetchInfo = {
            narHash = "sha256-o8t5gDs/wZAL2Kp8DmTZCsGinzLn4RNUUnEnZ79x5Hk=";
            type = "tarball";
            url = "https://registry.npmjs.org/commander/-/commander-4.1.1.tgz";
          };
          ident = "commander";
          ltype = "file";
          treeInfo = { };
          version = "4.1.1";
        };
      };
      commondir = {
        "1.0.1" = {
          fetchInfo = {
            narHash = "sha256-jGg3gZrCHXpfkaYa2AiccVfiRHA1PXKbw1NYEmze+b0=";
            type = "tarball";
            url = "https://registry.npmjs.org/commondir/-/commondir-1.0.1.tgz";
          };
          ident = "commondir";
          ltype = "file";
          treeInfo = { };
          version = "1.0.1";
        };
      };
      compare-versions = {
        "4.1.4" = {
          fetchInfo = {
            narHash = "sha256-cbXKurGrM/al82uPp7X2UYe6fUjR3PfB3oRBMdjLdyE=";
            type = "tarball";
            url = "https://registry.npmjs.org/compare-versions/-/compare-versions-4.1.4.tgz";
          };
          ident = "compare-versions";
          ltype = "file";
          treeInfo = { };
          version = "4.1.4";
        };
      };
      concat-map = {
        "0.0.1" = {
          fetchInfo = {
            narHash = "sha256-ZY5/rMtzNK56p81EGaPcoIRr+J9j7yWh4szGxIOFYFA=";
            type = "tarball";
            url = "https://registry.npmjs.org/concat-map/-/concat-map-0.0.1.tgz";
          };
          ident = "concat-map";
          ltype = "file";
          treeInfo = { };
          version = "0.0.1";
        };
      };
      convert-source-map = {
        "1.9.0" = {
          fetchInfo = {
            narHash = "sha256-9zjFbAgTFN8PnaoIBuarc6354vYjJomgtng2vak3ERQ=";
            type = "tarball";
            url = "https://registry.npmjs.org/convert-source-map/-/convert-source-map-1.9.0.tgz";
          };
          ident = "convert-source-map";
          ltype = "file";
          treeInfo = { };
          version = "1.9.0";
        };
      };
      cosmiconfig = {
        "7.1.0" = {
          depInfo = {
            "@types/parse-json" = {
              descriptor = "^4.0.0";
              pin = "4.0.0";
              runtime = true;
            };
            import-fresh = {
              descriptor = "^3.2.1";
              pin = "3.3.0";
              runtime = true;
            };
            parse-json = {
              descriptor = "^5.0.0";
              pin = "5.2.0";
              runtime = true;
            };
            path-type = {
              descriptor = "^4.0.0";
              pin = "4.0.0";
              runtime = true;
            };
            yaml = {
              descriptor = "^1.10.0";
              pin = "1.10.2";
              runtime = true;
            };
          };
          fetchInfo = {
            narHash = "sha256-Rsy6y20bwlt3wOjULRA1aWGNxF313vGryr/6B8xTz7I=";
            type = "tarball";
            url = "https://registry.npmjs.org/cosmiconfig/-/cosmiconfig-7.1.0.tgz";
          };
          ident = "cosmiconfig";
          ltype = "file";
          version = "7.1.0";
        };
      };
      cross-spawn = {
        "7.0.3" = {
          depInfo = {
            path-key = {
              descriptor = "^3.1.0";
              pin = "3.1.1";
              runtime = true;
            };
            shebang-command = {
              descriptor = "^2.0.0";
              pin = "2.0.0";
              runtime = true;
            };
            which = {
              descriptor = "^2.0.1";
              pin = "2.0.2";
              runtime = true;
            };
          };
          fetchInfo = {
            narHash = "sha256-JZEEsKxB3BAGF+e9rlh4d9UUa8JEz4dSjfAvIXrerzY=";
            type = "tarball";
            url = "https://registry.npmjs.org/cross-spawn/-/cross-spawn-7.0.3.tgz";
          };
          ident = "cross-spawn";
          ltype = "file";
          version = "7.0.3";
        };
      };
      css-unit-converter = {
        "1.1.2" = {
          fetchInfo = {
            narHash = "sha256-I10yAK53iZh+q28Lwi8JPLvY1i0Klu6iL3TaGXg+MRI=";
            type = "tarball";
            url = "https://registry.npmjs.org/css-unit-converter/-/css-unit-converter-1.1.2.tgz";
          };
          ident = "css-unit-converter";
          ltype = "file";
          treeInfo = { };
          version = "1.1.2";
        };
      };
      cssesc = {
        "3.0.0" = {
          binInfo = {
            binPairs = {
              cssesc = "bin/cssesc";
            };
          };
          fetchInfo = {
            narHash = "sha256-oNYp7WDgDmKyjj+R4wvwENq7fqYH648SiYKDCCVtZvw=";
            type = "tarball";
            url = "https://registry.npmjs.org/cssesc/-/cssesc-3.0.0.tgz";
          };
          ident = "cssesc";
          ltype = "file";
          treeInfo = { };
          version = "3.0.0";
        };
      };
      csstype = {
        "3.1.2" = {
          fetchInfo = {
            narHash = "sha256-gTHlTxB3UvjA/rIxygU25qSI5I59psA2Afiku7bneo4=";
            type = "tarball";
            url = "https://registry.npmjs.org/csstype/-/csstype-3.1.2.tgz";
          };
          ident = "csstype";
          ltype = "file";
          treeInfo = { };
          version = "3.1.2";
        };
      };
      cuid = {
        "2.1.8" = {
          fetchInfo = {
            narHash = "sha256-RFfJ79m9t0suo+HF3vD3qiJK2t2nueGPUzTVXlR5p/o=";
            type = "tarball";
            url = "https://registry.npmjs.org/cuid/-/cuid-2.1.8.tgz";
          };
          ident = "cuid";
          ltype = "file";
          treeInfo = { };
          version = "2.1.8";
        };
      };
      d3-array = {
        "3.2.4" = {
          depInfo = {
            internmap = {
              descriptor = "1 - 2";
              pin = "2.0.3";
              runtime = true;
            };
          };
          fetchInfo = {
            narHash = "sha256-7a2tClggGoqMHCndF0b38YTlWQJuCgCIsRr+HbTbpyU=";
            type = "tarball";
            url = "https://registry.npmjs.org/d3-array/-/d3-array-3.2.4.tgz";
          };
          ident = "d3-array";
          ltype = "file";
          version = "3.2.4";
        };
      };
      d3-color = {
        "3.1.0" = {
          fetchInfo = {
            narHash = "sha256-cT/t1XDkpwm9iza8haFGE4qVg6vqO856ubqZrrjGpT0=";
            type = "tarball";
            url = "https://registry.npmjs.org/d3-color/-/d3-color-3.1.0.tgz";
          };
          ident = "d3-color";
          ltype = "file";
          treeInfo = { };
          version = "3.1.0";
        };
      };
      d3-ease = {
        "3.0.1" = {
          fetchInfo = {
            narHash = "sha256-7+6k/QrZVbq9NO/rMs21kXiHkC+xDzcUGDLeuN6dxTg=";
            type = "tarball";
            url = "https://registry.npmjs.org/d3-ease/-/d3-ease-3.0.1.tgz";
          };
          ident = "d3-ease";
          ltype = "file";
          treeInfo = { };
          version = "3.0.1";
        };
      };
      d3-format = {
        "3.1.0" = {
          fetchInfo = {
            narHash = "sha256-1/gxbah6XA1hcfviytziQMqLW8ylHOBOJODyW0FXp6I=";
            type = "tarball";
            url = "https://registry.npmjs.org/d3-format/-/d3-format-3.1.0.tgz";
          };
          ident = "d3-format";
          ltype = "file";
          treeInfo = { };
          version = "3.1.0";
        };
      };
      d3-interpolate = {
        "3.0.1" = {
          depInfo = {
            d3-color = {
              descriptor = "1 - 3";
              pin = "3.1.0";
              runtime = true;
            };
          };
          fetchInfo = {
            narHash = "sha256-NRAs5hu5J/3p386YELCBth0Hzhrxg2WK/OXTy3jUfyc=";
            type = "tarball";
            url = "https://registry.npmjs.org/d3-interpolate/-/d3-interpolate-3.0.1.tgz";
          };
          ident = "d3-interpolate";
          ltype = "file";
          version = "3.0.1";
        };
      };
      d3-path = {
        "3.1.0" = {
          fetchInfo = {
            narHash = "sha256-MS70PBjwXw68XDWlu+LUvIjKOQ0EBIp7f2kUlMqyq64=";
            type = "tarball";
            url = "https://registry.npmjs.org/d3-path/-/d3-path-3.1.0.tgz";
          };
          ident = "d3-path";
          ltype = "file";
          treeInfo = { };
          version = "3.1.0";
        };
      };
      d3-scale = {
        "4.0.2" = {
          depInfo = {
            d3-array = {
              descriptor = "2.10.0 - 3";
              pin = "3.2.4";
              runtime = true;
            };
            d3-format = {
              descriptor = "1 - 3";
              pin = "3.1.0";
              runtime = true;
            };
            d3-interpolate = {
              descriptor = "1.2.0 - 3";
              pin = "3.0.1";
              runtime = true;
            };
            d3-time = {
              descriptor = "2.1.1 - 3";
              pin = "3.1.0";
              runtime = true;
            };
            d3-time-format = {
              descriptor = "2 - 4";
              pin = "4.1.0";
              runtime = true;
            };
          };
          fetchInfo = {
            narHash = "sha256-a9K9gRjZnm8R0QyyyAgcnLJOlu0N4fAkWKVx3xGa5Fg=";
            type = "tarball";
            url = "https://registry.npmjs.org/d3-scale/-/d3-scale-4.0.2.tgz";
          };
          ident = "d3-scale";
          ltype = "file";
          version = "4.0.2";
        };
      };
      d3-shape = {
        "3.2.0" = {
          depInfo = {
            d3-path = {
              descriptor = "^3.1.0";
              pin = "3.1.0";
              runtime = true;
            };
          };
          fetchInfo = {
            narHash = "sha256-uvrlf0GVmS99lkTC+14bLDkXbq4vWZT/EemJXo6wjx4=";
            type = "tarball";
            url = "https://registry.npmjs.org/d3-shape/-/d3-shape-3.2.0.tgz";
          };
          ident = "d3-shape";
          ltype = "file";
          version = "3.2.0";
        };
      };
      d3-time = {
        "3.1.0" = {
          depInfo = {
            d3-array = {
              descriptor = "2 - 3";
              pin = "3.2.4";
              runtime = true;
            };
          };
          fetchInfo = {
            narHash = "sha256-AHbVxhUy2vSTYIV7o7WQUpW3WtDORQIfMIUxHRoxkc0=";
            type = "tarball";
            url = "https://registry.npmjs.org/d3-time/-/d3-time-3.1.0.tgz";
          };
          ident = "d3-time";
          ltype = "file";
          version = "3.1.0";
        };
      };
      d3-time-format = {
        "4.1.0" = {
          depInfo = {
            d3-time = {
              descriptor = "1 - 3";
              pin = "3.1.0";
              runtime = true;
            };
          };
          fetchInfo = {
            narHash = "sha256-B53Zo8Z7SzCKn02OuYzyf5DXrwi5xsHUQ0y84zno2EA=";
            type = "tarball";
            url = "https://registry.npmjs.org/d3-time-format/-/d3-time-format-4.1.0.tgz";
          };
          ident = "d3-time-format";
          ltype = "file";
          version = "4.1.0";
        };
      };
      d3-timer = {
        "3.0.1" = {
          fetchInfo = {
            narHash = "sha256-LIzG59UnvctMfBueRcKBCghSO/efxX9l99TkSMwESI8=";
            type = "tarball";
            url = "https://registry.npmjs.org/d3-timer/-/d3-timer-3.0.1.tgz";
          };
          ident = "d3-timer";
          ltype = "file";
          treeInfo = { };
          version = "3.0.1";
        };
      };
      damerau-levenshtein = {
        "1.0.8" = {
          fetchInfo = {
            narHash = "sha256-ztLc9UYtOBIyFKSJ7WnN2JwOWKNgfPO4AQC+mkEE3rY=";
            type = "tarball";
            url = "https://registry.npmjs.org/damerau-levenshtein/-/damerau-levenshtein-1.0.8.tgz";
          };
          ident = "damerau-levenshtein";
          ltype = "file";
          treeInfo = { };
          version = "1.0.8";
        };
      };
      data-uri-to-buffer = {
        "2.0.2" = {
          fetchInfo = {
            narHash = "sha256-oEMPxXuuhxP8u65JH0t/8V3ndjrh9aS+wMSPtvRQJx4=";
            type = "tarball";
            url = "https://registry.npmjs.org/data-uri-to-buffer/-/data-uri-to-buffer-2.0.2.tgz";
          };
          ident = "data-uri-to-buffer";
          ltype = "file";
          treeInfo = { };
          version = "2.0.2";
        };
      };
      debug = {
        "3.2.7" = {
          depInfo = {
            ms = {
              descriptor = "^2.1.1";
              pin = "2.1.2";
              runtime = true;
            };
          };
          fetchInfo = {
            narHash = "sha256-I/6cOvNxwUL2s2jkzM902xCRra9lubfqNuobyY3+deI=";
            type = "tarball";
            url = "https://registry.npmjs.org/debug/-/debug-3.2.7.tgz";
          };
          ident = "debug";
          ltype = "file";
          version = "3.2.7";
        };
        "4.3.4" = {
          depInfo = {
            ms = {
              descriptor = "2.1.2";
              pin = "2.1.2";
              runtime = true;
            };
          };
          fetchInfo = {
            narHash = "sha256-S6cB3bQG4QiKORndkECqPyzcgJwPgetsh/AcbjSrW3I=";
            type = "tarball";
            url = "https://registry.npmjs.org/debug/-/debug-4.3.4.tgz";
          };
          ident = "debug";
          ltype = "file";
          peerInfo = {
            supports-color = {
              descriptor = "*";
              optional = true;
            };
          };
          version = "4.3.4";
        };
      };
      "decimal.js-light" = {
        "2.5.1" = {
          fetchInfo = {
            narHash = "sha256-mD+h3ijncUVG76e+0Sfvm4AYTWobMiUbGBGXV39QpOw=";
            type = "tarball";
            url = "https://registry.npmjs.org/decimal.js-light/-/decimal.js-light-2.5.1.tgz";
          };
          ident = "decimal.js-light";
          ltype = "file";
          treeInfo = { };
          version = "2.5.1";
        };
      };
      deep-is = {
        "0.1.4" = {
          fetchInfo = {
            narHash = "sha256-lCUSf2gkAHrLYjZ2TnOMaZM+uviLCB/UwkWf/dAZ5BE=";
            type = "tarball";
            url = "https://registry.npmjs.org/deep-is/-/deep-is-0.1.4.tgz";
          };
          ident = "deep-is";
          ltype = "file";
          treeInfo = { };
          version = "0.1.4";
        };
      };
      deepmerge = {
        "2.2.1" = {
          fetchInfo = {
            narHash = "sha256-ncWY5m4oFq5mMxvYkDeP5kquwqqBexs+LH/rImN5eGA=";
            type = "tarball";
            url = "https://registry.npmjs.org/deepmerge/-/deepmerge-2.2.1.tgz";
          };
          ident = "deepmerge";
          ltype = "file";
          treeInfo = { };
          version = "2.2.1";
        };
      };
      defaults = {
        "1.0.4" = {
          depInfo = {
            clone = {
              descriptor = "^1.0.2";
              pin = "1.0.4";
              runtime = true;
            };
          };
          fetchInfo = {
            narHash = "sha256-IA3dnncB9umkqcaZ2AmgInzG5Y+dPtqd3Z/gHM0tf/g=";
            type = "tarball";
            url = "https://registry.npmjs.org/defaults/-/defaults-1.0.4.tgz";
          };
          ident = "defaults";
          ltype = "file";
          version = "1.0.4";
        };
      };
      define-properties = {
        "1.2.0" = {
          depInfo = {
            has-property-descriptors = {
              descriptor = "^1.0.0";
              pin = "1.0.0";
              runtime = true;
            };
            object-keys = {
              descriptor = "^1.1.1";
              pin = "1.1.1";
              runtime = true;
            };
          };
          fetchInfo = {
            narHash = "sha256-U6gDRKRyIMWZlCZ/X74SgBjPBBpQ4D0mLWCF4fV3qgE=";
            type = "tarball";
            url = "https://registry.npmjs.org/define-properties/-/define-properties-1.2.0.tgz";
          };
          ident = "define-properties";
          ltype = "file";
          version = "1.2.0";
        };
      };
      delayed-stream = {
        "1.0.0" = {
          fetchInfo = {
            narHash = "sha256-kUE7OC4/g4RzhwzxU7Cj6hP07jok78tJwAsYWxWIQOc=";
            type = "tarball";
            url = "https://registry.npmjs.org/delayed-stream/-/delayed-stream-1.0.0.tgz";
          };
          ident = "delayed-stream";
          ltype = "file";
          treeInfo = { };
          version = "1.0.0";
        };
      };
      dependency-graph = {
        "0.11.0" = {
          fetchInfo = {
            narHash = "sha256-gq1D9LLSwe/nnEGEgUrW8FuDhfKUYoPrO993guFLOGA=";
            type = "tarball";
            url = "https://registry.npmjs.org/dependency-graph/-/dependency-graph-0.11.0.tgz";
          };
          ident = "dependency-graph";
          ltype = "file";
          treeInfo = { };
          version = "0.11.0";
        };
      };
      dequal = {
        "2.0.3" = {
          fetchInfo = {
            narHash = "sha256-GF9YabxZ1aw5srUlFpZEbKyc+cuNz1vJGKtR+vSE7Yc=";
            type = "tarball";
            url = "https://registry.npmjs.org/dequal/-/dequal-2.0.3.tgz";
          };
          ident = "dequal";
          ltype = "file";
          treeInfo = { };
          version = "2.0.3";
        };
      };
      didyoumean = {
        "1.2.2" = {
          fetchInfo = {
            narHash = "sha256-x8Wrd34ciGnUc9OhWAkVQxZhl4FT0W/aB0ztfWdNhxo=";
            type = "tarball";
            url = "https://registry.npmjs.org/didyoumean/-/didyoumean-1.2.2.tgz";
          };
          ident = "didyoumean";
          ltype = "file";
          treeInfo = { };
          version = "1.2.2";
        };
      };
      dir-glob = {
        "3.0.1" = {
          depInfo = {
            path-type = {
              descriptor = "^4.0.0";
              pin = "4.0.0";
              runtime = true;
            };
          };
          fetchInfo = {
            narHash = "sha256-VBtlDAN9t0rKKmCQqhsZEe7+FBMkKgQ+qSMH+0UgQuk=";
            type = "tarball";
            url = "https://registry.npmjs.org/dir-glob/-/dir-glob-3.0.1.tgz";
          };
          ident = "dir-glob";
          ltype = "file";
          version = "3.0.1";
        };
      };
      dlv = {
        "1.1.3" = {
          fetchInfo = {
            narHash = "sha256-73fK/T8ssF3XuCUZgDMkPRGUo4FnecMYktBEJySouBM=";
            type = "tarball";
            url = "https://registry.npmjs.org/dlv/-/dlv-1.1.3.tgz";
          };
          ident = "dlv";
          ltype = "file";
          treeInfo = { };
          version = "1.1.3";
        };
      };
      doctrine = {
        "2.1.0" = {
          depInfo = {
            esutils = {
              descriptor = "^2.0.2";
              pin = "2.0.3";
              runtime = true;
            };
          };
          fetchInfo = {
            narHash = "sha256-o5ERIuLV9oK9ID5yxwoD1cP2RddXaAXkSdS/LwRT2BA=";
            type = "tarball";
            url = "https://registry.npmjs.org/doctrine/-/doctrine-2.1.0.tgz";
          };
          ident = "doctrine";
          ltype = "file";
          version = "2.1.0";
        };
        "3.0.0" = {
          depInfo = {
            esutils = {
              descriptor = "^2.0.2";
              pin = "2.0.3";
              runtime = true;
            };
          };
          fetchInfo = {
            narHash = "sha256-o01Hdcu2uhZR8r2cI2b7geXXkLjjXze+96vyIoMiNzU=";
            type = "tarball";
            url = "https://registry.npmjs.org/doctrine/-/doctrine-3.0.0.tgz";
          };
          ident = "doctrine";
          ltype = "file";
          version = "3.0.0";
        };
      };
      dom-helpers = {
        "3.4.0" = {
          depInfo = {
            "@babel/runtime" = {
              descriptor = "^7.1.2";
              pin = "7.22.10";
              runtime = true;
            };
          };
          fetchInfo = {
            narHash = "sha256-H5Z8Ob0gDAHLKNudp6HKQIEVPJTIjQvrb2dtkLDkMTw=";
            type = "tarball";
            url = "https://registry.npmjs.org/dom-helpers/-/dom-helpers-3.4.0.tgz";
          };
          ident = "dom-helpers";
          ltype = "file";
          version = "3.4.0";
        };
        "5.2.1" = {
          depInfo = {
            "@babel/runtime" = {
              descriptor = "^7.8.7";
              pin = "7.22.10";
              runtime = true;
            };
            csstype = {
              descriptor = "^3.0.2";
              pin = "3.1.2";
              runtime = true;
            };
          };
          fetchInfo = {
            narHash = "sha256-DkzZGz1U902BcMC2nssAs+hULM4tJ17H+3dVUzwMopg=";
            type = "tarball";
            url = "https://registry.npmjs.org/dom-helpers/-/dom-helpers-5.2.1.tgz";
          };
          ident = "dom-helpers";
          ltype = "file";
          version = "5.2.1";
        };
      };
      electron-to-chromium = {
        "1.4.491" = {
          fetchInfo = {
            narHash = "sha256-5z8H7bxGnmZzme4MNwskN365qpcajHMc0+OOJ3fE9xk=";
            type = "tarball";
            url = "https://registry.npmjs.org/electron-to-chromium/-/electron-to-chromium-1.4.491.tgz";
          };
          ident = "electron-to-chromium";
          ltype = "file";
          treeInfo = { };
          version = "1.4.491";
        };
      };
      emoji-regex = {
        "8.0.0" = {
          fetchInfo = {
            narHash = "sha256-WRW3MHslwJkKGL+xt09TThHNLeRiKIcUGIk1j+ewTpc=";
            type = "tarball";
            url = "https://registry.npmjs.org/emoji-regex/-/emoji-regex-8.0.0.tgz";
          };
          ident = "emoji-regex";
          ltype = "file";
          treeInfo = { };
          version = "8.0.0";
        };
        "9.2.2" = {
          fetchInfo = {
            narHash = "sha256-xe6KVH2H1EXdHa5Y6sUeVZkWIZ4UESKkgS8f+/ZRNB4=";
            type = "tarball";
            url = "https://registry.npmjs.org/emoji-regex/-/emoji-regex-9.2.2.tgz";
          };
          ident = "emoji-regex";
          ltype = "file";
          treeInfo = { };
          version = "9.2.2";
        };
      };
      enhanced-resolve = {
        "5.15.0" = {
          depInfo = {
            graceful-fs = {
              descriptor = "^4.2.4";
              pin = "4.2.11";
              runtime = true;
            };
            tapable = {
              descriptor = "^2.2.0";
              pin = "2.2.1";
              runtime = true;
            };
          };
          fetchInfo = {
            narHash = "sha256-tzy2nj3A/cTD+7OyLXCa5jI9Q17uPski3MiPA1adNJA=";
            type = "tarball";
            url = "https://registry.npmjs.org/enhanced-resolve/-/enhanced-resolve-5.15.0.tgz";
          };
          ident = "enhanced-resolve";
          ltype = "file";
          version = "5.15.0";
        };
      };
      enquirer = {
        "2.4.1" = {
          depInfo = {
            ansi-colors = {
              descriptor = "^4.1.1";
              pin = "4.1.3";
              runtime = true;
            };
            strip-ansi = {
              descriptor = "^6.0.1";
              pin = "6.0.1";
              runtime = true;
            };
          };
          fetchInfo = {
            narHash = "sha256-beTKB8/v2jOhvO+Xb7kza+F4j6axlBrl8cr2Kl5edmU=";
            type = "tarball";
            url = "https://registry.npmjs.org/enquirer/-/enquirer-2.4.1.tgz";
          };
          ident = "enquirer";
          ltype = "file";
          version = "2.4.1";
        };
      };
      error-ex = {
        "1.3.2" = {
          depInfo = {
            is-arrayish = {
              descriptor = "^0.2.1";
              pin = "0.2.1";
              runtime = true;
            };
          };
          fetchInfo = {
            narHash = "sha256-daqjq1BAM46eXv0Nt+56+SGe+PTSy7sK4X6E66WwGSw=";
            type = "tarball";
            url = "https://registry.npmjs.org/error-ex/-/error-ex-1.3.2.tgz";
          };
          ident = "error-ex";
          ltype = "file";
          version = "1.3.2";
        };
      };
      es-abstract = {
        "1.22.1" = {
          depInfo = {
            array-buffer-byte-length = {
              descriptor = "^1.0.0";
              pin = "1.0.0";
              runtime = true;
            };
            "arraybuffer.prototype.slice" = {
              descriptor = "^1.0.1";
              pin = "1.0.1";
              runtime = true;
            };
            available-typed-arrays = {
              descriptor = "^1.0.5";
              pin = "1.0.5";
              runtime = true;
            };
            call-bind = {
              descriptor = "^1.0.2";
              pin = "1.0.2";
              runtime = true;
            };
            es-set-tostringtag = {
              descriptor = "^2.0.1";
              pin = "2.0.1";
              runtime = true;
            };
            es-to-primitive = {
              descriptor = "^1.2.1";
              pin = "1.2.1";
              runtime = true;
            };
            "function.prototype.name" = {
              descriptor = "^1.1.5";
              pin = "1.1.5";
              runtime = true;
            };
            get-intrinsic = {
              descriptor = "^1.2.1";
              pin = "1.2.1";
              runtime = true;
            };
            get-symbol-description = {
              descriptor = "^1.0.0";
              pin = "1.0.0";
              runtime = true;
            };
            globalthis = {
              descriptor = "^1.0.3";
              pin = "1.0.3";
              runtime = true;
            };
            gopd = {
              descriptor = "^1.0.1";
              pin = "1.0.1";
              runtime = true;
            };
            has = {
              descriptor = "^1.0.3";
              pin = "1.0.3";
              runtime = true;
            };
            has-property-descriptors = {
              descriptor = "^1.0.0";
              pin = "1.0.0";
              runtime = true;
            };
            has-proto = {
              descriptor = "^1.0.1";
              pin = "1.0.1";
              runtime = true;
            };
            has-symbols = {
              descriptor = "^1.0.3";
              pin = "1.0.3";
              runtime = true;
            };
            internal-slot = {
              descriptor = "^1.0.5";
              pin = "1.0.5";
              runtime = true;
            };
            is-array-buffer = {
              descriptor = "^3.0.2";
              pin = "3.0.2";
              runtime = true;
            };
            is-callable = {
              descriptor = "^1.2.7";
              pin = "1.2.7";
              runtime = true;
            };
            is-negative-zero = {
              descriptor = "^2.0.2";
              pin = "2.0.2";
              runtime = true;
            };
            is-regex = {
              descriptor = "^1.1.4";
              pin = "1.1.4";
              runtime = true;
            };
            is-shared-array-buffer = {
              descriptor = "^1.0.2";
              pin = "1.0.2";
              runtime = true;
            };
            is-string = {
              descriptor = "^1.0.7";
              pin = "1.0.7";
              runtime = true;
            };
            is-typed-array = {
              descriptor = "^1.1.10";
              pin = "1.1.12";
              runtime = true;
            };
            is-weakref = {
              descriptor = "^1.0.2";
              pin = "1.0.2";
              runtime = true;
            };
            object-inspect = {
              descriptor = "^1.12.3";
              pin = "1.12.3";
              runtime = true;
            };
            object-keys = {
              descriptor = "^1.1.1";
              pin = "1.1.1";
              runtime = true;
            };
            "object.assign" = {
              descriptor = "^4.1.4";
              pin = "4.1.4";
              runtime = true;
            };
            "regexp.prototype.flags" = {
              descriptor = "^1.5.0";
              pin = "1.5.0";
              runtime = true;
            };
            safe-array-concat = {
              descriptor = "^1.0.0";
              pin = "1.0.0";
              runtime = true;
            };
            safe-regex-test = {
              descriptor = "^1.0.0";
              pin = "1.0.0";
              runtime = true;
            };
            "string.prototype.trim" = {
              descriptor = "^1.2.7";
              pin = "1.2.7";
              runtime = true;
            };
            "string.prototype.trimend" = {
              descriptor = "^1.0.6";
              pin = "1.0.6";
              runtime = true;
            };
            "string.prototype.trimstart" = {
              descriptor = "^1.0.6";
              pin = "1.0.6";
              runtime = true;
            };
            typed-array-buffer = {
              descriptor = "^1.0.0";
              pin = "1.0.0";
              runtime = true;
            };
            typed-array-byte-length = {
              descriptor = "^1.0.0";
              pin = "1.0.0";
              runtime = true;
            };
            typed-array-byte-offset = {
              descriptor = "^1.0.0";
              pin = "1.0.0";
              runtime = true;
            };
            typed-array-length = {
              descriptor = "^1.0.4";
              pin = "1.0.4";
              runtime = true;
            };
            unbox-primitive = {
              descriptor = "^1.0.2";
              pin = "1.0.2";
              runtime = true;
            };
            which-typed-array = {
              descriptor = "^1.1.10";
              pin = "1.1.11";
              runtime = true;
            };
          };
          fetchInfo = {
            narHash = "sha256-eeqy1Cb9HiJktqBgV+ew8THIp3m8sw+MiC1lNgA7MXs=";
            type = "tarball";
            url = "https://registry.npmjs.org/es-abstract/-/es-abstract-1.22.1.tgz";
          };
          ident = "es-abstract";
          ltype = "file";
          version = "1.22.1";
        };
      };
      es-aggregate-error = {
        "1.0.9" = {
          depInfo = {
            define-properties = {
              descriptor = "^1.1.4";
              pin = "1.2.0";
              runtime = true;
            };
            es-abstract = {
              descriptor = "^1.20.4";
              pin = "1.22.1";
              runtime = true;
            };
            function-bind = {
              descriptor = "^1.1.1";
              pin = "1.1.1";
              runtime = true;
            };
            functions-have-names = {
              descriptor = "^1.2.3";
              pin = "1.2.3";
              runtime = true;
            };
            get-intrinsic = {
              descriptor = "^1.1.3";
              pin = "1.2.1";
              runtime = true;
            };
            globalthis = {
              descriptor = "^1.0.3";
              pin = "1.0.3";
              runtime = true;
            };
            has-property-descriptors = {
              descriptor = "^1.0.0";
              pin = "1.0.0";
              runtime = true;
            };
          };
          fetchInfo = {
            narHash = "sha256-0TMgeLHN2WjHbK18P3Hyb0pf6L4f8qr9C1Sym9ril88=";
            type = "tarball";
            url = "https://registry.npmjs.org/es-aggregate-error/-/es-aggregate-error-1.0.9.tgz";
          };
          ident = "es-aggregate-error";
          ltype = "file";
          version = "1.0.9";
        };
      };
      es-set-tostringtag = {
        "2.0.1" = {
          depInfo = {
            get-intrinsic = {
              descriptor = "^1.1.3";
              pin = "1.2.1";
              runtime = true;
            };
            has = {
              descriptor = "^1.0.3";
              pin = "1.0.3";
              runtime = true;
            };
            has-tostringtag = {
              descriptor = "^1.0.0";
              pin = "1.0.0";
              runtime = true;
            };
          };
          fetchInfo = {
            narHash = "sha256-oHVOAUcBNvm2jp6ZOAqrqqv8FIyjU3akaUjhjiuAVbg=";
            type = "tarball";
            url = "https://registry.npmjs.org/es-set-tostringtag/-/es-set-tostringtag-2.0.1.tgz";
          };
          ident = "es-set-tostringtag";
          ltype = "file";
          version = "2.0.1";
        };
      };
      es-shim-unscopables = {
        "1.0.0" = {
          depInfo = {
            has = {
              descriptor = "^1.0.3";
              pin = "1.0.3";
              runtime = true;
            };
          };
          fetchInfo = {
            narHash = "sha256-p1PtxubOfdj79colMq6VF+9oAdvtCb4eGb9X7tuymn8=";
            type = "tarball";
            url = "https://registry.npmjs.org/es-shim-unscopables/-/es-shim-unscopables-1.0.0.tgz";
          };
          ident = "es-shim-unscopables";
          ltype = "file";
          version = "1.0.0";
        };
      };
      es-to-primitive = {
        "1.2.1" = {
          depInfo = {
            is-callable = {
              descriptor = "^1.1.4";
              pin = "1.2.7";
              runtime = true;
            };
            is-date-object = {
              descriptor = "^1.0.1";
              pin = "1.0.5";
              runtime = true;
            };
            is-symbol = {
              descriptor = "^1.0.2";
              pin = "1.0.4";
              runtime = true;
            };
          };
          fetchInfo = {
            narHash = "sha256-J2bNBFeEP8hzunktaqsjfxzXlnzq9qNVtOBWm7bAXMk=";
            type = "tarball";
            url = "https://registry.npmjs.org/es-to-primitive/-/es-to-primitive-1.2.1.tgz";
          };
          ident = "es-to-primitive";
          ltype = "file";
          version = "1.2.1";
        };
      };
      es6-promise = {
        "3.3.1" = {
          fetchInfo = {
            narHash = "sha256-cIjEzmRLSNyNpYnJMqmH8P7naTlt6ZvQVmpqZ7VHGog=";
            type = "tarball";
            url = "https://registry.npmjs.org/es6-promise/-/es6-promise-3.3.1.tgz";
          };
          ident = "es6-promise";
          ltype = "file";
          treeInfo = { };
          version = "3.3.1";
        };
      };
      esbuild = {
        "0.15.18" = {
          binInfo = {
            binPairs = {
              esbuild = "bin/esbuild";
            };
          };
          depInfo = {
            "@esbuild/android-arm" = {
              descriptor = "0.15.18";
              optional = true;
              pin = "0.15.18";
              runtime = true;
            };
            "@esbuild/linux-loong64" = {
              descriptor = "0.15.18";
              optional = true;
              pin = "0.15.18";
              runtime = true;
            };
            esbuild-android-64 = {
              descriptor = "0.15.18";
              optional = true;
              pin = "0.15.18";
              runtime = true;
            };
            esbuild-android-arm64 = {
              descriptor = "0.15.18";
              optional = true;
              pin = "0.15.18";
              runtime = true;
            };
            esbuild-darwin-64 = {
              descriptor = "0.15.18";
              optional = true;
              pin = "0.15.18";
              runtime = true;
            };
            esbuild-darwin-arm64 = {
              descriptor = "0.15.18";
              optional = true;
              pin = "0.15.18";
              runtime = true;
            };
            esbuild-freebsd-64 = {
              descriptor = "0.15.18";
              optional = true;
              pin = "0.15.18";
              runtime = true;
            };
            esbuild-freebsd-arm64 = {
              descriptor = "0.15.18";
              optional = true;
              pin = "0.15.18";
              runtime = true;
            };
            esbuild-linux-32 = {
              descriptor = "0.15.18";
              optional = true;
              pin = "0.15.18";
              runtime = true;
            };
            esbuild-linux-64 = {
              descriptor = "0.15.18";
              optional = true;
              pin = "0.15.18";
              runtime = true;
            };
            esbuild-linux-arm = {
              descriptor = "0.15.18";
              optional = true;
              pin = "0.15.18";
              runtime = true;
            };
            esbuild-linux-arm64 = {
              descriptor = "0.15.18";
              optional = true;
              pin = "0.15.18";
              runtime = true;
            };
            esbuild-linux-mips64le = {
              descriptor = "0.15.18";
              optional = true;
              pin = "0.15.18";
              runtime = true;
            };
            esbuild-linux-ppc64le = {
              descriptor = "0.15.18";
              optional = true;
              pin = "0.15.18";
              runtime = true;
            };
            esbuild-linux-riscv64 = {
              descriptor = "0.15.18";
              optional = true;
              pin = "0.15.18";
              runtime = true;
            };
            esbuild-linux-s390x = {
              descriptor = "0.15.18";
              optional = true;
              pin = "0.15.18";
              runtime = true;
            };
            esbuild-netbsd-64 = {
              descriptor = "0.15.18";
              optional = true;
              pin = "0.15.18";
              runtime = true;
            };
            esbuild-openbsd-64 = {
              descriptor = "0.15.18";
              optional = true;
              pin = "0.15.18";
              runtime = true;
            };
            esbuild-sunos-64 = {
              descriptor = "0.15.18";
              optional = true;
              pin = "0.15.18";
              runtime = true;
            };
            esbuild-windows-32 = {
              descriptor = "0.15.18";
              optional = true;
              pin = "0.15.18";
              runtime = true;
            };
            esbuild-windows-64 = {
              descriptor = "0.15.18";
              optional = true;
              pin = "0.15.18";
              runtime = true;
            };
            esbuild-windows-arm64 = {
              descriptor = "0.15.18";
              optional = true;
              pin = "0.15.18";
              runtime = true;
            };
          };
          fetchInfo = {
            narHash = "sha256-cpOrpOfJ3FbajYBcW/1n7PbZVlqor+fZb0Mi0Gb2/Dc=";
            type = "tarball";
            url = "https://registry.npmjs.org/esbuild/-/esbuild-0.15.18.tgz";
          };
          ident = "esbuild";
          lifecycle = {
            install = true;
          };
          ltype = "file";
          version = "0.15.18";
        };
      };
      esbuild-android-64 = {
        "0.15.18" = {
          fetchInfo = {
            narHash = "sha256-YvwlUTl8HmAskzdWhXPawQuWxwN35LUZmr94kh/pjaw=";
            type = "tarball";
            url = "https://registry.npmjs.org/esbuild-android-64/-/esbuild-android-64-0.15.18.tgz";
          };
          ident = "esbuild-android-64";
          ltype = "file";
          sysInfo = {
            cpu = [
              "x86_64"
            ];
            os = [
              "unknown"
            ];
          };
          treeInfo = { };
          version = "0.15.18";
        };
      };
      esbuild-android-arm64 = {
        "0.15.18" = {
          fetchInfo = {
            narHash = "sha256-QsV003tW7Yud+ozTSDAiH2O9dndB/pa11MUsnb9jzRA=";
            type = "tarball";
            url = "https://registry.npmjs.org/esbuild-android-arm64/-/esbuild-android-arm64-0.15.18.tgz";
          };
          ident = "esbuild-android-arm64";
          ltype = "file";
          sysInfo = {
            cpu = [
              "aarch64"
            ];
            os = [
              "unknown"
            ];
          };
          treeInfo = { };
          version = "0.15.18";
        };
      };
      esbuild-darwin-64 = {
        "0.15.18" = {
          fetchInfo = {
            narHash = "sha256-RV3gicVhwBxwWx9yMimnoXpPZ1vvjiTxscuHYyFMeIM=";
            type = "tarball";
            url = "https://registry.npmjs.org/esbuild-darwin-64/-/esbuild-darwin-64-0.15.18.tgz";
          };
          ident = "esbuild-darwin-64";
          ltype = "file";
          sysInfo = {
            cpu = [
              "x86_64"
            ];
            os = [
              "darwin"
            ];
          };
          treeInfo = { };
          version = "0.15.18";
        };
      };
      esbuild-darwin-arm64 = {
        "0.15.18" = {
          fetchInfo = {
            narHash = "sha256-X1HbpCceI38u4YWJgfIwZVXNuyowpuMbw+Ud4M+YOkc=";
            type = "tarball";
            url = "https://registry.npmjs.org/esbuild-darwin-arm64/-/esbuild-darwin-arm64-0.15.18.tgz";
          };
          ident = "esbuild-darwin-arm64";
          ltype = "file";
          sysInfo = {
            cpu = [
              "aarch64"
            ];
            os = [
              "darwin"
            ];
          };
          treeInfo = { };
          version = "0.15.18";
        };
      };
      esbuild-freebsd-64 = {
        "0.15.18" = {
          fetchInfo = {
            narHash = "sha256-rf4t/Ivp+8HjrxEZYDpMSEWe0l4rFtKLxvWdMfIt4+0=";
            type = "tarball";
            url = "https://registry.npmjs.org/esbuild-freebsd-64/-/esbuild-freebsd-64-0.15.18.tgz";
          };
          ident = "esbuild-freebsd-64";
          ltype = "file";
          sysInfo = {
            cpu = [
              "x86_64"
            ];
            os = [
              "freebsd"
            ];
          };
          treeInfo = { };
          version = "0.15.18";
        };
      };
      esbuild-freebsd-arm64 = {
        "0.15.18" = {
          fetchInfo = {
            narHash = "sha256-8Nj2Ur0ZixwRdAEOisOcMjXQQQhGJug7bK/v/UUgJNY=";
            type = "tarball";
            url = "https://registry.npmjs.org/esbuild-freebsd-arm64/-/esbuild-freebsd-arm64-0.15.18.tgz";
          };
          ident = "esbuild-freebsd-arm64";
          ltype = "file";
          sysInfo = {
            cpu = [
              "aarch64"
            ];
            os = [
              "freebsd"
            ];
          };
          treeInfo = { };
          version = "0.15.18";
        };
      };
      esbuild-linux-32 = {
        "0.15.18" = {
          fetchInfo = {
            narHash = "sha256-ZXng0ylgmcd38oAqzO2PUaEbd3xUtyCZze6ghTJYfnA=";
            type = "tarball";
            url = "https://registry.npmjs.org/esbuild-linux-32/-/esbuild-linux-32-0.15.18.tgz";
          };
          ident = "esbuild-linux-32";
          ltype = "file";
          sysInfo = {
            cpu = [
              "i686"
            ];
            os = [
              "linux"
            ];
          };
          treeInfo = { };
          version = "0.15.18";
        };
      };
      esbuild-linux-64 = {
        "0.15.18" = {
          fetchInfo = {
            narHash = "sha256-2g6YIq0odtIKb0SFdkvpYH7vM4Buf3YRatkrw7goluk=";
            type = "tarball";
            url = "https://registry.npmjs.org/esbuild-linux-64/-/esbuild-linux-64-0.15.18.tgz";
          };
          ident = "esbuild-linux-64";
          ltype = "file";
          sysInfo = {
            cpu = [
              "x86_64"
            ];
            os = [
              "linux"
            ];
          };
          treeInfo = { };
          version = "0.15.18";
        };
      };
      esbuild-linux-arm = {
        "0.15.18" = {
          fetchInfo = {
            narHash = "sha256-Kkwn6tVzLbX3T+1IC9dQ+Z87vHw3NchleGaww3rBZ44=";
            type = "tarball";
            url = "https://registry.npmjs.org/esbuild-linux-arm/-/esbuild-linux-arm-0.15.18.tgz";
          };
          ident = "esbuild-linux-arm";
          ltype = "file";
          sysInfo = {
            cpu = [
              "aarch"
            ];
            os = [
              "linux"
            ];
          };
          treeInfo = { };
          version = "0.15.18";
        };
      };
      esbuild-linux-arm64 = {
        "0.15.18" = {
          fetchInfo = {
            narHash = "sha256-U1EhUyPd3cTDQVZf5dD2HgysmDne9DOzukZXEx1YUJg=";
            type = "tarball";
            url = "https://registry.npmjs.org/esbuild-linux-arm64/-/esbuild-linux-arm64-0.15.18.tgz";
          };
          ident = "esbuild-linux-arm64";
          ltype = "file";
          sysInfo = {
            cpu = [
              "aarch64"
            ];
            os = [
              "linux"
            ];
          };
          treeInfo = { };
          version = "0.15.18";
        };
      };
      esbuild-linux-mips64le = {
        "0.15.18" = {
          fetchInfo = {
            narHash = "sha256-sNN1UuuVXXHzd/feSL2H2DaY/FBc0Ie1+M3dOu0zkLM=";
            type = "tarball";
            url = "https://registry.npmjs.org/esbuild-linux-mips64le/-/esbuild-linux-mips64le-0.15.18.tgz";
          };
          ident = "esbuild-linux-mips64le";
          ltype = "file";
          sysInfo = {
            cpu = [
              "mipsel"
            ];
            os = [
              "linux"
            ];
          };
          treeInfo = { };
          version = "0.15.18";
        };
      };
      esbuild-linux-ppc64le = {
        "0.15.18" = {
          fetchInfo = {
            narHash = "sha256-3l+rynDvkRpR2goSTj46VGOJeyE2e5fji66QtA6t+/w=";
            type = "tarball";
            url = "https://registry.npmjs.org/esbuild-linux-ppc64le/-/esbuild-linux-ppc64le-0.15.18.tgz";
          };
          ident = "esbuild-linux-ppc64le";
          ltype = "file";
          sysInfo = {
            cpu = [
              "powerpc64le"
            ];
            os = [
              "linux"
            ];
          };
          treeInfo = { };
          version = "0.15.18";
        };
      };
      esbuild-linux-riscv64 = {
        "0.15.18" = {
          fetchInfo = {
            narHash = "sha256-kVj54+p8WlbIus3tCEiozzLkfCZyeV+uMC7BKzLzEMk=";
            type = "tarball";
            url = "https://registry.npmjs.org/esbuild-linux-riscv64/-/esbuild-linux-riscv64-0.15.18.tgz";
          };
          ident = "esbuild-linux-riscv64";
          ltype = "file";
          sysInfo = {
            cpu = [
              "riscv64"
            ];
            os = [
              "linux"
            ];
          };
          treeInfo = { };
          version = "0.15.18";
        };
      };
      esbuild-linux-s390x = {
        "0.15.18" = {
          fetchInfo = {
            narHash = "sha256-OA1fXCqUFi3GgTre8uHj29JxILq9VHjrz/134I+4CM8=";
            type = "tarball";
            url = "https://registry.npmjs.org/esbuild-linux-s390x/-/esbuild-linux-s390x-0.15.18.tgz";
          };
          ident = "esbuild-linux-s390x";
          ltype = "file";
          sysInfo = {
            cpu = [
              "unknown"
            ];
            os = [
              "linux"
            ];
          };
          treeInfo = { };
          version = "0.15.18";
        };
      };
      esbuild-netbsd-64 = {
        "0.15.18" = {
          fetchInfo = {
            narHash = "sha256-UNL29zwMndGNakoNZK7aHELh+FphYz39ugnmT//c2e4=";
            type = "tarball";
            url = "https://registry.npmjs.org/esbuild-netbsd-64/-/esbuild-netbsd-64-0.15.18.tgz";
          };
          ident = "esbuild-netbsd-64";
          ltype = "file";
          sysInfo = {
            cpu = [
              "x86_64"
            ];
            os = [
              "netbsd"
            ];
          };
          treeInfo = { };
          version = "0.15.18";
        };
      };
      esbuild-openbsd-64 = {
        "0.15.18" = {
          fetchInfo = {
            narHash = "sha256-BRWDmCVj/C4A9IZwG1EpxsLksT+0ZJlgYDHJbVxIDVI=";
            type = "tarball";
            url = "https://registry.npmjs.org/esbuild-openbsd-64/-/esbuild-openbsd-64-0.15.18.tgz";
          };
          ident = "esbuild-openbsd-64";
          ltype = "file";
          sysInfo = {
            cpu = [
              "x86_64"
            ];
            os = [
              "openbsd"
            ];
          };
          treeInfo = { };
          version = "0.15.18";
        };
      };
      esbuild-sunos-64 = {
        "0.15.18" = {
          fetchInfo = {
            narHash = "sha256-KFYiZ4bivnA8VfFQo9Z1OZkFr8XyLtVdRPHUfTpoe6U=";
            type = "tarball";
            url = "https://registry.npmjs.org/esbuild-sunos-64/-/esbuild-sunos-64-0.15.18.tgz";
          };
          ident = "esbuild-sunos-64";
          ltype = "file";
          sysInfo = {
            cpu = [
              "x86_64"
            ];
            os = [
              "sunprocess"
            ];
          };
          treeInfo = { };
          version = "0.15.18";
        };
      };
      esbuild-windows-32 = {
        "0.15.18" = {
          fetchInfo = {
            narHash = "sha256-RUR3vp/WsyRmv2zgloggIH/W4Jkymit6J8uPsqP9jtM=";
            type = "tarball";
            url = "https://registry.npmjs.org/esbuild-windows-32/-/esbuild-windows-32-0.15.18.tgz";
          };
          ident = "esbuild-windows-32";
          ltype = "file";
          sysInfo = {
            cpu = [
              "i686"
            ];
            os = [
              "win32"
            ];
          };
          treeInfo = { };
          version = "0.15.18";
        };
      };
      esbuild-windows-64 = {
        "0.15.18" = {
          fetchInfo = {
            narHash = "sha256-2MqvXDlaUcmuPydHKBKC1+27HswqSy0tOpDgz/DKOlU=";
            type = "tarball";
            url = "https://registry.npmjs.org/esbuild-windows-64/-/esbuild-windows-64-0.15.18.tgz";
          };
          ident = "esbuild-windows-64";
          ltype = "file";
          sysInfo = {
            cpu = [
              "x86_64"
            ];
            os = [
              "win32"
            ];
          };
          treeInfo = { };
          version = "0.15.18";
        };
      };
      esbuild-windows-arm64 = {
        "0.15.18" = {
          fetchInfo = {
            narHash = "sha256-y0vn1/J9sIDIotDMDJilSYGfIjh34iD+o88inh+V2BQ=";
            type = "tarball";
            url = "https://registry.npmjs.org/esbuild-windows-arm64/-/esbuild-windows-arm64-0.15.18.tgz";
          };
          ident = "esbuild-windows-arm64";
          ltype = "file";
          sysInfo = {
            cpu = [
              "aarch64"
            ];
            os = [
              "win32"
            ];
          };
          treeInfo = { };
          version = "0.15.18";
        };
      };
      escalade = {
        "3.1.1" = {
          fetchInfo = {
            narHash = "sha256-5BSRjy0hMk0+ydgMP5t57Y4ea7VnLGGH3YIkNT9a11E=";
            type = "tarball";
            url = "https://registry.npmjs.org/escalade/-/escalade-3.1.1.tgz";
          };
          ident = "escalade";
          ltype = "file";
          treeInfo = { };
          version = "3.1.1";
        };
      };
      escape-string-regexp = {
        "1.0.5" = {
          fetchInfo = {
            narHash = "sha256-jI2WTcziWydQXDepnqeq9ZLmmJeODhVO2w1qLvZc90Q=";
            type = "tarball";
            url = "https://registry.npmjs.org/escape-string-regexp/-/escape-string-regexp-1.0.5.tgz";
          };
          ident = "escape-string-regexp";
          ltype = "file";
          treeInfo = { };
          version = "1.0.5";
        };
        "4.0.0" = {
          fetchInfo = {
            narHash = "sha256-d7WCjjMj36VTWLhrU8YwNOQ0ed2OBaAQBxvuLKvsONc=";
            type = "tarball";
            url = "https://registry.npmjs.org/escape-string-regexp/-/escape-string-regexp-4.0.0.tgz";
          };
          ident = "escape-string-regexp";
          ltype = "file";
          treeInfo = { };
          version = "4.0.0";
        };
      };
      eslint = {
        "8.46.0" = {
          binInfo = {
            binPairs = {
              eslint = "bin/eslint.js";
            };
          };
          depInfo = {
            "@eslint-community/eslint-utils" = {
              descriptor = "^4.2.0";
              pin = "4.4.0";
              runtime = true;
            };
            "@eslint-community/regexpp" = {
              descriptor = "^4.6.1";
              pin = "4.6.2";
              runtime = true;
            };
            "@eslint/eslintrc" = {
              descriptor = "^2.1.1";
              pin = "2.1.2";
              runtime = true;
            };
            "@eslint/js" = {
              descriptor = "^8.46.0";
              pin = "8.47.0";
              runtime = true;
            };
            "@humanwhocodes/config-array" = {
              descriptor = "^0.11.10";
              pin = "0.11.10";
              runtime = true;
            };
            "@humanwhocodes/module-importer" = {
              descriptor = "^1.0.1";
              pin = "1.0.1";
              runtime = true;
            };
            "@nodelib/fs.walk" = {
              descriptor = "^1.2.8";
              pin = "1.2.8";
              runtime = true;
            };
            ajv = {
              descriptor = "^6.12.4";
              pin = "6.12.6";
              runtime = true;
            };
            chalk = {
              descriptor = "^4.0.0";
              pin = "4.1.2";
              runtime = true;
            };
            cross-spawn = {
              descriptor = "^7.0.2";
              pin = "7.0.3";
              runtime = true;
            };
            debug = {
              descriptor = "^4.3.2";
              pin = "4.3.4";
              runtime = true;
            };
            doctrine = {
              descriptor = "^3.0.0";
              pin = "3.0.0";
              runtime = true;
            };
            escape-string-regexp = {
              descriptor = "^4.0.0";
              pin = "4.0.0";
              runtime = true;
            };
            eslint-scope = {
              descriptor = "^7.2.2";
              pin = "7.2.2";
              runtime = true;
            };
            eslint-visitor-keys = {
              descriptor = "^3.4.2";
              pin = "3.4.3";
              runtime = true;
            };
            espree = {
              descriptor = "^9.6.1";
              pin = "9.6.1";
              runtime = true;
            };
            esquery = {
              descriptor = "^1.4.2";
              pin = "1.5.0";
              runtime = true;
            };
            esutils = {
              descriptor = "^2.0.2";
              pin = "2.0.3";
              runtime = true;
            };
            fast-deep-equal = {
              descriptor = "^3.1.3";
              pin = "3.1.3";
              runtime = true;
            };
            file-entry-cache = {
              descriptor = "^6.0.1";
              pin = "6.0.1";
              runtime = true;
            };
            find-up = {
              descriptor = "^5.0.0";
              pin = "5.0.0";
              runtime = true;
            };
            glob-parent = {
              descriptor = "^6.0.2";
              pin = "6.0.2";
              runtime = true;
            };
            globals = {
              descriptor = "^13.19.0";
              pin = "13.21.0";
              runtime = true;
            };
            graphemer = {
              descriptor = "^1.4.0";
              pin = "1.4.0";
              runtime = true;
            };
            ignore = {
              descriptor = "^5.2.0";
              pin = "5.2.4";
              runtime = true;
            };
            imurmurhash = {
              descriptor = "^0.1.4";
              pin = "0.1.4";
              runtime = true;
            };
            is-glob = {
              descriptor = "^4.0.0";
              pin = "4.0.3";
              runtime = true;
            };
            is-path-inside = {
              descriptor = "^3.0.3";
              pin = "3.0.3";
              runtime = true;
            };
            js-yaml = {
              descriptor = "^4.1.0";
              pin = "4.1.0";
              runtime = true;
            };
            json-stable-stringify-without-jsonify = {
              descriptor = "^1.0.1";
              pin = "1.0.1";
              runtime = true;
            };
            levn = {
              descriptor = "^0.4.1";
              pin = "0.4.1";
              runtime = true;
            };
            "lodash.merge" = {
              descriptor = "^4.6.2";
              pin = "4.6.2";
              runtime = true;
            };
            minimatch = {
              descriptor = "^3.1.2";
              pin = "3.1.2";
              runtime = true;
            };
            natural-compare = {
              descriptor = "^1.4.0";
              pin = "1.4.0";
              runtime = true;
            };
            optionator = {
              descriptor = "^0.9.3";
              pin = "0.9.3";
              runtime = true;
            };
            strip-ansi = {
              descriptor = "^6.0.1";
              pin = "6.0.1";
              runtime = true;
            };
            text-table = {
              descriptor = "^0.2.0";
              pin = "0.2.0";
              runtime = true;
            };
          };
          fetchInfo = {
            narHash = "sha256-xQ/jOerD9OOXNVQw8sepHgYLqoq2nFBK5jTv6XYOvRk=";
            type = "tarball";
            url = "https://registry.npmjs.org/eslint/-/eslint-8.46.0.tgz";
          };
          ident = "eslint";
          ltype = "file";
          version = "8.46.0";
        };
      };
      eslint-config-next = {
        "13.4.12" = {
          depInfo = {
            "@next/eslint-plugin-next" = {
              descriptor = "13.4.12";
              pin = "13.4.12";
              runtime = true;
            };
            "@rushstack/eslint-patch" = {
              descriptor = "^1.1.3";
              pin = "1.3.3";
              runtime = true;
            };
            "@typescript-eslint/parser" = {
              descriptor = "^5.42.0";
              pin = "5.62.0";
              runtime = true;
            };
            eslint-import-resolver-node = {
              descriptor = "^0.3.6";
              pin = "0.3.9";
              runtime = true;
            };
            eslint-import-resolver-typescript = {
              descriptor = "^3.5.2";
              pin = "3.6.0";
              runtime = true;
            };
            eslint-plugin-import = {
              descriptor = "^2.26.0";
              pin = "2.28.0";
              runtime = true;
            };
            eslint-plugin-jsx-a11y = {
              descriptor = "^6.5.1";
              pin = "6.7.1";
              runtime = true;
            };
            eslint-plugin-react = {
              descriptor = "^7.31.7";
              pin = "7.33.1";
              runtime = true;
            };
            eslint-plugin-react-hooks = {
              descriptor = "5.0.0-canary-7118f5dd7-20230705";
              pin = "5.0.0-canary-7118f5dd7-20230705";
              runtime = true;
            };
          };
          fetchInfo = {
            narHash = "sha256-Vs8HerjwSyAxtsAA4TMrvZ1T+t+iTbJElddcpnAwCNc=";
            type = "tarball";
            url = "https://registry.npmjs.org/eslint-config-next/-/eslint-config-next-13.4.12.tgz";
          };
          ident = "eslint-config-next";
          ltype = "file";
          peerInfo = {
            eslint = {
              descriptor = "^7.23.0 || ^8.0.0";
            };
            typescript = {
              descriptor = ">=3.3.1";
              optional = true;
            };
          };
          version = "13.4.12";
        };
      };
      eslint-import-resolver-node = {
        "0.3.9" = {
          depInfo = {
            debug = {
              descriptor = "^3.2.7";
              pin = "3.2.7";
              runtime = true;
            };
            is-core-module = {
              descriptor = "^2.13.0";
              pin = "2.13.0";
              runtime = true;
            };
            resolve = {
              descriptor = "^1.22.4";
              pin = "1.22.4";
              runtime = true;
            };
          };
          fetchInfo = {
            narHash = "sha256-ooMgMmq3zJ+rHArFE+eoC7w34g0YPO/RsEkPdGlSwiY=";
            type = "tarball";
            url = "https://registry.npmjs.org/eslint-import-resolver-node/-/eslint-import-resolver-node-0.3.9.tgz";
          };
          ident = "eslint-import-resolver-node";
          ltype = "file";
          version = "0.3.9";
        };
      };
      eslint-import-resolver-typescript = {
        "3.6.0" = {
          depInfo = {
            debug = {
              descriptor = "^4.3.4";
              pin = "4.3.4";
              runtime = true;
            };
            enhanced-resolve = {
              descriptor = "^5.12.0";
              pin = "5.15.0";
              runtime = true;
            };
            eslint-module-utils = {
              descriptor = "^2.7.4";
              pin = "2.8.0";
              runtime = true;
            };
            fast-glob = {
              descriptor = "^3.3.1";
              pin = "3.3.1";
              runtime = true;
            };
            get-tsconfig = {
              descriptor = "^4.5.0";
              pin = "4.7.0";
              runtime = true;
            };
            is-core-module = {
              descriptor = "^2.11.0";
              pin = "2.13.0";
              runtime = true;
            };
            is-glob = {
              descriptor = "^4.0.3";
              pin = "4.0.3";
              runtime = true;
            };
          };
          fetchInfo = {
            narHash = "sha256-VoQrsIgSUxSeBalUj+hM5k96VSTeadu5vOC92RYcjEw=";
            type = "tarball";
            url = "https://registry.npmjs.org/eslint-import-resolver-typescript/-/eslint-import-resolver-typescript-3.6.0.tgz";
          };
          ident = "eslint-import-resolver-typescript";
          ltype = "file";
          peerInfo = {
            eslint = {
              descriptor = "*";
            };
            eslint-plugin-import = {
              descriptor = "*";
            };
          };
          version = "3.6.0";
        };
      };
      eslint-module-utils = {
        "2.8.0" = {
          depInfo = {
            debug = {
              descriptor = "^3.2.7";
              pin = "3.2.7";
              runtime = true;
            };
          };
          fetchInfo = {
            narHash = "sha256-gALdH2ZFeHchXffpyUaS47byHnmq8/+RnuTuJjL6fVU=";
            type = "tarball";
            url = "https://registry.npmjs.org/eslint-module-utils/-/eslint-module-utils-2.8.0.tgz";
          };
          ident = "eslint-module-utils";
          ltype = "file";
          peerInfo = {
            eslint = {
              descriptor = "*";
              optional = true;
            };
          };
          version = "2.8.0";
        };
      };
      eslint-plugin-import = {
        "2.28.0" = {
          depInfo = {
            array-includes = {
              descriptor = "^3.1.6";
              pin = "3.1.6";
              runtime = true;
            };
            "array.prototype.findlastindex" = {
              descriptor = "^1.2.2";
              pin = "1.2.2";
              runtime = true;
            };
            "array.prototype.flat" = {
              descriptor = "^1.3.1";
              pin = "1.3.1";
              runtime = true;
            };
            "array.prototype.flatmap" = {
              descriptor = "^1.3.1";
              pin = "1.3.1";
              runtime = true;
            };
            debug = {
              descriptor = "^3.2.7";
              pin = "3.2.7";
              runtime = true;
            };
            doctrine = {
              descriptor = "^2.1.0";
              pin = "2.1.0";
              runtime = true;
            };
            eslint-import-resolver-node = {
              descriptor = "^0.3.7";
              pin = "0.3.9";
              runtime = true;
            };
            eslint-module-utils = {
              descriptor = "^2.8.0";
              pin = "2.8.0";
              runtime = true;
            };
            has = {
              descriptor = "^1.0.3";
              pin = "1.0.3";
              runtime = true;
            };
            is-core-module = {
              descriptor = "^2.12.1";
              pin = "2.13.0";
              runtime = true;
            };
            is-glob = {
              descriptor = "^4.0.3";
              pin = "4.0.3";
              runtime = true;
            };
            minimatch = {
              descriptor = "^3.1.2";
              pin = "3.1.2";
              runtime = true;
            };
            "object.fromentries" = {
              descriptor = "^2.0.6";
              pin = "2.0.6";
              runtime = true;
            };
            "object.groupby" = {
              descriptor = "^1.0.0";
              pin = "1.0.0";
              runtime = true;
            };
            "object.values" = {
              descriptor = "^1.1.6";
              pin = "1.1.6";
              runtime = true;
            };
            resolve = {
              descriptor = "^1.22.3";
              pin = "1.22.4";
              runtime = true;
            };
            semver = {
              descriptor = "^6.3.1";
              pin = "6.3.1";
              runtime = true;
            };
            tsconfig-paths = {
              descriptor = "^3.14.2";
              pin = "3.14.2";
              runtime = true;
            };
          };
          fetchInfo = {
            narHash = "sha256-uW0L5m3du+xXHHMeDBXtAThGngcSV6JhwZdlWAeNCMo=";
            type = "tarball";
            url = "https://registry.npmjs.org/eslint-plugin-import/-/eslint-plugin-import-2.28.0.tgz";
          };
          ident = "eslint-plugin-import";
          ltype = "file";
          peerInfo = {
            eslint = {
              descriptor = "^2 || ^3 || ^4 || ^5 || ^6 || ^7.2.0 || ^8";
            };
          };
          version = "2.28.0";
        };
      };
      eslint-plugin-jsx-a11y = {
        "6.7.1" = {
          depInfo = {
            "@babel/runtime" = {
              descriptor = "^7.20.7";
              pin = "7.22.10";
              runtime = true;
            };
            aria-query = {
              descriptor = "^5.1.3";
              pin = "5.3.0";
              runtime = true;
            };
            array-includes = {
              descriptor = "^3.1.6";
              pin = "3.1.6";
              runtime = true;
            };
            "array.prototype.flatmap" = {
              descriptor = "^1.3.1";
              pin = "1.3.1";
              runtime = true;
            };
            ast-types-flow = {
              descriptor = "^0.0.7";
              pin = "0.0.7";
              runtime = true;
            };
            axe-core = {
              descriptor = "^4.6.2";
              pin = "4.7.2";
              runtime = true;
            };
            axobject-query = {
              descriptor = "^3.1.1";
              pin = "3.2.1";
              runtime = true;
            };
            damerau-levenshtein = {
              descriptor = "^1.0.8";
              pin = "1.0.8";
              runtime = true;
            };
            emoji-regex = {
              descriptor = "^9.2.2";
              pin = "9.2.2";
              runtime = true;
            };
            has = {
              descriptor = "^1.0.3";
              pin = "1.0.3";
              runtime = true;
            };
            jsx-ast-utils = {
              descriptor = "^3.3.3";
              pin = "3.3.5";
              runtime = true;
            };
            language-tags = {
              descriptor = "=1.0.5";
              pin = "1.0.5";
              runtime = true;
            };
            minimatch = {
              descriptor = "^3.1.2";
              pin = "3.1.2";
              runtime = true;
            };
            "object.entries" = {
              descriptor = "^1.1.6";
              pin = "1.1.6";
              runtime = true;
            };
            "object.fromentries" = {
              descriptor = "^2.0.6";
              pin = "2.0.6";
              runtime = true;
            };
            semver = {
              descriptor = "^6.3.0";
              pin = "6.3.1";
              runtime = true;
            };
          };
          fetchInfo = {
            narHash = "sha256-Q9S6Zx3k3uHus3GXEUSfQM9oetRrNHIwUCMi6tU9hRA=";
            type = "tarball";
            url = "https://registry.npmjs.org/eslint-plugin-jsx-a11y/-/eslint-plugin-jsx-a11y-6.7.1.tgz";
          };
          ident = "eslint-plugin-jsx-a11y";
          ltype = "file";
          peerInfo = {
            eslint = {
              descriptor = "^3 || ^4 || ^5 || ^6 || ^7 || ^8";
            };
          };
          version = "6.7.1";
        };
      };
      eslint-plugin-react = {
        "7.33.1" = {
          depInfo = {
            array-includes = {
              descriptor = "^3.1.6";
              pin = "3.1.6";
              runtime = true;
            };
            "array.prototype.flatmap" = {
              descriptor = "^1.3.1";
              pin = "1.3.1";
              runtime = true;
            };
            "array.prototype.tosorted" = {
              descriptor = "^1.1.1";
              pin = "1.1.1";
              runtime = true;
            };
            doctrine = {
              descriptor = "^2.1.0";
              pin = "2.1.0";
              runtime = true;
            };
            estraverse = {
              descriptor = "^5.3.0";
              pin = "5.3.0";
              runtime = true;
            };
            jsx-ast-utils = {
              descriptor = "^2.4.1 || ^3.0.0";
              pin = "3.3.5";
              runtime = true;
            };
            minimatch = {
              descriptor = "^3.1.2";
              pin = "3.1.2";
              runtime = true;
            };
            "object.entries" = {
              descriptor = "^1.1.6";
              pin = "1.1.6";
              runtime = true;
            };
            "object.fromentries" = {
              descriptor = "^2.0.6";
              pin = "2.0.6";
              runtime = true;
            };
            "object.hasown" = {
              descriptor = "^1.1.2";
              pin = "1.1.2";
              runtime = true;
            };
            "object.values" = {
              descriptor = "^1.1.6";
              pin = "1.1.6";
              runtime = true;
            };
            prop-types = {
              descriptor = "^15.8.1";
              pin = "15.8.1";
              runtime = true;
            };
            resolve = {
              descriptor = "^2.0.0-next.4";
              pin = "2.0.0-next.4";
              runtime = true;
            };
            semver = {
              descriptor = "^6.3.1";
              pin = "6.3.1";
              runtime = true;
            };
            "string.prototype.matchall" = {
              descriptor = "^4.0.8";
              pin = "4.0.8";
              runtime = true;
            };
          };
          fetchInfo = {
            narHash = "sha256-ClYHYbYB/Rt+RQNHx+0cN0cvs3dlGdSD4qHrdYPb9d0=";
            type = "tarball";
            url = "https://registry.npmjs.org/eslint-plugin-react/-/eslint-plugin-react-7.33.1.tgz";
          };
          ident = "eslint-plugin-react";
          ltype = "file";
          peerInfo = {
            eslint = {
              descriptor = "^3 || ^4 || ^5 || ^6 || ^7 || ^8";
            };
          };
          version = "7.33.1";
        };
      };
      eslint-plugin-react-hooks = {
        "5.0.0-canary-7118f5dd7-20230705" = {
          fetchInfo = {
            narHash = "sha256-6/aerRZZEbM90478V3GP6xvunNur52J3eK85DXb65C4=";
            type = "tarball";
            url = "https://registry.npmjs.org/eslint-plugin-react-hooks/-/eslint-plugin-react-hooks-5.0.0-canary-7118f5dd7-20230705.tgz";
          };
          ident = "eslint-plugin-react-hooks";
          ltype = "file";
          peerInfo = {
            eslint = {
              descriptor = "^3.0.0 || ^4.0.0 || ^5.0.0 || ^6.0.0 || ^7.0.0 || ^8.0.0-0";
            };
          };
          treeInfo = { };
          version = "5.0.0-canary-7118f5dd7-20230705";
        };
      };
      eslint-plugin-tailwindcss = {
        "3.13.0" = {
          depInfo = {
            fast-glob = {
              descriptor = "^3.2.5";
              pin = "3.3.1";
              runtime = true;
            };
            postcss = {
              descriptor = "^8.4.4";
              pin = "8.4.27";
              runtime = true;
            };
          };
          fetchInfo = {
            narHash = "sha256-rWd+p9Sa4jcjEo886w2NAIy5AYjccC2pQXuGyPKtGw0=";
            type = "tarball";
            url = "https://registry.npmjs.org/eslint-plugin-tailwindcss/-/eslint-plugin-tailwindcss-3.13.0.tgz";
          };
          ident = "eslint-plugin-tailwindcss";
          ltype = "file";
          peerInfo = {
            tailwindcss = {
              descriptor = "^3.3.2";
            };
          };
          version = "3.13.0";
        };
      };
      eslint-scope = {
        "7.2.2" = {
          depInfo = {
            esrecurse = {
              descriptor = "^4.3.0";
              pin = "4.3.0";
              runtime = true;
            };
            estraverse = {
              descriptor = "^5.2.0";
              pin = "5.3.0";
              runtime = true;
            };
          };
          fetchInfo = {
            narHash = "sha256-t93ep+f1vmtCw+/t5EJxSBx0pgSNk7RcZppk5poBQWc=";
            type = "tarball";
            url = "https://registry.npmjs.org/eslint-scope/-/eslint-scope-7.2.2.tgz";
          };
          ident = "eslint-scope";
          ltype = "file";
          version = "7.2.2";
        };
      };
      eslint-visitor-keys = {
        "3.4.3" = {
          fetchInfo = {
            narHash = "sha256-kZy6Qi4xSU1uHD4vzFgn8MC4DaNQPLVqA6/O8VhmTzk=";
            type = "tarball";
            url = "https://registry.npmjs.org/eslint-visitor-keys/-/eslint-visitor-keys-3.4.3.tgz";
          };
          ident = "eslint-visitor-keys";
          ltype = "file";
          treeInfo = { };
          version = "3.4.3";
        };
      };
      espree = {
        "9.6.1" = {
          depInfo = {
            acorn = {
              descriptor = "^8.9.0";
              pin = "8.10.0";
              runtime = true;
            };
            acorn-jsx = {
              descriptor = "^5.3.2";
              pin = "5.3.2";
              runtime = true;
            };
            eslint-visitor-keys = {
              descriptor = "^3.4.1";
              pin = "3.4.3";
              runtime = true;
            };
          };
          fetchInfo = {
            narHash = "sha256-MmLjL+4VVeLurXw+/6Byf4S6KvOotFT34h1UKIr/hN0=";
            type = "tarball";
            url = "https://registry.npmjs.org/espree/-/espree-9.6.1.tgz";
          };
          ident = "espree";
          ltype = "file";
          version = "9.6.1";
        };
      };
      esprima = {
        "4.0.1" = {
          binInfo = {
            binPairs = {
              esparse = "bin/esparse.js";
              esvalidate = "bin/esvalidate.js";
            };
          };
          fetchInfo = {
            narHash = "sha256-1+SuAJDLWU9BTTp5ceLHWDAlVfETkd5VW35T9kxNNg0=";
            type = "tarball";
            url = "https://registry.npmjs.org/esprima/-/esprima-4.0.1.tgz";
          };
          ident = "esprima";
          ltype = "file";
          treeInfo = { };
          version = "4.0.1";
        };
      };
      esquery = {
        "1.5.0" = {
          depInfo = {
            estraverse = {
              descriptor = "^5.1.0";
              pin = "5.3.0";
              runtime = true;
            };
          };
          fetchInfo = {
            narHash = "sha256-XY6uS/pUiPUL7jX+6aJKsTvIrnexv2DBGC66WzzjZ5w=";
            type = "tarball";
            url = "https://registry.npmjs.org/esquery/-/esquery-1.5.0.tgz";
          };
          ident = "esquery";
          ltype = "file";
          version = "1.5.0";
        };
      };
      esrecurse = {
        "4.3.0" = {
          depInfo = {
            estraverse = {
              descriptor = "^5.2.0";
              pin = "5.3.0";
              runtime = true;
            };
          };
          fetchInfo = {
            narHash = "sha256-L2yCPwe2ilGsbvyZlJ+BZPHW5GTO7tz1uJwtojcSr9Y=";
            type = "tarball";
            url = "https://registry.npmjs.org/esrecurse/-/esrecurse-4.3.0.tgz";
          };
          ident = "esrecurse";
          ltype = "file";
          version = "4.3.0";
        };
      };
      estraverse = {
        "5.3.0" = {
          fetchInfo = {
            narHash = "sha256-Vb6OEwicNHaYjRSLyES24y4OJtyPPb/7ecZpH6ZOGFg=";
            type = "tarball";
            url = "https://registry.npmjs.org/estraverse/-/estraverse-5.3.0.tgz";
          };
          ident = "estraverse";
          ltype = "file";
          treeInfo = { };
          version = "5.3.0";
        };
      };
      estree-walker = {
        "1.0.1" = {
          fetchInfo = {
            narHash = "sha256-8Wtdf/l4wmml2HcFW61LU/zkDjVPnvpR8U8OgSJTZwg=";
            type = "tarball";
            url = "https://registry.npmjs.org/estree-walker/-/estree-walker-1.0.1.tgz";
          };
          ident = "estree-walker";
          ltype = "file";
          treeInfo = { };
          version = "1.0.1";
        };
        "2.0.2" = {
          fetchInfo = {
            narHash = "sha256-VWAjCLb125r8rYf6XVjVDWibZtnEDisgYEkcU7uZMlc=";
            type = "tarball";
            url = "https://registry.npmjs.org/estree-walker/-/estree-walker-2.0.2.tgz";
          };
          ident = "estree-walker";
          ltype = "file";
          treeInfo = { };
          version = "2.0.2";
        };
      };
      esutils = {
        "2.0.3" = {
          fetchInfo = {
            narHash = "sha256-5ELIsVusYd9/R/gTN89JTtg9quxfu170hXVKuwceIdg=";
            type = "tarball";
            url = "https://registry.npmjs.org/esutils/-/esutils-2.0.3.tgz";
          };
          ident = "esutils";
          ltype = "file";
          treeInfo = { };
          version = "2.0.3";
        };
      };
      event-target-shim = {
        "5.0.1" = {
          fetchInfo = {
            narHash = "sha256-2AJGuQbw+qwoe5mZd1JvbkE/oksRSHLS5K6rYdwvt0A=";
            type = "tarball";
            url = "https://registry.npmjs.org/event-target-shim/-/event-target-shim-5.0.1.tgz";
          };
          ident = "event-target-shim";
          ltype = "file";
          treeInfo = { };
          version = "5.0.1";
        };
      };
      eventemitter3 = {
        "4.0.7" = {
          fetchInfo = {
            narHash = "sha256-q8SENFH3M30q8hIpoQjEGGg1uMzj/O6phLhdaucBrKA=";
            type = "tarball";
            url = "https://registry.npmjs.org/eventemitter3/-/eventemitter3-4.0.7.tgz";
          };
          ident = "eventemitter3";
          ltype = "file";
          treeInfo = { };
          version = "4.0.7";
        };
      };
      execa = {
        "5.1.1" = {
          depInfo = {
            cross-spawn = {
              descriptor = "^7.0.3";
              pin = "7.0.3";
              runtime = true;
            };
            get-stream = {
              descriptor = "^6.0.0";
              pin = "6.0.1";
              runtime = true;
            };
            human-signals = {
              descriptor = "^2.1.0";
              pin = "2.1.0";
              runtime = true;
            };
            is-stream = {
              descriptor = "^2.0.0";
              pin = "2.0.1";
              runtime = true;
            };
            merge-stream = {
              descriptor = "^2.0.0";
              pin = "2.0.0";
              runtime = true;
            };
            npm-run-path = {
              descriptor = "^4.0.1";
              pin = "4.0.1";
              runtime = true;
            };
            onetime = {
              descriptor = "^5.1.2";
              pin = "5.1.2";
              runtime = true;
            };
            signal-exit = {
              descriptor = "^3.0.3";
              pin = "3.0.7";
              runtime = true;
            };
            strip-final-newline = {
              descriptor = "^2.0.0";
              pin = "2.0.0";
              runtime = true;
            };
          };
          fetchInfo = {
            narHash = "sha256-P5IyUg7KIfSrao+yxAluQcJpF6R2YDzPqoOnmcLbVtQ=";
            type = "tarball";
            url = "https://registry.npmjs.org/execa/-/execa-5.1.1.tgz";
          };
          ident = "execa";
          ltype = "file";
          version = "5.1.1";
        };
      };
      fast-deep-equal = {
        "3.1.3" = {
          fetchInfo = {
            narHash = "sha256-KpUhRWsLDBdqgjClgxbRoAtbWsUvY7JhVil6+dMUqwE=";
            type = "tarball";
            url = "https://registry.npmjs.org/fast-deep-equal/-/fast-deep-equal-3.1.3.tgz";
          };
          ident = "fast-deep-equal";
          ltype = "file";
          treeInfo = { };
          version = "3.1.3";
        };
      };
      fast-equals = {
        "5.0.1" = {
          fetchInfo = {
            narHash = "sha256-GB8ciw0PXHlpTfNtY63zTEm0F/SvE7K13jsYl7jUWjQ=";
            type = "tarball";
            url = "https://registry.npmjs.org/fast-equals/-/fast-equals-5.0.1.tgz";
          };
          ident = "fast-equals";
          ltype = "file";
          treeInfo = { };
          version = "5.0.1";
        };
      };
      fast-glob = {
        "3.2.12" = {
          depInfo = {
            "@nodelib/fs.stat" = {
              descriptor = "^2.0.2";
              pin = "2.0.5";
              runtime = true;
            };
            "@nodelib/fs.walk" = {
              descriptor = "^1.2.3";
              pin = "1.2.8";
              runtime = true;
            };
            glob-parent = {
              descriptor = "^5.1.2";
              pin = "5.1.2";
              runtime = true;
            };
            merge2 = {
              descriptor = "^1.3.0";
              pin = "1.4.1";
              runtime = true;
            };
            micromatch = {
              descriptor = "^4.0.4";
              pin = "4.0.5";
              runtime = true;
            };
          };
          fetchInfo = {
            narHash = "sha256-YnT17ehrbvhwqYLX+9p1qX6JPxDvNK81DX3DCzn/XPA=";
            type = "tarball";
            url = "https://registry.npmjs.org/fast-glob/-/fast-glob-3.2.12.tgz";
          };
          ident = "fast-glob";
          ltype = "file";
          version = "3.2.12";
        };
        "3.3.1" = {
          depInfo = {
            "@nodelib/fs.stat" = {
              descriptor = "^2.0.2";
              pin = "2.0.5";
              runtime = true;
            };
            "@nodelib/fs.walk" = {
              descriptor = "^1.2.3";
              pin = "1.2.8";
              runtime = true;
            };
            glob-parent = {
              descriptor = "^5.1.2";
              pin = "5.1.2";
              runtime = true;
            };
            merge2 = {
              descriptor = "^1.3.0";
              pin = "1.4.1";
              runtime = true;
            };
            micromatch = {
              descriptor = "^4.0.4";
              pin = "4.0.5";
              runtime = true;
            };
          };
          fetchInfo = {
            narHash = "sha256-5nqC11gSSkfExDdLdMBzSaydhIbFVw3jjzTT9OWZ/bg=";
            type = "tarball";
            url = "https://registry.npmjs.org/fast-glob/-/fast-glob-3.3.1.tgz";
          };
          ident = "fast-glob";
          ltype = "file";
          version = "3.3.1";
        };
      };
      fast-json-stable-stringify = {
        "2.1.0" = {
          fetchInfo = {
            narHash = "sha256-nvrcRKamdCbRlzJK0Bh6NkK5zpCoFhkizKEov4yK2oI=";
            type = "tarball";
            url = "https://registry.npmjs.org/fast-json-stable-stringify/-/fast-json-stable-stringify-2.1.0.tgz";
          };
          ident = "fast-json-stable-stringify";
          ltype = "file";
          treeInfo = { };
          version = "2.1.0";
        };
      };
      fast-levenshtein = {
        "2.0.6" = {
          fetchInfo = {
            narHash = "sha256-ecbIyMHylbbr7yuhLAsB/amPAPjjzF0rZw6qZDni7b8=";
            type = "tarball";
            url = "https://registry.npmjs.org/fast-levenshtein/-/fast-levenshtein-2.0.6.tgz";
          };
          ident = "fast-levenshtein";
          ltype = "file";
          treeInfo = { };
          version = "2.0.6";
        };
      };
      fast-memoize = {
        "2.5.2" = {
          fetchInfo = {
            narHash = "sha256-VCuN++59C22UmtD3ZIw2XaHP/Pwnvx9AAtjremfnAr4=";
            type = "tarball";
            url = "https://registry.npmjs.org/fast-memoize/-/fast-memoize-2.5.2.tgz";
          };
          ident = "fast-memoize";
          ltype = "file";
          treeInfo = { };
          version = "2.5.2";
        };
      };
      fast-safe-stringify = {
        "2.1.1" = {
          fetchInfo = {
            narHash = "sha256-8JSjejXM3vYZcePsFSgp3nsuz1MS9pJyLf0hqJPSpcY=";
            type = "tarball";
            url = "https://registry.npmjs.org/fast-safe-stringify/-/fast-safe-stringify-2.1.1.tgz";
          };
          ident = "fast-safe-stringify";
          ltype = "file";
          treeInfo = { };
          version = "2.1.1";
        };
      };
      fastq = {
        "1.15.0" = {
          depInfo = {
            reusify = {
              descriptor = "^1.0.4";
              pin = "1.0.4";
              runtime = true;
            };
          };
          fetchInfo = {
            narHash = "sha256-ZQL8MrtnhshvuGKqN0POOAVUOHfnLxeRre7FIRwF/mU=";
            type = "tarball";
            url = "https://registry.npmjs.org/fastq/-/fastq-1.15.0.tgz";
          };
          ident = "fastq";
          ltype = "file";
          version = "1.15.0";
        };
      };
      file-entry-cache = {
        "6.0.1" = {
          depInfo = {
            flat-cache = {
              descriptor = "^3.0.4";
              pin = "3.0.4";
              runtime = true;
            };
          };
          fetchInfo = {
            narHash = "sha256-MwVItPdMFD5YC4DfaF68o699xdGokviC2VW6Z0rw1Hs=";
            type = "tarball";
            url = "https://registry.npmjs.org/file-entry-cache/-/file-entry-cache-6.0.1.tgz";
          };
          ident = "file-entry-cache";
          ltype = "file";
          version = "6.0.1";
        };
      };
      fill-range = {
        "7.0.1" = {
          depInfo = {
            to-regex-range = {
              descriptor = "^5.0.1";
              pin = "5.0.1";
              runtime = true;
            };
          };
          fetchInfo = {
            narHash = "sha256-1Cy9dyWlI0TnadlFR9TSryNYjR27SRRWtTT6oDiUHps=";
            type = "tarball";
            url = "https://registry.npmjs.org/fill-range/-/fill-range-7.0.1.tgz";
          };
          ident = "fill-range";
          ltype = "file";
          version = "7.0.1";
        };
      };
      find-root = {
        "1.1.0" = {
          fetchInfo = {
            narHash = "sha256-grIQ6Ml6cBttYVMYj34V1G9PrquEAh5ygziquXEkSTE=";
            type = "tarball";
            url = "https://registry.npmjs.org/find-root/-/find-root-1.1.0.tgz";
          };
          ident = "find-root";
          ltype = "file";
          treeInfo = { };
          version = "1.1.0";
        };
      };
      find-up = {
        "3.0.0" = {
          depInfo = {
            locate-path = {
              descriptor = "^3.0.0";
              pin = "3.0.0";
              runtime = true;
            };
          };
          fetchInfo = {
            narHash = "sha256-MqJDglB+Fm0w0FN0ebtHpOon3vAFJt+5tm1Vq0FkReY=";
            type = "tarball";
            url = "https://registry.npmjs.org/find-up/-/find-up-3.0.0.tgz";
          };
          ident = "find-up";
          ltype = "file";
          version = "3.0.0";
        };
        "5.0.0" = {
          depInfo = {
            locate-path = {
              descriptor = "^6.0.0";
              pin = "6.0.0";
              runtime = true;
            };
            path-exists = {
              descriptor = "^4.0.0";
              pin = "4.0.0";
              runtime = true;
            };
          };
          fetchInfo = {
            narHash = "sha256-WZuEghlt11JSbLWajuil1Gnm7yIUKnq2vCUvT7Xydrg=";
            type = "tarball";
            url = "https://registry.npmjs.org/find-up/-/find-up-5.0.0.tgz";
          };
          ident = "find-up";
          ltype = "file";
          version = "5.0.0";
        };
      };
      flat-cache = {
        "3.0.4" = {
          depInfo = {
            flatted = {
              descriptor = "^3.1.0";
              pin = "3.2.7";
              runtime = true;
            };
            rimraf = {
              descriptor = "^3.0.2";
              pin = "3.0.2";
              runtime = true;
            };
          };
          fetchInfo = {
            narHash = "sha256-AQ5bUXhq/Y5gpPJWh2PcKocLZ4KPYGtJ0iLVrr6Rxn8=";
            type = "tarball";
            url = "https://registry.npmjs.org/flat-cache/-/flat-cache-3.0.4.tgz";
          };
          ident = "flat-cache";
          ltype = "file";
          version = "3.0.4";
        };
      };
      flatted = {
        "3.2.7" = {
          fetchInfo = {
            narHash = "sha256-1wHd6K1UO8pxAb5P31QO68je15eMyrcYloG1VHylH8U=";
            type = "tarball";
            url = "https://registry.npmjs.org/flatted/-/flatted-3.2.7.tgz";
          };
          ident = "flatted";
          ltype = "file";
          treeInfo = { };
          version = "3.2.7";
        };
      };
      follow-redirects = {
        "1.15.2" = {
          fetchInfo = {
            narHash = "sha256-MK6jEPJVqrI028JDGPYWVcf11eBgflgylSJU+Z1RAF8=";
            type = "tarball";
            url = "https://registry.npmjs.org/follow-redirects/-/follow-redirects-1.15.2.tgz";
          };
          ident = "follow-redirects";
          ltype = "file";
          peerInfo = {
            debug = {
              descriptor = "*";
              optional = true;
            };
          };
          treeInfo = { };
          version = "1.15.2";
        };
      };
      for-each = {
        "0.3.3" = {
          depInfo = {
            is-callable = {
              descriptor = "^1.1.3";
              pin = "1.2.7";
              runtime = true;
            };
          };
          fetchInfo = {
            narHash = "sha256-k807WSABZLSTmLKtziFXu5hqnm9YlWMP9X8K8kOdgpc=";
            type = "tarball";
            url = "https://registry.npmjs.org/for-each/-/for-each-0.3.3.tgz";
          };
          ident = "for-each";
          ltype = "file";
          version = "0.3.3";
        };
      };
      form-data = {
        "4.0.0" = {
          depInfo = {
            asynckit = {
              descriptor = "^0.4.0";
              pin = "0.4.0";
              runtime = true;
            };
            combined-stream = {
              descriptor = "^1.0.8";
              pin = "1.0.8";
              runtime = true;
            };
            mime-types = {
              descriptor = "^2.1.12";
              pin = "2.1.35";
              runtime = true;
            };
          };
          fetchInfo = {
            narHash = "sha256-ASh2B2n7uaQZkO0SWR3lnu3IeZ6e1KIevUBTfO0ixLU=";
            type = "tarball";
            url = "https://registry.npmjs.org/form-data/-/form-data-4.0.0.tgz";
          };
          ident = "form-data";
          ltype = "file";
          version = "4.0.0";
        };
      };
      format-util = {
        "1.0.5" = {
          fetchInfo = {
            narHash = "sha256-x0EN0Gk1ee5oV4HaSC5//VYNwTlxNMyk/tN4cGnjexQ=";
            type = "tarball";
            url = "https://registry.npmjs.org/format-util/-/format-util-1.0.5.tgz";
          };
          ident = "format-util";
          ltype = "file";
          treeInfo = { };
          version = "1.0.5";
        };
      };
      "fraction.js" = {
        "4.2.0" = {
          fetchInfo = {
            narHash = "sha256-KCon2hX/Al54872dmiipwOLnOyrlqtWt6IMF6hrTHeM=";
            type = "tarball";
            url = "https://registry.npmjs.org/fraction.js/-/fraction.js-4.2.0.tgz";
          };
          ident = "fraction.js";
          ltype = "file";
          treeInfo = { };
          version = "4.2.0";
        };
      };
      fs-extra = {
        "10.1.0" = {
          depInfo = {
            graceful-fs = {
              descriptor = "^4.2.0";
              pin = "4.2.11";
              runtime = true;
            };
            jsonfile = {
              descriptor = "^6.0.1";
              pin = "6.1.0";
              runtime = true;
            };
            universalify = {
              descriptor = "^2.0.0";
              pin = "2.0.0";
              runtime = true;
            };
          };
          fetchInfo = {
            narHash = "sha256-PQ+uNPCEvMKJHftEGLouC++L6nvRvIehWDLixzDVkgE=";
            type = "tarball";
            url = "https://registry.npmjs.org/fs-extra/-/fs-extra-10.1.0.tgz";
          };
          ident = "fs-extra";
          ltype = "file";
          version = "10.1.0";
        };
      };
      "fs.realpath" = {
        "1.0.0" = {
          fetchInfo = {
            narHash = "sha256-oPk2F5VP+ECdKr8qs3h0dziW0mK71uwTUrbgulLI/ks=";
            type = "tarball";
            url = "https://registry.npmjs.org/fs.realpath/-/fs.realpath-1.0.0.tgz";
          };
          ident = "fs.realpath";
          ltype = "file";
          treeInfo = { };
          version = "1.0.0";
        };
      };
      fsevents = {
        "2.3.2" = {
          fetchInfo = {
            narHash = "sha256-E3+DvwgglDWVPPUVoggGWI8OFZR0YJ5zk7nYB4+UwLI=";
            type = "tarball";
            url = "https://registry.npmjs.org/fsevents/-/fsevents-2.3.2.tgz";
          };
          ident = "fsevents";
          lifecycle = {
            install = true;
          };
          ltype = "file";
          sysInfo = {
            os = [
              "darwin"
            ];
          };
          treeInfo = { };
          version = "2.3.2";
        };
      };
      function-bind = {
        "1.1.1" = {
          fetchInfo = {
            narHash = "sha256-9SZTeDBJ87ogdiEHyC3b2/wr1Bv8qb8rCJeD+OYvf9A=";
            type = "tarball";
            url = "https://registry.npmjs.org/function-bind/-/function-bind-1.1.1.tgz";
          };
          ident = "function-bind";
          ltype = "file";
          treeInfo = { };
          version = "1.1.1";
        };
      };
      "function.prototype.name" = {
        "1.1.5" = {
          depInfo = {
            call-bind = {
              descriptor = "^1.0.2";
              pin = "1.0.2";
              runtime = true;
            };
            define-properties = {
              descriptor = "^1.1.3";
              pin = "1.2.0";
              runtime = true;
            };
            es-abstract = {
              descriptor = "^1.19.0";
              pin = "1.22.1";
              runtime = true;
            };
            functions-have-names = {
              descriptor = "^1.2.2";
              pin = "1.2.3";
              runtime = true;
            };
          };
          fetchInfo = {
            narHash = "sha256-FWK+IcHcca7NT3qw34biqkqnh3QwhmNLB14cdLU2VE4=";
            type = "tarball";
            url = "https://registry.npmjs.org/function.prototype.name/-/function.prototype.name-1.1.5.tgz";
          };
          ident = "function.prototype.name";
          ltype = "file";
          version = "1.1.5";
        };
      };
      functions-have-names = {
        "1.2.3" = {
          fetchInfo = {
            narHash = "sha256-dVfHQ/TWDvhFrCqSX2JEBlW2wJ3THV0pbZ0zt7I0Olk=";
            type = "tarball";
            url = "https://registry.npmjs.org/functions-have-names/-/functions-have-names-1.2.3.tgz";
          };
          ident = "functions-have-names";
          ltype = "file";
          treeInfo = { };
          version = "1.2.3";
        };
      };
      get-caller-file = {
        "2.0.5" = {
          fetchInfo = {
            narHash = "sha256-6s6ASytSaJ0gB+1O75bM58qa3ql1fpWpA8ayznW3F+I=";
            type = "tarball";
            url = "https://registry.npmjs.org/get-caller-file/-/get-caller-file-2.0.5.tgz";
          };
          ident = "get-caller-file";
          ltype = "file";
          treeInfo = { };
          version = "2.0.5";
        };
      };
      get-intrinsic = {
        "1.2.1" = {
          depInfo = {
            function-bind = {
              descriptor = "^1.1.1";
              pin = "1.1.1";
              runtime = true;
            };
            has = {
              descriptor = "^1.0.3";
              pin = "1.0.3";
              runtime = true;
            };
            has-proto = {
              descriptor = "^1.0.1";
              pin = "1.0.1";
              runtime = true;
            };
            has-symbols = {
              descriptor = "^1.0.3";
              pin = "1.0.3";
              runtime = true;
            };
          };
          fetchInfo = {
            narHash = "sha256-9no1EKud/J4wr6WSN//rpyQqByB0HGgY/jmykJNpyvU=";
            type = "tarball";
            url = "https://registry.npmjs.org/get-intrinsic/-/get-intrinsic-1.2.1.tgz";
          };
          ident = "get-intrinsic";
          ltype = "file";
          version = "1.2.1";
        };
      };
      get-source = {
        "2.0.12" = {
          depInfo = {
            data-uri-to-buffer = {
              descriptor = "^2.0.0";
              pin = "2.0.2";
              runtime = true;
            };
            source-map = {
              descriptor = "^0.6.1";
              pin = "0.6.1";
              runtime = true;
            };
          };
          fetchInfo = {
            narHash = "sha256-6ZXEcclhuHzTS1j/7Kp4ltHRvxuo9TCGCNTIWMZoVCw=";
            type = "tarball";
            url = "https://registry.npmjs.org/get-source/-/get-source-2.0.12.tgz";
          };
          ident = "get-source";
          ltype = "file";
          version = "2.0.12";
        };
      };
      get-stream = {
        "6.0.1" = {
          fetchInfo = {
            narHash = "sha256-NkzeCHoKd73Q37o0O2OT8yyusJPNB3pWuTNPjTHRZN8=";
            type = "tarball";
            url = "https://registry.npmjs.org/get-stream/-/get-stream-6.0.1.tgz";
          };
          ident = "get-stream";
          ltype = "file";
          treeInfo = { };
          version = "6.0.1";
        };
      };
      get-symbol-description = {
        "1.0.0" = {
          depInfo = {
            call-bind = {
              descriptor = "^1.0.2";
              pin = "1.0.2";
              runtime = true;
            };
            get-intrinsic = {
              descriptor = "^1.1.1";
              pin = "1.2.1";
              runtime = true;
            };
          };
          fetchInfo = {
            narHash = "sha256-bp4YseOAXEN7IU9lE2OGbqZeZUYyPwtPftsSD3ZyTsk=";
            type = "tarball";
            url = "https://registry.npmjs.org/get-symbol-description/-/get-symbol-description-1.0.0.tgz";
          };
          ident = "get-symbol-description";
          ltype = "file";
          version = "1.0.0";
        };
      };
      get-tsconfig = {
        "4.7.0" = {
          depInfo = {
            resolve-pkg-maps = {
              descriptor = "^1.0.0";
              pin = "1.0.0";
              runtime = true;
            };
          };
          fetchInfo = {
            narHash = "sha256-2WlmRXvAkWRHd1e2ml4brCNzVvzxIOtIDuT77w2sUPw=";
            type = "tarball";
            url = "https://registry.npmjs.org/get-tsconfig/-/get-tsconfig-4.7.0.tgz";
          };
          ident = "get-tsconfig";
          ltype = "file";
          version = "4.7.0";
        };
      };
      glob = {
        "7.1.6" = {
          depInfo = {
            "fs.realpath" = {
              descriptor = "^1.0.0";
              pin = "1.0.0";
              runtime = true;
            };
            inflight = {
              descriptor = "^1.0.4";
              pin = "1.0.6";
              runtime = true;
            };
            inherits = {
              descriptor = "2";
              pin = "2.0.4";
              runtime = true;
            };
            minimatch = {
              descriptor = "^3.0.4";
              pin = "3.1.2";
              runtime = true;
            };
            once = {
              descriptor = "^1.3.0";
              pin = "1.4.0";
              runtime = true;
            };
            path-is-absolute = {
              descriptor = "^1.0.0";
              pin = "1.0.1";
              runtime = true;
            };
          };
          fetchInfo = {
            narHash = "sha256-vAvUXyD9nc0s+gEZROHFFKajC2bfPelw5A8qx0+vWeo=";
            type = "tarball";
            url = "https://registry.npmjs.org/glob/-/glob-7.1.6.tgz";
          };
          ident = "glob";
          ltype = "file";
          version = "7.1.6";
        };
        "7.1.7" = {
          depInfo = {
            "fs.realpath" = {
              descriptor = "^1.0.0";
              pin = "1.0.0";
              runtime = true;
            };
            inflight = {
              descriptor = "^1.0.4";
              pin = "1.0.6";
              runtime = true;
            };
            inherits = {
              descriptor = "2";
              pin = "2.0.4";
              runtime = true;
            };
            minimatch = {
              descriptor = "^3.0.4";
              pin = "3.1.2";
              runtime = true;
            };
            once = {
              descriptor = "^1.3.0";
              pin = "1.4.0";
              runtime = true;
            };
            path-is-absolute = {
              descriptor = "^1.0.0";
              pin = "1.0.1";
              runtime = true;
            };
          };
          fetchInfo = {
            narHash = "sha256-7ZgNyQIpMqqC4/B3Hyt21dl5d0mnSAu/rtglBTS6Y4E=";
            type = "tarball";
            url = "https://registry.npmjs.org/glob/-/glob-7.1.7.tgz";
          };
          ident = "glob";
          ltype = "file";
          version = "7.1.7";
        };
      };
      glob-parent = {
        "5.1.2" = {
          depInfo = {
            is-glob = {
              descriptor = "^4.0.1";
              pin = "4.0.3";
              runtime = true;
            };
          };
          fetchInfo = {
            narHash = "sha256-mBzP81bqsUi8ynclBz+RKWEXbDPwkIyeOayR4oTzrsI=";
            type = "tarball";
            url = "https://registry.npmjs.org/glob-parent/-/glob-parent-5.1.2.tgz";
          };
          ident = "glob-parent";
          ltype = "file";
          version = "5.1.2";
        };
        "6.0.2" = {
          depInfo = {
            is-glob = {
              descriptor = "^4.0.3";
              pin = "4.0.3";
              runtime = true;
            };
          };
          fetchInfo = {
            narHash = "sha256-vvuqFaFPDyQ16dP8E52w8+seROdq79wwdXAV/g2BLPo=";
            type = "tarball";
            url = "https://registry.npmjs.org/glob-parent/-/glob-parent-6.0.2.tgz";
          };
          ident = "glob-parent";
          ltype = "file";
          version = "6.0.2";
        };
      };
      glob-to-regexp = {
        "0.4.1" = {
          fetchInfo = {
            narHash = "sha256-PPP4pb8uF1bYQXXMlu0YHg/8v61VEvxwqlv8HFvF1vQ=";
            type = "tarball";
            url = "https://registry.npmjs.org/glob-to-regexp/-/glob-to-regexp-0.4.1.tgz";
          };
          ident = "glob-to-regexp";
          ltype = "file";
          treeInfo = { };
          version = "0.4.1";
        };
      };
      globals = {
        "13.21.0" = {
          depInfo = {
            type-fest = {
              descriptor = "^0.20.2";
              pin = "0.20.2";
              runtime = true;
            };
          };
          fetchInfo = {
            narHash = "sha256-cFRMHOs3yihQpb802YB5OTH98+QLLN7wZ1HzhNqPVUg=";
            type = "tarball";
            url = "https://registry.npmjs.org/globals/-/globals-13.21.0.tgz";
          };
          ident = "globals";
          ltype = "file";
          version = "13.21.0";
        };
      };
      globalthis = {
        "1.0.3" = {
          depInfo = {
            define-properties = {
              descriptor = "^1.1.3";
              pin = "1.2.0";
              runtime = true;
            };
          };
          fetchInfo = {
            narHash = "sha256-1IG9q5XPzjamsW5fTagVpUVQtVhpqqKn2SrQFtEtCF0=";
            type = "tarball";
            url = "https://registry.npmjs.org/globalthis/-/globalthis-1.0.3.tgz";
          };
          ident = "globalthis";
          ltype = "file";
          version = "1.0.3";
        };
      };
      globby = {
        "11.1.0" = {
          depInfo = {
            array-union = {
              descriptor = "^2.1.0";
              pin = "2.1.0";
              runtime = true;
            };
            dir-glob = {
              descriptor = "^3.0.1";
              pin = "3.0.1";
              runtime = true;
            };
            fast-glob = {
              descriptor = "^3.2.9";
              pin = "3.3.1";
              runtime = true;
            };
            ignore = {
              descriptor = "^5.2.0";
              pin = "5.2.4";
              runtime = true;
            };
            merge2 = {
              descriptor = "^1.4.1";
              pin = "1.4.1";
              runtime = true;
            };
            slash = {
              descriptor = "^3.0.0";
              pin = "3.0.0";
              runtime = true;
            };
          };
          fetchInfo = {
            narHash = "sha256-pDQt3eQJagRiZZ3o4V+Jnlbnwb4u03qB4/v0axxMp/A=";
            type = "tarball";
            url = "https://registry.npmjs.org/globby/-/globby-11.1.0.tgz";
          };
          ident = "globby";
          ltype = "file";
          version = "11.1.0";
        };
      };
      goober = {
        "2.1.13" = {
          fetchInfo = {
            narHash = "sha256-Ta5XFdBjCxiVFBIHCTjgJD2x/8SWo6pr1UwDDvX5ljI=";
            type = "tarball";
            url = "https://registry.npmjs.org/goober/-/goober-2.1.13.tgz";
          };
          ident = "goober";
          ltype = "file";
          peerInfo = {
            csstype = {
              descriptor = "^3.0.10";
            };
          };
          treeInfo = { };
          version = "2.1.13";
        };
      };
      gopd = {
        "1.0.1" = {
          depInfo = {
            get-intrinsic = {
              descriptor = "^1.1.3";
              pin = "1.2.1";
              runtime = true;
            };
          };
          fetchInfo = {
            narHash = "sha256-wknwzCUDVb/wjP+hhlq6AA5gqrQzPfozD37C6FNPj44=";
            type = "tarball";
            url = "https://registry.npmjs.org/gopd/-/gopd-1.0.1.tgz";
          };
          ident = "gopd";
          ltype = "file";
          version = "1.0.1";
        };
      };
      graceful-fs = {
        "4.2.11" = {
          fetchInfo = {
            narHash = "sha256-fH5Hc6M2zHaGeId+SmUwYBdGE4mmjA/Sg/Jj5Jh+P8g=";
            type = "tarball";
            url = "https://registry.npmjs.org/graceful-fs/-/graceful-fs-4.2.11.tgz";
          };
          ident = "graceful-fs";
          ltype = "file";
          treeInfo = { };
          version = "4.2.11";
        };
      };
      graphemer = {
        "1.4.0" = {
          fetchInfo = {
            narHash = "sha256-DZyl/8fBRXZUVwvxbPufo9mhgQw5epZJaC2RI+BjdgA=";
            type = "tarball";
            url = "https://registry.npmjs.org/graphemer/-/graphemer-1.4.0.tgz";
          };
          ident = "graphemer";
          ltype = "file";
          treeInfo = { };
          version = "1.4.0";
        };
      };
      has = {
        "1.0.3" = {
          depInfo = {
            function-bind = {
              descriptor = "^1.1.1";
              pin = "1.1.1";
              runtime = true;
            };
          };
          fetchInfo = {
            narHash = "sha256-z8QWvFmgxmKtQJ34TpRAZljXFJmXY0WUMPj1K64SHx4=";
            type = "tarball";
            url = "https://registry.npmjs.org/has/-/has-1.0.3.tgz";
          };
          ident = "has";
          ltype = "file";
          version = "1.0.3";
        };
      };
      has-bigints = {
        "1.0.2" = {
          fetchInfo = {
            narHash = "sha256-LbPq15+J8usV8bCOrccIRtzh4ZyiUjLqzaflRX9w4bo=";
            type = "tarball";
            url = "https://registry.npmjs.org/has-bigints/-/has-bigints-1.0.2.tgz";
          };
          ident = "has-bigints";
          ltype = "file";
          treeInfo = { };
          version = "1.0.2";
        };
      };
      has-flag = {
        "3.0.0" = {
          fetchInfo = {
            narHash = "sha256-6FPI3mvzeaWOqNs71lre0tBCY/xdSo+7lBMqw1c9lM4=";
            type = "tarball";
            url = "https://registry.npmjs.org/has-flag/-/has-flag-3.0.0.tgz";
          };
          ident = "has-flag";
          ltype = "file";
          treeInfo = { };
          version = "3.0.0";
        };
        "4.0.0" = {
          fetchInfo = {
            narHash = "sha256-vPSUFfMlEN5g/4ID+ZlkxJd2xcrLd2zb1zB0uEfVeKE=";
            type = "tarball";
            url = "https://registry.npmjs.org/has-flag/-/has-flag-4.0.0.tgz";
          };
          ident = "has-flag";
          ltype = "file";
          treeInfo = { };
          version = "4.0.0";
        };
      };
      has-property-descriptors = {
        "1.0.0" = {
          depInfo = {
            get-intrinsic = {
              descriptor = "^1.1.1";
              pin = "1.2.1";
              runtime = true;
            };
          };
          fetchInfo = {
            narHash = "sha256-4ifPgOoeFgucRb9lxIJmJo2IZdx4Agfb6/y7EBR2f0U=";
            type = "tarball";
            url = "https://registry.npmjs.org/has-property-descriptors/-/has-property-descriptors-1.0.0.tgz";
          };
          ident = "has-property-descriptors";
          ltype = "file";
          version = "1.0.0";
        };
      };
      has-proto = {
        "1.0.1" = {
          fetchInfo = {
            narHash = "sha256-ISNmtDgUP0rItqrzD4aR/XFTe2Pnr6iUaMaJ0iajpe0=";
            type = "tarball";
            url = "https://registry.npmjs.org/has-proto/-/has-proto-1.0.1.tgz";
          };
          ident = "has-proto";
          ltype = "file";
          treeInfo = { };
          version = "1.0.1";
        };
      };
      has-symbols = {
        "1.0.3" = {
          fetchInfo = {
            narHash = "sha256-UwYczbYNNKbZcyCkiLt8e3ASAghJIM72pdCV7DH0XQk=";
            type = "tarball";
            url = "https://registry.npmjs.org/has-symbols/-/has-symbols-1.0.3.tgz";
          };
          ident = "has-symbols";
          ltype = "file";
          treeInfo = { };
          version = "1.0.3";
        };
      };
      has-tostringtag = {
        "1.0.0" = {
          depInfo = {
            has-symbols = {
              descriptor = "^1.0.2";
              pin = "1.0.3";
              runtime = true;
            };
          };
          fetchInfo = {
            narHash = "sha256-EjwjgT5bnHi8aoxdUvSdR4A0YWGKRF5K2VfwACp5VPQ=";
            type = "tarball";
            url = "https://registry.npmjs.org/has-tostringtag/-/has-tostringtag-1.0.0.tgz";
          };
          ident = "has-tostringtag";
          ltype = "file";
          version = "1.0.0";
        };
      };
      hex-rgb = {
        "5.0.0" = {
          fetchInfo = {
            narHash = "sha256-FpFp2XMjtLx7WBUJq5FS0g1QepJC7GhVljkQS3a+nyE=";
            type = "tarball";
            url = "https://registry.npmjs.org/hex-rgb/-/hex-rgb-5.0.0.tgz";
          };
          ident = "hex-rgb";
          ltype = "file";
          treeInfo = { };
          version = "5.0.0";
        };
      };
      hoist-non-react-statics = {
        "3.3.2" = {
          depInfo = {
            react-is = {
              descriptor = "^16.7.0";
              pin = "16.13.1";
              runtime = true;
            };
          };
          fetchInfo = {
            narHash = "sha256-eZiFEkmy/HthIpyyfuVH6yWBrq2Ot6tD5yRndqHMoUM=";
            type = "tarball";
            url = "https://registry.npmjs.org/hoist-non-react-statics/-/hoist-non-react-statics-3.3.2.tgz";
          };
          ident = "hoist-non-react-statics";
          ltype = "file";
          version = "3.3.2";
        };
      };
      hpagent = {
        "1.2.0" = {
          fetchInfo = {
            narHash = "sha256-B0Sov+wlOtQvN/ygcnns6a6buyObXwo9mNRqA82oG+M=";
            type = "tarball";
            url = "https://registry.npmjs.org/hpagent/-/hpagent-1.2.0.tgz";
          };
          ident = "hpagent";
          ltype = "file";
          treeInfo = { };
          version = "1.2.0";
        };
      };
      http2-client = {
        "1.3.5" = {
          fetchInfo = {
            narHash = "sha256-TAGT1j0/SuhPQc5zqeb3Ji5dqdQqT0K2nZ/uIHKVV14=";
            type = "tarball";
            url = "https://registry.npmjs.org/http2-client/-/http2-client-1.3.5.tgz";
          };
          ident = "http2-client";
          ltype = "file";
          treeInfo = { };
          version = "1.3.5";
        };
      };
      human-signals = {
        "2.1.0" = {
          fetchInfo = {
            narHash = "sha256-KRp+zRfFzMRydLkYqjMF4hAY131GmpbWfJB3Lgxiia4=";
            type = "tarball";
            url = "https://registry.npmjs.org/human-signals/-/human-signals-2.1.0.tgz";
          };
          ident = "human-signals";
          ltype = "file";
          treeInfo = { };
          version = "2.1.0";
        };
      };
      ibm-openapi-validator = {
        "0.97.5" = {
          binInfo = {
            binPairs = {
              lint-openapi = "src/cli-validator/index.js";
            };
          };
          depInfo = {
            "@ibm-cloud/openapi-ruleset" = {
              descriptor = "0.45.5";
              pin = "0.45.5";
              runtime = true;
            };
            "@stoplight/spectral-cli" = {
              descriptor = "^6.4.2";
              pin = "6.10.1";
              runtime = true;
            };
            "@stoplight/spectral-core" = {
              descriptor = "^1.12.4";
              pin = "1.18.3";
              runtime = true;
            };
            "@stoplight/spectral-parsers" = {
              descriptor = "^1.0.1";
              pin = "1.0.3";
              runtime = true;
            };
            chalk = {
              descriptor = "^4.1.1";
              pin = "4.1.2";
              runtime = true;
            };
            commander = {
              descriptor = "^2.20.3";
              pin = "2.20.3";
              runtime = true;
            };
            deepmerge = {
              descriptor = "^2.2.1";
              pin = "2.2.1";
              runtime = true;
            };
            find-up = {
              descriptor = "^3.0.0";
              pin = "3.0.0";
              runtime = true;
            };
            globby = {
              descriptor = "^11.0.4";
              pin = "11.1.0";
              runtime = true;
            };
            js-yaml = {
              descriptor = "^3.14.1";
              pin = "3.14.1";
              runtime = true;
            };
            json-dup-key-validator = {
              descriptor = "^1.0.3";
              pin = "1.0.3";
              runtime = true;
            };
            json-schema-ref-parser = {
              descriptor = "^5.1.3";
              pin = "5.1.3";
              runtime = true;
            };
            jsonschema = {
              descriptor = "^1.4.0";
              pin = "1.4.1";
              runtime = true;
            };
            lodash = {
              descriptor = "^4.17.21";
              pin = "4.17.21";
              runtime = true;
            };
            matcher = {
              descriptor = "^1.1.1";
              pin = "1.1.1";
              runtime = true;
            };
            pad = {
              descriptor = "^2.3.0";
              pin = "2.3.0";
              runtime = true;
            };
            require-all = {
              descriptor = "^3.0.0";
              pin = "3.0.0";
              runtime = true;
            };
            semver = {
              descriptor = "^5.7.1";
              pin = "5.7.2";
              runtime = true;
            };
            yaml-js = {
              descriptor = "^0.2.3";
              pin = "0.2.3";
              runtime = true;
            };
          };
          fetchInfo = {
            narHash = "sha256-OAtHLrGRiAwo8mqfU8+TScxq/bRJ4/keuTUJAQcn+rw=";
            type = "tarball";
            url = "https://registry.npmjs.org/ibm-openapi-validator/-/ibm-openapi-validator-0.97.5.tgz";
          };
          ident = "ibm-openapi-validator";
          ltype = "file";
          version = "0.97.5";
        };
      };
      ignore = {
        "5.2.4" = {
          fetchInfo = {
            narHash = "sha256-fHACW7copflWCDPJUsCqYCSzJ6Gg5IQiwSQQRi9kK9s=";
            type = "tarball";
            url = "https://registry.npmjs.org/ignore/-/ignore-5.2.4.tgz";
          };
          ident = "ignore";
          ltype = "file";
          treeInfo = { };
          version = "5.2.4";
        };
      };
      immer = {
        "9.0.21" = {
          fetchInfo = {
            narHash = "sha256-IwQugqdVIPXOuRtwImgR8acRz0T7z045zMJe/JZfTD4=";
            type = "tarball";
            url = "https://registry.npmjs.org/immer/-/immer-9.0.21.tgz";
          };
          ident = "immer";
          ltype = "file";
          treeInfo = { };
          version = "9.0.21";
        };
      };
      import-fresh = {
        "3.3.0" = {
          depInfo = {
            parent-module = {
              descriptor = "^1.0.0";
              pin = "1.0.1";
              runtime = true;
            };
            resolve-from = {
              descriptor = "^4.0.0";
              pin = "4.0.0";
              runtime = true;
            };
          };
          fetchInfo = {
            narHash = "sha256-wgIxG44lNfa7v7fwdcEEDXWhWkzNo8I850QRuK0jGj0=";
            type = "tarball";
            url = "https://registry.npmjs.org/import-fresh/-/import-fresh-3.3.0.tgz";
          };
          ident = "import-fresh";
          ltype = "file";
          version = "3.3.0";
        };
      };
      imurmurhash = {
        "0.1.4" = {
          fetchInfo = {
            narHash = "sha256-kQg6DzTfAqCJNsP9gs1WygIi03+4/AGeF43p9h4LH30=";
            type = "tarball";
            url = "https://registry.npmjs.org/imurmurhash/-/imurmurhash-0.1.4.tgz";
          };
          ident = "imurmurhash";
          ltype = "file";
          treeInfo = { };
          version = "0.1.4";
        };
      };
      inflight = {
        "1.0.6" = {
          depInfo = {
            once = {
              descriptor = "^1.3.0";
              pin = "1.4.0";
              runtime = true;
            };
            wrappy = {
              descriptor = "1";
              pin = "1.0.2";
              runtime = true;
            };
          };
          fetchInfo = {
            narHash = "sha256-QYcVNxVNod45ft7XJVhWJCKuVPN95a8FwfAefYWKqhg=";
            type = "tarball";
            url = "https://registry.npmjs.org/inflight/-/inflight-1.0.6.tgz";
          };
          ident = "inflight";
          ltype = "file";
          version = "1.0.6";
        };
      };
      inherits = {
        "2.0.4" = {
          fetchInfo = {
            narHash = "sha256-EnwyCC7V9GbsUCFpqRNJtPNfbbEqyJTYxbRqR5SgYW0=";
            type = "tarball";
            url = "https://registry.npmjs.org/inherits/-/inherits-2.0.4.tgz";
          };
          ident = "inherits";
          ltype = "file";
          treeInfo = { };
          version = "2.0.4";
        };
      };
      internal-slot = {
        "1.0.5" = {
          depInfo = {
            get-intrinsic = {
              descriptor = "^1.2.0";
              pin = "1.2.1";
              runtime = true;
            };
            has = {
              descriptor = "^1.0.3";
              pin = "1.0.3";
              runtime = true;
            };
            side-channel = {
              descriptor = "^1.0.4";
              pin = "1.0.4";
              runtime = true;
            };
          };
          fetchInfo = {
            narHash = "sha256-eK9f78pfeMH3KsgSG/xJfY9Dwkyj+ODRoiyIvgaaK4A=";
            type = "tarball";
            url = "https://registry.npmjs.org/internal-slot/-/internal-slot-1.0.5.tgz";
          };
          ident = "internal-slot";
          ltype = "file";
          version = "1.0.5";
        };
      };
      internmap = {
        "2.0.3" = {
          fetchInfo = {
            narHash = "sha256-KIR9V1DKo0L+A86SoyglogHN3+BJNc/AHV5nKZys7yY=";
            type = "tarball";
            url = "https://registry.npmjs.org/internmap/-/internmap-2.0.3.tgz";
          };
          ident = "internmap";
          ltype = "file";
          treeInfo = { };
          version = "2.0.3";
        };
      };
      is-array-buffer = {
        "3.0.2" = {
          depInfo = {
            call-bind = {
              descriptor = "^1.0.2";
              pin = "1.0.2";
              runtime = true;
            };
            get-intrinsic = {
              descriptor = "^1.2.0";
              pin = "1.2.1";
              runtime = true;
            };
            is-typed-array = {
              descriptor = "^1.1.10";
              pin = "1.1.12";
              runtime = true;
            };
          };
          fetchInfo = {
            narHash = "sha256-cente5TFioP5ObySfy4+ktghDmCgFGicBJxZhbjBpNg=";
            type = "tarball";
            url = "https://registry.npmjs.org/is-array-buffer/-/is-array-buffer-3.0.2.tgz";
          };
          ident = "is-array-buffer";
          ltype = "file";
          version = "3.0.2";
        };
      };
      is-arrayish = {
        "0.2.1" = {
          fetchInfo = {
            narHash = "sha256-wvuJg92GZxDL9IffjN5ttz8DRki65ZgZoM3Mr1V9IyM=";
            type = "tarball";
            url = "https://registry.npmjs.org/is-arrayish/-/is-arrayish-0.2.1.tgz";
          };
          ident = "is-arrayish";
          ltype = "file";
          treeInfo = { };
          version = "0.2.1";
        };
      };
      is-bigint = {
        "1.0.4" = {
          depInfo = {
            has-bigints = {
              descriptor = "^1.0.1";
              pin = "1.0.2";
              runtime = true;
            };
          };
          fetchInfo = {
            narHash = "sha256-GKH3x0bhVd9eRyfWcs89IHQJgjn/5h0mITbkxgg7mAg=";
            type = "tarball";
            url = "https://registry.npmjs.org/is-bigint/-/is-bigint-1.0.4.tgz";
          };
          ident = "is-bigint";
          ltype = "file";
          version = "1.0.4";
        };
      };
      is-binary-path = {
        "2.1.0" = {
          depInfo = {
            binary-extensions = {
              descriptor = "^2.0.0";
              pin = "2.2.0";
              runtime = true;
            };
          };
          fetchInfo = {
            narHash = "sha256-sw0xKthTgrk2Z3NKJLg5XXpyAcTpC5aQkG0LDEGA8Lk=";
            type = "tarball";
            url = "https://registry.npmjs.org/is-binary-path/-/is-binary-path-2.1.0.tgz";
          };
          ident = "is-binary-path";
          ltype = "file";
          version = "2.1.0";
        };
      };
      is-boolean-object = {
        "1.1.2" = {
          depInfo = {
            call-bind = {
              descriptor = "^1.0.2";
              pin = "1.0.2";
              runtime = true;
            };
            has-tostringtag = {
              descriptor = "^1.0.0";
              pin = "1.0.0";
              runtime = true;
            };
          };
          fetchInfo = {
            narHash = "sha256-/cvTh9+AMWF6iMMXCngaxj+LnPNCxatQFp/pSrgs74k=";
            type = "tarball";
            url = "https://registry.npmjs.org/is-boolean-object/-/is-boolean-object-1.1.2.tgz";
          };
          ident = "is-boolean-object";
          ltype = "file";
          version = "1.1.2";
        };
      };
      is-callable = {
        "1.2.7" = {
          fetchInfo = {
            narHash = "sha256-7h/ZjgrSnEtMqP8EQvVCNjfvNS7ZQ03uQIqtAG7afmw=";
            type = "tarball";
            url = "https://registry.npmjs.org/is-callable/-/is-callable-1.2.7.tgz";
          };
          ident = "is-callable";
          ltype = "file";
          treeInfo = { };
          version = "1.2.7";
        };
      };
      is-core-module = {
        "2.13.0" = {
          depInfo = {
            has = {
              descriptor = "^1.0.3";
              pin = "1.0.3";
              runtime = true;
            };
          };
          fetchInfo = {
            narHash = "sha256-Zfs85iR40drNuBag9ZL90jcygps8dljkurXcCiQo3Do=";
            type = "tarball";
            url = "https://registry.npmjs.org/is-core-module/-/is-core-module-2.13.0.tgz";
          };
          ident = "is-core-module";
          ltype = "file";
          version = "2.13.0";
        };
      };
      is-date-object = {
        "1.0.5" = {
          depInfo = {
            has-tostringtag = {
              descriptor = "^1.0.0";
              pin = "1.0.0";
              runtime = true;
            };
          };
          fetchInfo = {
            narHash = "sha256-DOoOg9XTnjmck7pSLUl5chkS5FDZHmbwlkiIWi2ESwg=";
            type = "tarball";
            url = "https://registry.npmjs.org/is-date-object/-/is-date-object-1.0.5.tgz";
          };
          ident = "is-date-object";
          ltype = "file";
          version = "1.0.5";
        };
      };
      is-extglob = {
        "2.1.1" = {
          fetchInfo = {
            narHash = "sha256-vY1Bx1tKKhqfbF3itxnDzWl3wA8dMl1GiNL93Bdb+1A=";
            type = "tarball";
            url = "https://registry.npmjs.org/is-extglob/-/is-extglob-2.1.1.tgz";
          };
          ident = "is-extglob";
          ltype = "file";
          treeInfo = { };
          version = "2.1.1";
        };
      };
      is-fullwidth-code-point = {
        "3.0.0" = {
          fetchInfo = {
            narHash = "sha256-FAwh/1ODBHIw/Tm2EQLvleV6Xkb1qy7AKy6kBEi9ei8=";
            type = "tarball";
            url = "https://registry.npmjs.org/is-fullwidth-code-point/-/is-fullwidth-code-point-3.0.0.tgz";
          };
          ident = "is-fullwidth-code-point";
          ltype = "file";
          treeInfo = { };
          version = "3.0.0";
        };
      };
      is-glob = {
        "4.0.3" = {
          depInfo = {
            is-extglob = {
              descriptor = "^2.1.1";
              pin = "2.1.1";
              runtime = true;
            };
          };
          fetchInfo = {
            narHash = "sha256-7FIQemaZXYPFuIoAykkbzU8g5B2TlAUoymUpYM0QO9A=";
            type = "tarball";
            url = "https://registry.npmjs.org/is-glob/-/is-glob-4.0.3.tgz";
          };
          ident = "is-glob";
          ltype = "file";
          version = "4.0.3";
        };
      };
      is-negative-zero = {
        "2.0.2" = {
          fetchInfo = {
            narHash = "sha256-df2CjgfWqs/rALktCOr77RPoyjtKAReBT0yFXLDqFAo=";
            type = "tarball";
            url = "https://registry.npmjs.org/is-negative-zero/-/is-negative-zero-2.0.2.tgz";
          };
          ident = "is-negative-zero";
          ltype = "file";
          treeInfo = { };
          version = "2.0.2";
        };
      };
      is-number = {
        "7.0.0" = {
          fetchInfo = {
            narHash = "sha256-sOcAFDhYCindWvE4jW6RNeoCBP4VZEyS7M3dq7cGgNI=";
            type = "tarball";
            url = "https://registry.npmjs.org/is-number/-/is-number-7.0.0.tgz";
          };
          ident = "is-number";
          ltype = "file";
          treeInfo = { };
          version = "7.0.0";
        };
      };
      is-number-object = {
        "1.0.7" = {
          depInfo = {
            has-tostringtag = {
              descriptor = "^1.0.0";
              pin = "1.0.0";
              runtime = true;
            };
          };
          fetchInfo = {
            narHash = "sha256-MLgeeh0r1+/h/F32pDU8xH/pnSoFw6JtTM9y6GF2ne8=";
            type = "tarball";
            url = "https://registry.npmjs.org/is-number-object/-/is-number-object-1.0.7.tgz";
          };
          ident = "is-number-object";
          ltype = "file";
          version = "1.0.7";
        };
      };
      is-path-inside = {
        "3.0.3" = {
          fetchInfo = {
            narHash = "sha256-LKpocwZBiRKJz6FreaEet7sFz8yCqtLeibCW5Os5m2Q=";
            type = "tarball";
            url = "https://registry.npmjs.org/is-path-inside/-/is-path-inside-3.0.3.tgz";
          };
          ident = "is-path-inside";
          ltype = "file";
          treeInfo = { };
          version = "3.0.3";
        };
      };
      is-reference = {
        "1.2.1" = {
          depInfo = {
            "@types/estree" = {
              descriptor = "*";
              pin = "0.0.39";
              runtime = true;
            };
          };
          fetchInfo = {
            narHash = "sha256-fOuUkved1TR1elsn+8mGhlPUWkyRR66Eg7tmQR3Y/MY=";
            type = "tarball";
            url = "https://registry.npmjs.org/is-reference/-/is-reference-1.2.1.tgz";
          };
          ident = "is-reference";
          ltype = "file";
          version = "1.2.1";
        };
      };
      is-regex = {
        "1.1.4" = {
          depInfo = {
            call-bind = {
              descriptor = "^1.0.2";
              pin = "1.0.2";
              runtime = true;
            };
            has-tostringtag = {
              descriptor = "^1.0.0";
              pin = "1.0.0";
              runtime = true;
            };
          };
          fetchInfo = {
            narHash = "sha256-KgL5DJkp0EUQxKXR/HfjXwrUPfTY/rbhfQTt2384qM0=";
            type = "tarball";
            url = "https://registry.npmjs.org/is-regex/-/is-regex-1.1.4.tgz";
          };
          ident = "is-regex";
          ltype = "file";
          version = "1.1.4";
        };
      };
      is-shared-array-buffer = {
        "1.0.2" = {
          depInfo = {
            call-bind = {
              descriptor = "^1.0.2";
              pin = "1.0.2";
              runtime = true;
            };
          };
          fetchInfo = {
            narHash = "sha256-rebNppBowg+u/Gx3TI07QGZD0v26y5CxwdQ05B2Ei8k=";
            type = "tarball";
            url = "https://registry.npmjs.org/is-shared-array-buffer/-/is-shared-array-buffer-1.0.2.tgz";
          };
          ident = "is-shared-array-buffer";
          ltype = "file";
          version = "1.0.2";
        };
      };
      is-stream = {
        "2.0.1" = {
          fetchInfo = {
            narHash = "sha256-Fh80EDj5F2Taioq1Q5Q877MARryNTEB3CzpqWiSUlJQ=";
            type = "tarball";
            url = "https://registry.npmjs.org/is-stream/-/is-stream-2.0.1.tgz";
          };
          ident = "is-stream";
          ltype = "file";
          treeInfo = { };
          version = "2.0.1";
        };
      };
      is-string = {
        "1.0.7" = {
          depInfo = {
            has-tostringtag = {
              descriptor = "^1.0.0";
              pin = "1.0.0";
              runtime = true;
            };
          };
          fetchInfo = {
            narHash = "sha256-sGSG0tODo7omm2xgc/PIXmQbxr3CqLxeFJCJ3doOhCI=";
            type = "tarball";
            url = "https://registry.npmjs.org/is-string/-/is-string-1.0.7.tgz";
          };
          ident = "is-string";
          ltype = "file";
          version = "1.0.7";
        };
      };
      is-symbol = {
        "1.0.4" = {
          depInfo = {
            has-symbols = {
              descriptor = "^1.0.2";
              pin = "1.0.3";
              runtime = true;
            };
          };
          fetchInfo = {
            narHash = "sha256-D6RS2woSBBiF6Sd9vb7CRmQDpk7qEkvkcF+2eNufyZk=";
            type = "tarball";
            url = "https://registry.npmjs.org/is-symbol/-/is-symbol-1.0.4.tgz";
          };
          ident = "is-symbol";
          ltype = "file";
          version = "1.0.4";
        };
      };
      is-typed-array = {
        "1.1.12" = {
          depInfo = {
            which-typed-array = {
              descriptor = "^1.1.11";
              pin = "1.1.11";
              runtime = true;
            };
          };
          fetchInfo = {
            narHash = "sha256-STk0gB5cPrWs3P+ODY2g97ZtA6IOOtloNUAj0jy99bY=";
            type = "tarball";
            url = "https://registry.npmjs.org/is-typed-array/-/is-typed-array-1.1.12.tgz";
          };
          ident = "is-typed-array";
          ltype = "file";
          version = "1.1.12";
        };
      };
      is-weakref = {
        "1.0.2" = {
          depInfo = {
            call-bind = {
              descriptor = "^1.0.2";
              pin = "1.0.2";
              runtime = true;
            };
          };
          fetchInfo = {
            narHash = "sha256-OIz4DKzypaeD/AYOhAgijzNIbaNnSDnLg9sCVXTbiN4=";
            type = "tarball";
            url = "https://registry.npmjs.org/is-weakref/-/is-weakref-1.0.2.tgz";
          };
          ident = "is-weakref";
          ltype = "file";
          version = "1.0.2";
        };
      };
      isarray = {
        "2.0.5" = {
          fetchInfo = {
            narHash = "sha256-RJLBeZgYHQtWnj9N67T92krmNciVv5R1mefQjp9Inic=";
            type = "tarball";
            url = "https://registry.npmjs.org/isarray/-/isarray-2.0.5.tgz";
          };
          ident = "isarray";
          ltype = "file";
          treeInfo = { };
          version = "2.0.5";
        };
      };
      isexe = {
        "2.0.0" = {
          fetchInfo = {
            narHash = "sha256-l3Fv+HpHS6H1TqfC1WSGjsGlX08oDHyHdsEu9JQkvhE=";
            type = "tarball";
            url = "https://registry.npmjs.org/isexe/-/isexe-2.0.0.tgz";
          };
          ident = "isexe";
          ltype = "file";
          treeInfo = { };
          version = "2.0.0";
        };
      };
      jiti = {
        "1.19.1" = {
          binInfo = {
            binPairs = {
              jiti = "bin/jiti.js";
            };
          };
          fetchInfo = {
            narHash = "sha256-r+/scwMhEz4ifezUi6biBbiVPIdVRCmaHJecDTg++A4=";
            type = "tarball";
            url = "https://registry.npmjs.org/jiti/-/jiti-1.19.1.tgz";
          };
          ident = "jiti";
          ltype = "file";
          treeInfo = { };
          version = "1.19.1";
        };
      };
      js-tokens = {
        "4.0.0" = {
          fetchInfo = {
            narHash = "sha256-Dc0GyrdV+HX5ZTMTdtFfjh30QurY6nxA8wCQMZsnd6w=";
            type = "tarball";
            url = "https://registry.npmjs.org/js-tokens/-/js-tokens-4.0.0.tgz";
          };
          ident = "js-tokens";
          ltype = "file";
          treeInfo = { };
          version = "4.0.0";
        };
      };
      js-yaml = {
        "3.14.1" = {
          binInfo = {
            binPairs = {
              js-yaml = "bin/js-yaml.js";
            };
          };
          depInfo = {
            argparse = {
              descriptor = "^1.0.7";
              pin = "1.0.10";
              runtime = true;
            };
            esprima = {
              descriptor = "^4.0.0";
              pin = "4.0.1";
              runtime = true;
            };
          };
          fetchInfo = {
            narHash = "sha256-77V7kBw4w4mGhwUA3ay8IvZMqBK8XpXCEjaCDhCyuHU=";
            type = "tarball";
            url = "https://registry.npmjs.org/js-yaml/-/js-yaml-3.14.1.tgz";
          };
          ident = "js-yaml";
          ltype = "file";
          version = "3.14.1";
        };
        "4.1.0" = {
          binInfo = {
            binPairs = {
              js-yaml = "bin/js-yaml.js";
            };
          };
          depInfo = {
            argparse = {
              descriptor = "^2.0.1";
              pin = "2.0.1";
              runtime = true;
            };
          };
          fetchInfo = {
            narHash = "sha256-puppzIyc3zvi1et748xYGKqaZdZwBxnBhqjUHXHA898=";
            type = "tarball";
            url = "https://registry.npmjs.org/js-yaml/-/js-yaml-4.1.0.tgz";
          };
          ident = "js-yaml";
          ltype = "file";
          version = "4.1.0";
        };
      };
      jsep = {
        "1.3.8" = {
          fetchInfo = {
            narHash = "sha256-xry2lpW+sVL4dTK6//4hYWC97UlEtIBYRwHQLcou4uA=";
            type = "tarball";
            url = "https://registry.npmjs.org/jsep/-/jsep-1.3.8.tgz";
          };
          ident = "jsep";
          ltype = "file";
          treeInfo = { };
          version = "1.3.8";
        };
      };
      json-dup-key-validator = {
        "1.0.3" = {
          depInfo = {
            backslash = {
              descriptor = "^0.2.0";
              pin = "0.2.0";
              runtime = true;
            };
          };
          fetchInfo = {
            narHash = "sha256-yn/QpfNroVs+9nRueYeUP4f8EGECd7LjWzud2kMjfWs=";
            type = "tarball";
            url = "https://registry.npmjs.org/json-dup-key-validator/-/json-dup-key-validator-1.0.3.tgz";
          };
          ident = "json-dup-key-validator";
          ltype = "file";
          version = "1.0.3";
        };
      };
      json-parse-even-better-errors = {
        "2.3.1" = {
          fetchInfo = {
            narHash = "sha256-JLmbiGbR2cXNIiFjyKZj8WvbNwUEVpADUgztOocgA1s=";
            type = "tarball";
            url = "https://registry.npmjs.org/json-parse-even-better-errors/-/json-parse-even-better-errors-2.3.1.tgz";
          };
          ident = "json-parse-even-better-errors";
          ltype = "file";
          treeInfo = { };
          version = "2.3.1";
        };
      };
      json-schema-ref-parser = {
        "5.1.3" = {
          depInfo = {
            call-me-maybe = {
              descriptor = "^1.0.1";
              pin = "1.0.2";
              runtime = true;
            };
            debug = {
              descriptor = "^3.1.0";
              pin = "3.2.7";
              runtime = true;
            };
            js-yaml = {
              descriptor = "^3.12.0";
              pin = "3.14.1";
              runtime = true;
            };
            ono = {
              descriptor = "^4.0.6";
              pin = "4.0.11";
              runtime = true;
            };
          };
          fetchInfo = {
            narHash = "sha256-+e0kioQr/N6EzZiP3EpLgabD3Za+S8rslA8TnBCUokI=";
            type = "tarball";
            url = "https://registry.npmjs.org/json-schema-ref-parser/-/json-schema-ref-parser-5.1.3.tgz";
          };
          ident = "json-schema-ref-parser";
          ltype = "file";
          version = "5.1.3";
        };
      };
      json-schema-traverse = {
        "0.4.1" = {
          fetchInfo = {
            narHash = "sha256-6yxGXpY70Yc8jAAxR3YYhEXUc0SHZ3Peg+laVwXK9nQ=";
            type = "tarball";
            url = "https://registry.npmjs.org/json-schema-traverse/-/json-schema-traverse-0.4.1.tgz";
          };
          ident = "json-schema-traverse";
          ltype = "file";
          treeInfo = { };
          version = "0.4.1";
        };
        "1.0.0" = {
          fetchInfo = {
            narHash = "sha256-oFBdQYJbyzJo1poFuGBgYzTLpPZgBC9Xi3c8TXqQkS4=";
            type = "tarball";
            url = "https://registry.npmjs.org/json-schema-traverse/-/json-schema-traverse-1.0.0.tgz";
          };
          ident = "json-schema-traverse";
          ltype = "file";
          treeInfo = { };
          version = "1.0.0";
        };
      };
      json-stable-stringify-without-jsonify = {
        "1.0.1" = {
          fetchInfo = {
            narHash = "sha256-cxsnkpGiO9yUbm8LuBVJrbV2c3Pflghlra6EO35WgdM=";
            type = "tarball";
            url = "https://registry.npmjs.org/json-stable-stringify-without-jsonify/-/json-stable-stringify-without-jsonify-1.0.1.tgz";
          };
          ident = "json-stable-stringify-without-jsonify";
          ltype = "file";
          treeInfo = { };
          version = "1.0.1";
        };
      };
      json5 = {
        "1.0.2" = {
          binInfo = {
            binPairs = {
              json5 = "lib/cli.js";
            };
          };
          depInfo = {
            minimist = {
              descriptor = "^1.2.0";
              pin = "1.2.8";
              runtime = true;
            };
          };
          fetchInfo = {
            narHash = "sha256-muEUSc3kL7gt6Qg1PymdAwY57H158NnEOB5/FlGPqOY=";
            type = "tarball";
            url = "https://registry.npmjs.org/json5/-/json5-1.0.2.tgz";
          };
          ident = "json5";
          ltype = "file";
          version = "1.0.2";
        };
      };
      jsonc-parser = {
        "2.2.1" = {
          fetchInfo = {
            narHash = "sha256-4uk/KB7Z53M8ZC0WDTFX5A9POXPScY7y8fpw8kZpIdQ=";
            type = "tarball";
            url = "https://registry.npmjs.org/jsonc-parser/-/jsonc-parser-2.2.1.tgz";
          };
          ident = "jsonc-parser";
          ltype = "file";
          treeInfo = { };
          version = "2.2.1";
        };
      };
      jsonfile = {
        "6.1.0" = {
          depInfo = {
            graceful-fs = {
              descriptor = "^4.1.6";
              optional = true;
              pin = "4.2.11";
              runtime = true;
            };
            universalify = {
              descriptor = "^2.0.0";
              pin = "2.0.0";
              runtime = true;
            };
          };
          fetchInfo = {
            narHash = "sha256-4QwM2yG0GbEgncuoNWEYOtRjAS9tFi4mkUMpyk7Aht4=";
            type = "tarball";
            url = "https://registry.npmjs.org/jsonfile/-/jsonfile-6.1.0.tgz";
          };
          ident = "jsonfile";
          ltype = "file";
          version = "6.1.0";
        };
      };
      jsonpath-plus = {
        "6.0.1" = {
          fetchInfo = {
            narHash = "sha256-sLuJ/2iMy1YXsfdZLNpvNOi84RQY6Kl3A0bTAH2gf/U=";
            type = "tarball";
            url = "https://registry.npmjs.org/jsonpath-plus/-/jsonpath-plus-6.0.1.tgz";
          };
          ident = "jsonpath-plus";
          ltype = "file";
          treeInfo = { };
          version = "6.0.1";
        };
        "7.1.0" = {
          fetchInfo = {
            narHash = "sha256-02chxB91HmyifeghWSBqk65JooJ95euokX2gS+3KML4=";
            type = "tarball";
            url = "https://registry.npmjs.org/jsonpath-plus/-/jsonpath-plus-7.1.0.tgz";
          };
          ident = "jsonpath-plus";
          ltype = "file";
          treeInfo = { };
          version = "7.1.0";
        };
      };
      jsonpointer = {
        "5.0.1" = {
          fetchInfo = {
            narHash = "sha256-J8nyDp/Ma3gqzYzIAU7zLJwSWOuJoMn4HmOBBpwHpJI=";
            type = "tarball";
            url = "https://registry.npmjs.org/jsonpointer/-/jsonpointer-5.0.1.tgz";
          };
          ident = "jsonpointer";
          ltype = "file";
          treeInfo = { };
          version = "5.0.1";
        };
      };
      jsonschema = {
        "1.4.1" = {
          fetchInfo = {
            narHash = "sha256-3ppbBJCWYiaT9f9fnSnrhWiW89YxXX8QkowjjQMUPSI=";
            type = "tarball";
            url = "https://registry.npmjs.org/jsonschema/-/jsonschema-1.4.1.tgz";
          };
          ident = "jsonschema";
          ltype = "file";
          treeInfo = { };
          version = "1.4.1";
        };
      };
      jsx-ast-utils = {
        "3.3.5" = {
          depInfo = {
            array-includes = {
              descriptor = "^3.1.6";
              pin = "3.1.6";
              runtime = true;
            };
            "array.prototype.flat" = {
              descriptor = "^1.3.1";
              pin = "1.3.1";
              runtime = true;
            };
            "object.assign" = {
              descriptor = "^4.1.4";
              pin = "4.1.4";
              runtime = true;
            };
            "object.values" = {
              descriptor = "^1.1.6";
              pin = "1.1.6";
              runtime = true;
            };
          };
          fetchInfo = {
            narHash = "sha256-OZfyEVVS6vN5VqTYsBOAszIcTVT8pjogNnf/b0c0tTk=";
            type = "tarball";
            url = "https://registry.npmjs.org/jsx-ast-utils/-/jsx-ast-utils-3.3.5.tgz";
          };
          ident = "jsx-ast-utils";
          ltype = "file";
          version = "3.3.5";
        };
      };
      language-subtag-registry = {
        "0.3.22" = {
          fetchInfo = {
            narHash = "sha256-t6o6KNRUVs+U/IJbZH6ctsJFr90Czezi5LAR7CjppQY=";
            type = "tarball";
            url = "https://registry.npmjs.org/language-subtag-registry/-/language-subtag-registry-0.3.22.tgz";
          };
          ident = "language-subtag-registry";
          ltype = "file";
          treeInfo = { };
          version = "0.3.22";
        };
      };
      language-tags = {
        "1.0.5" = {
          depInfo = {
            language-subtag-registry = {
              descriptor = "~0.3.2";
              pin = "0.3.22";
              runtime = true;
            };
          };
          fetchInfo = {
            narHash = "sha256-7LVx9miRFYOI8+O086LCWuB541C+p2hfR+v54YPGUgs=";
            type = "tarball";
            url = "https://registry.npmjs.org/language-tags/-/language-tags-1.0.5.tgz";
          };
          ident = "language-tags";
          ltype = "file";
          version = "1.0.5";
        };
      };
      leven = {
        "3.1.0" = {
          fetchInfo = {
            narHash = "sha256-Lqb1AQUSH/47Zodo4pnzTiJ7YVH/ZJ1KxQDyUOvr3Ok=";
            type = "tarball";
            url = "https://registry.npmjs.org/leven/-/leven-3.1.0.tgz";
          };
          ident = "leven";
          ltype = "file";
          treeInfo = { };
          version = "3.1.0";
        };
      };
      levn = {
        "0.4.1" = {
          depInfo = {
            prelude-ls = {
              descriptor = "^1.2.1";
              pin = "1.2.1";
              runtime = true;
            };
            type-check = {
              descriptor = "~0.4.0";
              pin = "0.4.0";
              runtime = true;
            };
          };
          fetchInfo = {
            narHash = "sha256-azArXDTc0Dj7aDEBLsNQ4XOUQ/Vo86h4oHfl4AtwvAQ=";
            type = "tarball";
            url = "https://registry.npmjs.org/levn/-/levn-0.4.1.tgz";
          };
          ident = "levn";
          ltype = "file";
          version = "0.4.1";
        };
      };
      lilconfig = {
        "2.1.0" = {
          fetchInfo = {
            narHash = "sha256-Frn8b5WofAM65ZIDChyOlfTvuQibkx7zl28Zft5zHD0=";
            type = "tarball";
            url = "https://registry.npmjs.org/lilconfig/-/lilconfig-2.1.0.tgz";
          };
          ident = "lilconfig";
          ltype = "file";
          treeInfo = { };
          version = "2.1.0";
        };
      };
      lines-and-columns = {
        "1.2.4" = {
          fetchInfo = {
            narHash = "sha256-WUoaqN7ad2gwBKftukjtNRrFw19fcS7dRRog0pp4OHE=";
            type = "tarball";
            url = "https://registry.npmjs.org/lines-and-columns/-/lines-and-columns-1.2.4.tgz";
          };
          ident = "lines-and-columns";
          ltype = "file";
          treeInfo = { };
          version = "1.2.4";
        };
      };
      locate-path = {
        "3.0.0" = {
          depInfo = {
            p-locate = {
              descriptor = "^3.0.0";
              pin = "3.0.0";
              runtime = true;
            };
            path-exists = {
              descriptor = "^3.0.0";
              pin = "3.0.0";
              runtime = true;
            };
          };
          fetchInfo = {
            narHash = "sha256-PL6JLv3yHkyLXYpeBBdTZ7/bFNiCbCjlr1YNfze21F4=";
            type = "tarball";
            url = "https://registry.npmjs.org/locate-path/-/locate-path-3.0.0.tgz";
          };
          ident = "locate-path";
          ltype = "file";
          version = "3.0.0";
        };
        "6.0.0" = {
          depInfo = {
            p-locate = {
              descriptor = "^5.0.0";
              pin = "5.0.0";
              runtime = true;
            };
          };
          fetchInfo = {
            narHash = "sha256-bqbrOtZJVUwbqlw3MeIhr30gfcn1Unv2jM3LYAXal9Q=";
            type = "tarball";
            url = "https://registry.npmjs.org/locate-path/-/locate-path-6.0.0.tgz";
          };
          ident = "locate-path";
          ltype = "file";
          version = "6.0.0";
        };
      };
      lodash = {
        "4.17.21" = {
          fetchInfo = {
            narHash = "sha256-amyN064Yh6psvOfLgcpktd5dRNQStUYHHoIqiI6DMek=";
            type = "tarball";
            url = "https://registry.npmjs.org/lodash/-/lodash-4.17.21.tgz";
          };
          ident = "lodash";
          ltype = "file";
          treeInfo = { };
          version = "4.17.21";
        };
      };
      "lodash.get" = {
        "4.4.2" = {
          fetchInfo = {
            narHash = "sha256-wZOZjWT3WsLMfy4Uv58CbV4o/0IjwZ2k9Jd0zGBF5/c=";
            type = "tarball";
            url = "https://registry.npmjs.org/lodash.get/-/lodash.get-4.4.2.tgz";
          };
          ident = "lodash.get";
          ltype = "file";
          treeInfo = { };
          version = "4.4.2";
        };
      };
      "lodash.isempty" = {
        "4.4.0" = {
          fetchInfo = {
            narHash = "sha256-UKZTGO7LbDjQ2ZXqXpOLlX561kSTR+TWEMbuMJJLKOE=";
            type = "tarball";
            url = "https://registry.npmjs.org/lodash.isempty/-/lodash.isempty-4.4.0.tgz";
          };
          ident = "lodash.isempty";
          ltype = "file";
          treeInfo = { };
          version = "4.4.0";
        };
      };
      "lodash.merge" = {
        "4.6.2" = {
          fetchInfo = {
            narHash = "sha256-AnfgvzyOFLIADkPCDfsDKkaKULahu8+mA2KlIMIAg14=";
            type = "tarball";
            url = "https://registry.npmjs.org/lodash.merge/-/lodash.merge-4.6.2.tgz";
          };
          ident = "lodash.merge";
          ltype = "file";
          treeInfo = { };
          version = "4.6.2";
        };
      };
      "lodash.omit" = {
        "4.5.0" = {
          fetchInfo = {
            narHash = "sha256-02ws4Kyheaq/oLE62Tk/Dy+fAWSPzZWs7cngzr+zq/o=";
            type = "tarball";
            url = "https://registry.npmjs.org/lodash.omit/-/lodash.omit-4.5.0.tgz";
          };
          ident = "lodash.omit";
          ltype = "file";
          treeInfo = { };
          version = "4.5.0";
        };
      };
      "lodash.omitby" = {
        "4.6.0" = {
          fetchInfo = {
            narHash = "sha256-nmgrnafIsTyAnhaGicLFWV7+BdTb+JVP8OgZd44a028=";
            type = "tarball";
            url = "https://registry.npmjs.org/lodash.omitby/-/lodash.omitby-4.6.0.tgz";
          };
          ident = "lodash.omitby";
          ltype = "file";
          treeInfo = { };
          version = "4.6.0";
        };
      };
      "lodash.topath" = {
        "4.5.2" = {
          fetchInfo = {
            narHash = "sha256-3aFuJwgps5++V1+NiIqp8F85cyM3ox59tj2Ux7WbD4s=";
            type = "tarball";
            url = "https://registry.npmjs.org/lodash.topath/-/lodash.topath-4.5.2.tgz";
          };
          ident = "lodash.topath";
          ltype = "file";
          treeInfo = { };
          version = "4.5.2";
        };
      };
      "lodash.uniq" = {
        "4.5.0" = {
          fetchInfo = {
            narHash = "sha256-Sw5vOkUFgRD6stksmS6OQiTcDS6QuEIufLF9NI85EB0=";
            type = "tarball";
            url = "https://registry.npmjs.org/lodash.uniq/-/lodash.uniq-4.5.0.tgz";
          };
          ident = "lodash.uniq";
          ltype = "file";
          treeInfo = { };
          version = "4.5.0";
        };
      };
      "lodash.uniqby" = {
        "4.7.0" = {
          fetchInfo = {
            narHash = "sha256-RdNoosS58YOS75dIVwPPQBqLZcjCzVr4CA/N9q5tbZ0=";
            type = "tarball";
            url = "https://registry.npmjs.org/lodash.uniqby/-/lodash.uniqby-4.7.0.tgz";
          };
          ident = "lodash.uniqby";
          ltype = "file";
          treeInfo = { };
          version = "4.7.0";
        };
      };
      "lodash.uniqwith" = {
        "4.5.0" = {
          fetchInfo = {
            narHash = "sha256-YEatPFrj1x7fK2JgEgYhnh8JSYiFtbwbHCajA3Ex7o8=";
            type = "tarball";
            url = "https://registry.npmjs.org/lodash.uniqwith/-/lodash.uniqwith-4.5.0.tgz";
          };
          ident = "lodash.uniqwith";
          ltype = "file";
          treeInfo = { };
          version = "4.5.0";
        };
      };
      loose-envify = {
        "1.4.0" = {
          binInfo = {
            binPairs = {
              loose-envify = "cli.js";
            };
          };
          depInfo = {
            js-tokens = {
              descriptor = "^3.0.0 || ^4.0.0";
              pin = "4.0.0";
              runtime = true;
            };
          };
          fetchInfo = {
            narHash = "sha256-abQxb8UZImSEBRMsA9wep5NK2rpyd9JG0YeTGqz+jDk=";
            type = "tarball";
            url = "https://registry.npmjs.org/loose-envify/-/loose-envify-1.4.0.tgz";
          };
          ident = "loose-envify";
          ltype = "file";
          version = "1.4.0";
        };
      };
      lru-cache = {
        "6.0.0" = {
          depInfo = {
            yallist = {
              descriptor = "^4.0.0";
              pin = "4.0.0";
              runtime = true;
            };
          };
          fetchInfo = {
            narHash = "sha256-lBc6340YZYAh1Numj5iz418ChtGb3UUtRZLOYj/WJXg=";
            type = "tarball";
            url = "https://registry.npmjs.org/lru-cache/-/lru-cache-6.0.0.tgz";
          };
          ident = "lru-cache";
          ltype = "file";
          version = "6.0.0";
        };
      };
      magic-string = {
        "0.25.9" = {
          depInfo = {
            sourcemap-codec = {
              descriptor = "^1.4.8";
              pin = "1.4.8";
              runtime = true;
            };
          };
          fetchInfo = {
            narHash = "sha256-DZQkG9gmtfcmQOclaDQzaNCzG0alqiIHVG+aF8g82aQ=";
            type = "tarball";
            url = "https://registry.npmjs.org/magic-string/-/magic-string-0.25.9.tgz";
          };
          ident = "magic-string";
          ltype = "file";
          version = "0.25.9";
        };
      };
      matcher = {
        "1.1.1" = {
          depInfo = {
            escape-string-regexp = {
              descriptor = "^1.0.4";
              pin = "1.0.5";
              runtime = true;
            };
          };
          fetchInfo = {
            narHash = "sha256-7mt6KwWzoh6HKT2mtqqgn3szmfQ+BiHpnjZjnQrjSGg=";
            type = "tarball";
            url = "https://registry.npmjs.org/matcher/-/matcher-1.1.1.tgz";
          };
          ident = "matcher";
          ltype = "file";
          version = "1.1.1";
        };
      };
      merge-stream = {
        "2.0.0" = {
          fetchInfo = {
            narHash = "sha256-0ZC11XNq6TaUxEXOV9bwaS71Qd3wQoqZAkFRvtnab5I=";
            type = "tarball";
            url = "https://registry.npmjs.org/merge-stream/-/merge-stream-2.0.0.tgz";
          };
          ident = "merge-stream";
          ltype = "file";
          treeInfo = { };
          version = "2.0.0";
        };
      };
      merge2 = {
        "1.4.1" = {
          fetchInfo = {
            narHash = "sha256-EzedluwbDyO4GYNtgb6NskqXg5w/gF/jdYO2UNyiUDc=";
            type = "tarball";
            url = "https://registry.npmjs.org/merge2/-/merge2-1.4.1.tgz";
          };
          ident = "merge2";
          ltype = "file";
          treeInfo = { };
          version = "1.4.1";
        };
      };
      micromatch = {
        "4.0.5" = {
          depInfo = {
            braces = {
              descriptor = "^3.0.2";
              pin = "3.0.2";
              runtime = true;
            };
            picomatch = {
              descriptor = "^2.3.1";
              pin = "2.3.1";
              runtime = true;
            };
          };
          fetchInfo = {
            narHash = "sha256-5sy/ExTbi9X3zWFTVMx8cfbQCpl3Kyqc7RVqcpj11gg=";
            type = "tarball";
            url = "https://registry.npmjs.org/micromatch/-/micromatch-4.0.5.tgz";
          };
          ident = "micromatch";
          ltype = "file";
          version = "4.0.5";
        };
      };
      mime-db = {
        "1.52.0" = {
          fetchInfo = {
            narHash = "sha256-NWkhw5USnQpCVdzynhDEG/VbDLOdjy0JtGgopd89jr8=";
            type = "tarball";
            url = "https://registry.npmjs.org/mime-db/-/mime-db-1.52.0.tgz";
          };
          ident = "mime-db";
          ltype = "file";
          treeInfo = { };
          version = "1.52.0";
        };
      };
      mime-types = {
        "2.1.35" = {
          depInfo = {
            mime-db = {
              descriptor = "1.52.0";
              pin = "1.52.0";
              runtime = true;
            };
          };
          fetchInfo = {
            narHash = "sha256-OT0LH+QO5JfJrh7X0Lzsv3l/WurbpxPx/nztSX7DeI8=";
            type = "tarball";
            url = "https://registry.npmjs.org/mime-types/-/mime-types-2.1.35.tgz";
          };
          ident = "mime-types";
          ltype = "file";
          version = "2.1.35";
        };
      };
      mimic-fn = {
        "2.1.0" = {
          fetchInfo = {
            narHash = "sha256-up0po5F914aiPm0fCqnagVNmpVJeMAroQXpYiWZAOn0=";
            type = "tarball";
            url = "https://registry.npmjs.org/mimic-fn/-/mimic-fn-2.1.0.tgz";
          };
          ident = "mimic-fn";
          ltype = "file";
          treeInfo = { };
          version = "2.1.0";
        };
      };
      minimatch = {
        "3.1.2" = {
          depInfo = {
            brace-expansion = {
              descriptor = "^1.1.7";
              pin = "1.1.11";
              runtime = true;
            };
          };
          fetchInfo = {
            narHash = "sha256-lngTO0Bk/Spf3t/zG5/j7C2STufjXWF5DlmKjvj1M8s=";
            type = "tarball";
            url = "https://registry.npmjs.org/minimatch/-/minimatch-3.1.2.tgz";
          };
          ident = "minimatch";
          ltype = "file";
          version = "3.1.2";
        };
      };
      minimist = {
        "1.2.8" = {
          fetchInfo = {
            narHash = "sha256-odj63qvs7TXmqy6XlhjY4qtPK5MUF5SZP4bznCdKSKY=";
            type = "tarball";
            url = "https://registry.npmjs.org/minimist/-/minimist-1.2.8.tgz";
          };
          ident = "minimist";
          ltype = "file";
          treeInfo = { };
          version = "1.2.8";
        };
      };
      ms = {
        "2.1.2" = {
          fetchInfo = {
            narHash = "sha256-Y87ut99BMamY3YJBX3Cj3DvOJWkqW+7MrPm7bLyuT50=";
            type = "tarball";
            url = "https://registry.npmjs.org/ms/-/ms-2.1.2.tgz";
          };
          ident = "ms";
          ltype = "file";
          treeInfo = { };
          version = "2.1.2";
        };
      };
      my-app = {
        "0.1.0" = {
          depInfo = {
            "@emotion/react" = {
              descriptor = "^11.11.1";
              pin = "11.11.1";
              runtime = true;
            };
            "@emotion/styled" = {
              descriptor = "^11.11.0";
              pin = "11.11.0";
              runtime = true;
            };
            "@mui/icons-material" = {
              descriptor = "^5.14.3";
              pin = "5.14.3";
              runtime = true;
            };
            "@mui/material" = {
              descriptor = "^5.14.3";
              pin = "5.14.5";
              runtime = true;
            };
            "@types/node" = {
              descriptor = "20.4.7";
              pin = "20.4.7";
            };
            "@types/react" = {
              descriptor = "18.2.18";
              pin = "18.2.18";
            };
            "@types/react-dom" = {
              descriptor = "18.2.7";
              pin = "18.2.7";
            };
            "@types/w3c-web-usb" = {
              descriptor = "^1.0.6";
              pin = "1.0.6";
            };
            autoprefixer = {
              descriptor = "10.4.14";
              pin = "10.4.14";
              runtime = true;
            };
            axios = {
              descriptor = "^1.4.0";
              pin = "1.4.0";
              runtime = true;
            };
            classnames = {
              descriptor = "^2.3.2";
              pin = "2.3.2";
              runtime = true;
            };
            esbuild = {
              descriptor = "^0.15.18";
              pin = "0.15.18";
            };
            eslint = {
              descriptor = "^8.46.0";
              pin = "8.46.0";
            };
            eslint-config-next = {
              descriptor = "13.4.12";
              pin = "13.4.12";
            };
            eslint-plugin-tailwindcss = {
              descriptor = "^3.13.0";
              pin = "3.13.0";
            };
            hex-rgb = {
              descriptor = "^5.0.0";
              pin = "5.0.0";
              runtime = true;
            };
            next = {
              descriptor = "13.4.12";
              pin = "13.4.12";
              runtime = true;
            };
            orval = {
              descriptor = "^6.17.0";
              pin = "6.17.0";
            };
            postcss = {
              descriptor = "8.4.27";
              pin = "8.4.27";
              runtime = true;
            };
            prettier = {
              descriptor = "^3.0.1";
              pin = "3.0.1";
            };
            prettier-plugin-tailwindcss = {
              descriptor = "^0.4.1";
              pin = "0.4.1";
            };
            react = {
              descriptor = "18.2.0";
              pin = "18.2.0";
              runtime = true;
            };
            react-dom = {
              descriptor = "18.2.0";
              pin = "18.2.0";
              runtime = true;
            };
            react-hook-form = {
              descriptor = "^7.45.4";
              pin = "7.45.4";
              runtime = true;
            };
            react-hot-toast = {
              descriptor = "^2.4.1";
              pin = "2.4.1";
              runtime = true;
            };
            recharts = {
              descriptor = "^2.7.3";
              pin = "2.7.3";
              runtime = true;
            };
            swr = {
              descriptor = "^2.2.1";
              pin = "2.2.1";
              runtime = true;
            };
            tailwindcss = {
              descriptor = "3.3.3";
              pin = "3.3.3";
              runtime = true;
            };
            typescript = {
              descriptor = "5.1.6";
              pin = "5.1.6";
            };
          };
          fetchInfo = "path:..";
          ident = "my-app";
          lifecycle = {
            build = true;
          };
          ltype = "dir";
          treeInfo = {
            "node_modules/@aashutoshrathi/word-wrap" = {
              dev = true;
              key = "@aashutoshrathi/word-wrap/1.2.6";
            };
            "node_modules/@alloc/quick-lru" = {
              key = "@alloc/quick-lru/5.2.0";
            };
            "node_modules/@apidevtools/json-schema-ref-parser" = {
              dev = true;
              key = "@apidevtools/json-schema-ref-parser/9.0.6";
            };
            "node_modules/@apidevtools/json-schema-ref-parser/node_modules/argparse" = {
              dev = true;
              key = "argparse/1.0.10";
            };
            "node_modules/@apidevtools/json-schema-ref-parser/node_modules/js-yaml" = {
              dev = true;
              key = "js-yaml/3.14.1";
            };
            "node_modules/@apidevtools/openapi-schemas" = {
              dev = true;
              key = "@apidevtools/openapi-schemas/2.1.0";
            };
            "node_modules/@apidevtools/swagger-methods" = {
              dev = true;
              key = "@apidevtools/swagger-methods/3.0.2";
            };
            "node_modules/@apidevtools/swagger-parser" = {
              dev = true;
              key = "@apidevtools/swagger-parser/10.1.0";
            };
            "node_modules/@apidevtools/swagger-parser/node_modules/ajv" = {
              dev = true;
              key = "ajv/8.12.0";
            };
            "node_modules/@apidevtools/swagger-parser/node_modules/ajv-draft-04" = {
              dev = true;
              key = "ajv-draft-04/1.0.0";
            };
            "node_modules/@apidevtools/swagger-parser/node_modules/json-schema-traverse" = {
              dev = true;
              key = "json-schema-traverse/1.0.0";
            };
            "node_modules/@asyncapi/specs" = {
              dev = true;
              key = "@asyncapi/specs/4.3.1";
            };
            "node_modules/@babel/code-frame" = {
              key = "@babel/code-frame/7.22.10";
            };
            "node_modules/@babel/code-frame/node_modules/ansi-styles" = {
              key = "ansi-styles/3.2.1";
            };
            "node_modules/@babel/code-frame/node_modules/chalk" = {
              key = "chalk/2.4.2";
            };
            "node_modules/@babel/code-frame/node_modules/color-convert" = {
              key = "color-convert/1.9.3";
            };
            "node_modules/@babel/code-frame/node_modules/color-name" = {
              key = "color-name/1.1.3";
            };
            "node_modules/@babel/code-frame/node_modules/escape-string-regexp" = {
              key = "escape-string-regexp/1.0.5";
            };
            "node_modules/@babel/code-frame/node_modules/has-flag" = {
              key = "has-flag/3.0.0";
            };
            "node_modules/@babel/code-frame/node_modules/supports-color" = {
              key = "supports-color/5.5.0";
            };
            "node_modules/@babel/helper-module-imports" = {
              key = "@babel/helper-module-imports/7.22.5";
            };
            "node_modules/@babel/helper-string-parser" = {
              key = "@babel/helper-string-parser/7.22.5";
            };
            "node_modules/@babel/helper-validator-identifier" = {
              key = "@babel/helper-validator-identifier/7.22.5";
            };
            "node_modules/@babel/highlight" = {
              key = "@babel/highlight/7.22.10";
            };
            "node_modules/@babel/highlight/node_modules/ansi-styles" = {
              key = "ansi-styles/3.2.1";
            };
            "node_modules/@babel/highlight/node_modules/chalk" = {
              key = "chalk/2.4.2";
            };
            "node_modules/@babel/highlight/node_modules/color-convert" = {
              key = "color-convert/1.9.3";
            };
            "node_modules/@babel/highlight/node_modules/color-name" = {
              key = "color-name/1.1.3";
            };
            "node_modules/@babel/highlight/node_modules/escape-string-regexp" = {
              key = "escape-string-regexp/1.0.5";
            };
            "node_modules/@babel/highlight/node_modules/has-flag" = {
              key = "has-flag/3.0.0";
            };
            "node_modules/@babel/highlight/node_modules/supports-color" = {
              key = "supports-color/5.5.0";
            };
            "node_modules/@babel/runtime" = {
              key = "@babel/runtime/7.22.10";
            };
            "node_modules/@babel/types" = {
              key = "@babel/types/7.22.10";
            };
            "node_modules/@emotion/babel-plugin" = {
              key = "@emotion/babel-plugin/11.11.0";
            };
            "node_modules/@emotion/cache" = {
              key = "@emotion/cache/11.11.0";
            };
            "node_modules/@emotion/hash" = {
              key = "@emotion/hash/0.9.1";
            };
            "node_modules/@emotion/is-prop-valid" = {
              key = "@emotion/is-prop-valid/1.2.1";
            };
            "node_modules/@emotion/memoize" = {
              key = "@emotion/memoize/0.8.1";
            };
            "node_modules/@emotion/react" = {
              key = "@emotion/react/11.11.1";
            };
            "node_modules/@emotion/serialize" = {
              key = "@emotion/serialize/1.1.2";
            };
            "node_modules/@emotion/sheet" = {
              key = "@emotion/sheet/1.2.2";
            };
            "node_modules/@emotion/styled" = {
              key = "@emotion/styled/11.11.0";
            };
            "node_modules/@emotion/unitless" = {
              key = "@emotion/unitless/0.8.1";
            };
            "node_modules/@emotion/use-insertion-effect-with-fallbacks" = {
              key = "@emotion/use-insertion-effect-with-fallbacks/1.0.1";
            };
            "node_modules/@emotion/utils" = {
              key = "@emotion/utils/1.2.1";
            };
            "node_modules/@emotion/weak-memoize" = {
              key = "@emotion/weak-memoize/0.3.1";
            };
            "node_modules/@esbuild/android-arm" = {
              dev = true;
              key = "@esbuild/android-arm/0.15.18";
              optional = true;
            };
            "node_modules/@esbuild/linux-loong64" = {
              dev = true;
              key = "@esbuild/linux-loong64/0.15.18";
              optional = true;
            };
            "node_modules/@eslint-community/eslint-utils" = {
              dev = true;
              key = "@eslint-community/eslint-utils/4.4.0";
            };
            "node_modules/@eslint-community/regexpp" = {
              dev = true;
              key = "@eslint-community/regexpp/4.6.2";
            };
            "node_modules/@eslint/eslintrc" = {
              dev = true;
              key = "@eslint/eslintrc/2.1.2";
            };
            "node_modules/@eslint/js" = {
              dev = true;
              key = "@eslint/js/8.47.0";
            };
            "node_modules/@exodus/schemasafe" = {
              dev = true;
              key = "@exodus/schemasafe/1.2.4";
            };
            "node_modules/@humanwhocodes/config-array" = {
              dev = true;
              key = "@humanwhocodes/config-array/0.11.10";
            };
            "node_modules/@humanwhocodes/module-importer" = {
              dev = true;
              key = "@humanwhocodes/module-importer/1.0.1";
            };
            "node_modules/@humanwhocodes/object-schema" = {
              dev = true;
              key = "@humanwhocodes/object-schema/1.2.1";
            };
            "node_modules/@ibm-cloud/openapi-ruleset" = {
              dev = true;
              key = "@ibm-cloud/openapi-ruleset/0.45.5";
            };
            "node_modules/@ibm-cloud/openapi-ruleset-utilities" = {
              dev = true;
              key = "@ibm-cloud/openapi-ruleset-utilities/0.0.1";
            };
            "node_modules/@jridgewell/gen-mapping" = {
              key = "@jridgewell/gen-mapping/0.3.3";
            };
            "node_modules/@jridgewell/resolve-uri" = {
              key = "@jridgewell/resolve-uri/3.1.1";
            };
            "node_modules/@jridgewell/set-array" = {
              key = "@jridgewell/set-array/1.1.2";
            };
            "node_modules/@jridgewell/sourcemap-codec" = {
              key = "@jridgewell/sourcemap-codec/1.4.15";
            };
            "node_modules/@jridgewell/trace-mapping" = {
              key = "@jridgewell/trace-mapping/0.3.19";
            };
            "node_modules/@jsdevtools/ono" = {
              dev = true;
              key = "@jsdevtools/ono/7.1.3";
            };
            "node_modules/@jsep-plugin/regex" = {
              dev = true;
              key = "@jsep-plugin/regex/1.0.3";
            };
            "node_modules/@jsep-plugin/ternary" = {
              dev = true;
              key = "@jsep-plugin/ternary/1.1.3";
            };
            "node_modules/@mui/base" = {
              key = "@mui/base/5.0.0-beta.11";
            };
            "node_modules/@mui/core-downloads-tracker" = {
              key = "@mui/core-downloads-tracker/5.14.5";
            };
            "node_modules/@mui/icons-material" = {
              key = "@mui/icons-material/5.14.3";
            };
            "node_modules/@mui/material" = {
              key = "@mui/material/5.14.5";
            };
            "node_modules/@mui/private-theming" = {
              key = "@mui/private-theming/5.14.5";
            };
            "node_modules/@mui/styled-engine" = {
              key = "@mui/styled-engine/5.13.2";
            };
            "node_modules/@mui/system" = {
              key = "@mui/system/5.14.5";
            };
            "node_modules/@mui/types" = {
              key = "@mui/types/7.2.4";
            };
            "node_modules/@mui/utils" = {
              key = "@mui/utils/5.14.5";
            };
            "node_modules/@next/env" = {
              key = "@next/env/13.4.12";
            };
            "node_modules/@next/eslint-plugin-next" = {
              dev = true;
              key = "@next/eslint-plugin-next/13.4.12";
            };
            "node_modules/@next/swc-darwin-arm64" = {
              key = "@next/swc-darwin-arm64/13.4.12";
              optional = true;
            };
            "node_modules/@next/swc-darwin-x64" = {
              key = "@next/swc-darwin-x64/13.4.12";
              optional = true;
            };
            "node_modules/@next/swc-linux-arm64-gnu" = {
              key = "@next/swc-linux-arm64-gnu/13.4.12";
              optional = true;
            };
            "node_modules/@next/swc-linux-arm64-musl" = {
              key = "@next/swc-linux-arm64-musl/13.4.12";
              optional = true;
            };
            "node_modules/@next/swc-linux-x64-gnu" = {
              key = "@next/swc-linux-x64-gnu/13.4.12";
              optional = true;
            };
            "node_modules/@next/swc-linux-x64-musl" = {
              key = "@next/swc-linux-x64-musl/13.4.12";
              optional = true;
            };
            "node_modules/@next/swc-win32-arm64-msvc" = {
              key = "@next/swc-win32-arm64-msvc/13.4.12";
              optional = true;
            };
            "node_modules/@next/swc-win32-ia32-msvc" = {
              key = "@next/swc-win32-ia32-msvc/13.4.12";
              optional = true;
            };
            "node_modules/@next/swc-win32-x64-msvc" = {
              key = "@next/swc-win32-x64-msvc/13.4.12";
              optional = true;
            };
            "node_modules/@nodelib/fs.scandir" = {
              key = "@nodelib/fs.scandir/2.1.5";
            };
            "node_modules/@nodelib/fs.stat" = {
              key = "@nodelib/fs.stat/2.0.5";
            };
            "node_modules/@nodelib/fs.walk" = {
              key = "@nodelib/fs.walk/1.2.8";
            };
            "node_modules/@orval/angular" = {
              dev = true;
              key = "@orval/angular/6.17.0";
            };
            "node_modules/@orval/axios" = {
              dev = true;
              key = "@orval/axios/6.17.0";
            };
            "node_modules/@orval/core" = {
              dev = true;
              key = "@orval/core/6.17.0";
            };
            "node_modules/@orval/core/node_modules/ajv" = {
              dev = true;
              key = "ajv/8.12.0";
            };
            "node_modules/@orval/core/node_modules/json-schema-traverse" = {
              dev = true;
              key = "json-schema-traverse/1.0.0";
            };
            "node_modules/@orval/msw" = {
              dev = true;
              key = "@orval/msw/6.17.0";
            };
            "node_modules/@orval/query" = {
              dev = true;
              key = "@orval/query/6.17.0";
            };
            "node_modules/@orval/swr" = {
              dev = true;
              key = "@orval/swr/6.17.0";
            };
            "node_modules/@orval/zod" = {
              dev = true;
              key = "@orval/zod/6.17.0";
            };
            "node_modules/@popperjs/core" = {
              key = "@popperjs/core/2.11.8";
            };
            "node_modules/@rollup/plugin-commonjs" = {
              dev = true;
              key = "@rollup/plugin-commonjs/22.0.2";
            };
            "node_modules/@rollup/pluginutils" = {
              dev = true;
              key = "@rollup/pluginutils/3.1.0";
            };
            "node_modules/@rollup/pluginutils/node_modules/estree-walker" = {
              dev = true;
              key = "estree-walker/1.0.1";
            };
            "node_modules/@rushstack/eslint-patch" = {
              dev = true;
              key = "@rushstack/eslint-patch/1.3.3";
            };
            "node_modules/@stoplight/json" = {
              dev = true;
              key = "@stoplight/json/3.21.0";
            };
            "node_modules/@stoplight/json-ref-readers" = {
              dev = true;
              key = "@stoplight/json-ref-readers/1.2.2";
            };
            "node_modules/@stoplight/json-ref-readers/node_modules/tslib" = {
              dev = true;
              key = "tslib/1.14.1";
            };
            "node_modules/@stoplight/json-ref-resolver" = {
              dev = true;
              key = "@stoplight/json-ref-resolver/3.1.6";
            };
            "node_modules/@stoplight/ordered-object-literal" = {
              dev = true;
              key = "@stoplight/ordered-object-literal/1.0.4";
            };
            "node_modules/@stoplight/path" = {
              dev = true;
              key = "@stoplight/path/1.3.2";
            };
            "node_modules/@stoplight/spectral-cli" = {
              dev = true;
              key = "@stoplight/spectral-cli/6.10.1";
            };
            "node_modules/@stoplight/spectral-cli/node_modules/fast-glob" = {
              dev = true;
              key = "fast-glob/3.2.12";
            };
            "node_modules/@stoplight/spectral-cli/node_modules/glob-parent" = {
              dev = true;
              key = "glob-parent/5.1.2";
            };
            "node_modules/@stoplight/spectral-core" = {
              dev = true;
              key = "@stoplight/spectral-core/1.18.3";
            };
            "node_modules/@stoplight/spectral-core/node_modules/@stoplight/better-ajv-errors" = {
              dev = true;
              key = "@stoplight/better-ajv-errors/1.0.3";
            };
            "node_modules/@stoplight/spectral-core/node_modules/@stoplight/types" = {
              dev = true;
              key = "@stoplight/types/13.6.0";
            };
            "node_modules/@stoplight/spectral-core/node_modules/ajv" = {
              dev = true;
              key = "ajv/8.12.0";
            };
            "node_modules/@stoplight/spectral-core/node_modules/ajv-errors" = {
              dev = true;
              key = "ajv-errors/3.0.0";
            };
            "node_modules/@stoplight/spectral-core/node_modules/json-schema-traverse" = {
              dev = true;
              key = "json-schema-traverse/1.0.0";
            };
            "node_modules/@stoplight/spectral-formats" = {
              dev = true;
              key = "@stoplight/spectral-formats/1.5.0";
            };
            "node_modules/@stoplight/spectral-formatters" = {
              dev = true;
              key = "@stoplight/spectral-formatters/1.2.0";
            };
            "node_modules/@stoplight/spectral-functions" = {
              dev = true;
              key = "@stoplight/spectral-functions/1.7.2";
            };
            "node_modules/@stoplight/spectral-functions/node_modules/@stoplight/better-ajv-errors" = {
              dev = true;
              key = "@stoplight/better-ajv-errors/1.0.3";
            };
            "node_modules/@stoplight/spectral-functions/node_modules/ajv" = {
              dev = true;
              key = "ajv/8.12.0";
            };
            "node_modules/@stoplight/spectral-functions/node_modules/ajv-draft-04" = {
              dev = true;
              key = "ajv-draft-04/1.0.0";
            };
            "node_modules/@stoplight/spectral-functions/node_modules/ajv-errors" = {
              dev = true;
              key = "ajv-errors/3.0.0";
            };
            "node_modules/@stoplight/spectral-functions/node_modules/json-schema-traverse" = {
              dev = true;
              key = "json-schema-traverse/1.0.0";
            };
            "node_modules/@stoplight/spectral-parsers" = {
              dev = true;
              key = "@stoplight/spectral-parsers/1.0.3";
            };
            "node_modules/@stoplight/spectral-ref-resolver" = {
              dev = true;
              key = "@stoplight/spectral-ref-resolver/1.0.4";
            };
            "node_modules/@stoplight/spectral-ruleset-bundler" = {
              dev = true;
              key = "@stoplight/spectral-ruleset-bundler/1.5.2";
            };
            "node_modules/@stoplight/spectral-ruleset-migrator" = {
              dev = true;
              key = "@stoplight/spectral-ruleset-migrator/1.9.5";
            };
            "node_modules/@stoplight/spectral-ruleset-migrator/node_modules/ajv" = {
              dev = true;
              key = "ajv/8.12.0";
            };
            "node_modules/@stoplight/spectral-ruleset-migrator/node_modules/json-schema-traverse" = {
              dev = true;
              key = "json-schema-traverse/1.0.0";
            };
            "node_modules/@stoplight/spectral-rulesets" = {
              dev = true;
              key = "@stoplight/spectral-rulesets/1.16.0";
            };
            "node_modules/@stoplight/spectral-rulesets/node_modules/@stoplight/better-ajv-errors" = {
              dev = true;
              key = "@stoplight/better-ajv-errors/1.0.3";
            };
            "node_modules/@stoplight/spectral-rulesets/node_modules/ajv" = {
              dev = true;
              key = "ajv/8.12.0";
            };
            "node_modules/@stoplight/spectral-rulesets/node_modules/json-schema-traverse" = {
              dev = true;
              key = "json-schema-traverse/1.0.0";
            };
            "node_modules/@stoplight/spectral-runtime" = {
              dev = true;
              key = "@stoplight/spectral-runtime/1.1.2";
            };
            "node_modules/@stoplight/spectral-runtime/node_modules/@stoplight/types" = {
              dev = true;
              key = "@stoplight/types/12.5.0";
            };
            "node_modules/@stoplight/types" = {
              dev = true;
              key = "@stoplight/types/13.19.0";
            };
            "node_modules/@stoplight/yaml" = {
              dev = true;
              key = "@stoplight/yaml/4.2.3";
            };
            "node_modules/@stoplight/yaml-ast-parser" = {
              dev = true;
              key = "@stoplight/yaml-ast-parser/0.0.48";
            };
            "node_modules/@swc/helpers" = {
              key = "@swc/helpers/0.5.1";
            };
            "node_modules/@types/d3-array" = {
              key = "@types/d3-array/3.0.5";
            };
            "node_modules/@types/d3-color" = {
              key = "@types/d3-color/3.1.0";
            };
            "node_modules/@types/d3-ease" = {
              key = "@types/d3-ease/3.0.0";
            };
            "node_modules/@types/d3-interpolate" = {
              key = "@types/d3-interpolate/3.0.1";
            };
            "node_modules/@types/d3-path" = {
              key = "@types/d3-path/3.0.0";
            };
            "node_modules/@types/d3-scale" = {
              key = "@types/d3-scale/4.0.3";
            };
            "node_modules/@types/d3-shape" = {
              key = "@types/d3-shape/3.1.1";
            };
            "node_modules/@types/d3-time" = {
              key = "@types/d3-time/3.0.0";
            };
            "node_modules/@types/d3-timer" = {
              key = "@types/d3-timer/3.0.0";
            };
            "node_modules/@types/es-aggregate-error" = {
              dev = true;
              key = "@types/es-aggregate-error/1.0.2";
            };
            "node_modules/@types/estree" = {
              dev = true;
              key = "@types/estree/0.0.39";
            };
            "node_modules/@types/json-schema" = {
              dev = true;
              key = "@types/json-schema/7.0.12";
            };
            "node_modules/@types/json5" = {
              dev = true;
              key = "@types/json5/0.0.29";
            };
            "node_modules/@types/node" = {
              dev = true;
              key = "@types/node/20.4.7";
            };
            "node_modules/@types/parse-json" = {
              key = "@types/parse-json/4.0.0";
            };
            "node_modules/@types/prop-types" = {
              key = "@types/prop-types/15.7.5";
            };
            "node_modules/@types/react" = {
              key = "@types/react/18.2.18";
            };
            "node_modules/@types/react-dom" = {
              dev = true;
              key = "@types/react-dom/18.2.7";
            };
            "node_modules/@types/react-is" = {
              key = "@types/react-is/18.2.1";
            };
            "node_modules/@types/react-transition-group" = {
              key = "@types/react-transition-group/4.4.6";
            };
            "node_modules/@types/scheduler" = {
              key = "@types/scheduler/0.16.3";
            };
            "node_modules/@types/urijs" = {
              dev = true;
              key = "@types/urijs/1.19.19";
            };
            "node_modules/@types/w3c-web-usb" = {
              dev = true;
              key = "@types/w3c-web-usb/1.0.6";
            };
            "node_modules/@typescript-eslint/parser" = {
              dev = true;
              key = "@typescript-eslint/parser/5.62.0";
            };
            "node_modules/@typescript-eslint/scope-manager" = {
              dev = true;
              key = "@typescript-eslint/scope-manager/5.62.0";
            };
            "node_modules/@typescript-eslint/types" = {
              dev = true;
              key = "@typescript-eslint/types/5.62.0";
            };
            "node_modules/@typescript-eslint/typescript-estree" = {
              dev = true;
              key = "@typescript-eslint/typescript-estree/5.62.0";
            };
            "node_modules/@typescript-eslint/visitor-keys" = {
              dev = true;
              key = "@typescript-eslint/visitor-keys/5.62.0";
            };
            "node_modules/abort-controller" = {
              dev = true;
              key = "abort-controller/3.0.0";
            };
            "node_modules/acorn" = {
              dev = true;
              key = "acorn/8.10.0";
            };
            "node_modules/acorn-jsx" = {
              dev = true;
              key = "acorn-jsx/5.3.2";
            };
            "node_modules/ajv" = {
              dev = true;
              key = "ajv/6.12.6";
            };
            "node_modules/ajv-formats" = {
              dev = true;
              key = "ajv-formats/2.1.1";
            };
            "node_modules/ajv-formats/node_modules/ajv" = {
              dev = true;
              key = "ajv/8.12.0";
            };
            "node_modules/ajv-formats/node_modules/json-schema-traverse" = {
              dev = true;
              key = "json-schema-traverse/1.0.0";
            };
            "node_modules/ansi-colors" = {
              dev = true;
              key = "ansi-colors/4.1.3";
            };
            "node_modules/ansi-regex" = {
              dev = true;
              key = "ansi-regex/5.0.1";
            };
            "node_modules/ansi-styles" = {
              dev = true;
              key = "ansi-styles/4.3.0";
            };
            "node_modules/any-promise" = {
              key = "any-promise/1.3.0";
            };
            "node_modules/anymatch" = {
              key = "anymatch/3.1.3";
            };
            "node_modules/arg" = {
              key = "arg/5.0.2";
            };
            "node_modules/argparse" = {
              dev = true;
              key = "argparse/2.0.1";
            };
            "node_modules/aria-query" = {
              dev = true;
              key = "aria-query/5.3.0";
            };
            "node_modules/array-buffer-byte-length" = {
              dev = true;
              key = "array-buffer-byte-length/1.0.0";
            };
            "node_modules/array-includes" = {
              dev = true;
              key = "array-includes/3.1.6";
            };
            "node_modules/array-union" = {
              dev = true;
              key = "array-union/2.1.0";
            };
            "node_modules/array.prototype.findlastindex" = {
              dev = true;
              key = "array.prototype.findlastindex/1.2.2";
            };
            "node_modules/array.prototype.flat" = {
              dev = true;
              key = "array.prototype.flat/1.3.1";
            };
            "node_modules/array.prototype.flatmap" = {
              dev = true;
              key = "array.prototype.flatmap/1.3.1";
            };
            "node_modules/array.prototype.tosorted" = {
              dev = true;
              key = "array.prototype.tosorted/1.1.1";
            };
            "node_modules/arraybuffer.prototype.slice" = {
              dev = true;
              key = "arraybuffer.prototype.slice/1.0.1";
            };
            "node_modules/as-table" = {
              dev = true;
              key = "as-table/1.0.55";
            };
            "node_modules/ast-types" = {
              dev = true;
              key = "ast-types/0.14.2";
            };
            "node_modules/ast-types-flow" = {
              dev = true;
              key = "ast-types-flow/0.0.7";
            };
            "node_modules/astring" = {
              dev = true;
              key = "astring/1.8.6";
            };
            "node_modules/asynckit" = {
              key = "asynckit/0.4.0";
            };
            "node_modules/autoprefixer" = {
              key = "autoprefixer/10.4.14";
            };
            "node_modules/available-typed-arrays" = {
              dev = true;
              key = "available-typed-arrays/1.0.5";
            };
            "node_modules/axe-core" = {
              dev = true;
              key = "axe-core/4.7.2";
            };
            "node_modules/axios" = {
              key = "axios/1.4.0";
            };
            "node_modules/axobject-query" = {
              dev = true;
              key = "axobject-query/3.2.1";
            };
            "node_modules/babel-plugin-macros" = {
              key = "babel-plugin-macros/3.1.0";
            };
            "node_modules/backslash" = {
              dev = true;
              key = "backslash/0.2.0";
            };
            "node_modules/balanced-match" = {
              key = "balanced-match/1.0.2";
            };
            "node_modules/binary-extensions" = {
              key = "binary-extensions/2.2.0";
            };
            "node_modules/brace-expansion" = {
              key = "brace-expansion/1.1.11";
            };
            "node_modules/braces" = {
              key = "braces/3.0.2";
            };
            "node_modules/browserslist" = {
              key = "browserslist/4.21.10";
            };
            "node_modules/builtins" = {
              dev = true;
              key = "builtins/1.0.3";
            };
            "node_modules/busboy" = {
              key = "busboy/1.6.0";
            };
            "node_modules/cac" = {
              dev = true;
              key = "cac/6.7.14";
            };
            "node_modules/call-bind" = {
              dev = true;
              key = "call-bind/1.0.2";
            };
            "node_modules/call-me-maybe" = {
              dev = true;
              key = "call-me-maybe/1.0.2";
            };
            "node_modules/callsites" = {
              key = "callsites/3.1.0";
            };
            "node_modules/camelcase-css" = {
              key = "camelcase-css/2.0.1";
            };
            "node_modules/caniuse-lite" = {
              key = "caniuse-lite/1.0.30001520";
            };
            "node_modules/chalk" = {
              dev = true;
              key = "chalk/4.1.2";
            };
            "node_modules/chokidar" = {
              key = "chokidar/3.5.3";
            };
            "node_modules/chokidar/node_modules/glob-parent" = {
              key = "glob-parent/5.1.2";
            };
            "node_modules/classnames" = {
              key = "classnames/2.3.2";
            };
            "node_modules/client-only" = {
              key = "client-only/0.0.1";
            };
            "node_modules/cliui" = {
              dev = true;
              key = "cliui/7.0.4";
            };
            "node_modules/clone" = {
              dev = true;
              key = "clone/1.0.4";
            };
            "node_modules/clsx" = {
              key = "clsx/2.0.0";
            };
            "node_modules/color-convert" = {
              dev = true;
              key = "color-convert/2.0.1";
            };
            "node_modules/color-name" = {
              dev = true;
              key = "color-name/1.1.4";
            };
            "node_modules/combined-stream" = {
              key = "combined-stream/1.0.8";
            };
            "node_modules/commander" = {
              key = "commander/4.1.1";
            };
            "node_modules/commondir" = {
              dev = true;
              key = "commondir/1.0.1";
            };
            "node_modules/compare-versions" = {
              dev = true;
              key = "compare-versions/4.1.4";
            };
            "node_modules/concat-map" = {
              key = "concat-map/0.0.1";
            };
            "node_modules/convert-source-map" = {
              key = "convert-source-map/1.9.0";
            };
            "node_modules/cosmiconfig" = {
              key = "cosmiconfig/7.1.0";
            };
            "node_modules/cross-spawn" = {
              dev = true;
              key = "cross-spawn/7.0.3";
            };
            "node_modules/css-unit-converter" = {
              key = "css-unit-converter/1.1.2";
            };
            "node_modules/cssesc" = {
              key = "cssesc/3.0.0";
            };
            "node_modules/csstype" = {
              key = "csstype/3.1.2";
            };
            "node_modules/cuid" = {
              dev = true;
              key = "cuid/2.1.8";
            };
            "node_modules/d3-array" = {
              key = "d3-array/3.2.4";
            };
            "node_modules/d3-color" = {
              key = "d3-color/3.1.0";
            };
            "node_modules/d3-ease" = {
              key = "d3-ease/3.0.1";
            };
            "node_modules/d3-format" = {
              key = "d3-format/3.1.0";
            };
            "node_modules/d3-interpolate" = {
              key = "d3-interpolate/3.0.1";
            };
            "node_modules/d3-path" = {
              key = "d3-path/3.1.0";
            };
            "node_modules/d3-scale" = {
              key = "d3-scale/4.0.2";
            };
            "node_modules/d3-shape" = {
              key = "d3-shape/3.2.0";
            };
            "node_modules/d3-time" = {
              key = "d3-time/3.1.0";
            };
            "node_modules/d3-time-format" = {
              key = "d3-time-format/4.1.0";
            };
            "node_modules/d3-timer" = {
              key = "d3-timer/3.0.1";
            };
            "node_modules/damerau-levenshtein" = {
              dev = true;
              key = "damerau-levenshtein/1.0.8";
            };
            "node_modules/data-uri-to-buffer" = {
              dev = true;
              key = "data-uri-to-buffer/2.0.2";
            };
            "node_modules/debug" = {
              dev = true;
              key = "debug/4.3.4";
            };
            "node_modules/decimal.js-light" = {
              key = "decimal.js-light/2.5.1";
            };
            "node_modules/deep-is" = {
              dev = true;
              key = "deep-is/0.1.4";
            };
            "node_modules/deepmerge" = {
              dev = true;
              key = "deepmerge/2.2.1";
            };
            "node_modules/defaults" = {
              dev = true;
              key = "defaults/1.0.4";
            };
            "node_modules/define-properties" = {
              dev = true;
              key = "define-properties/1.2.0";
            };
            "node_modules/delayed-stream" = {
              key = "delayed-stream/1.0.0";
            };
            "node_modules/dependency-graph" = {
              dev = true;
              key = "dependency-graph/0.11.0";
            };
            "node_modules/dequal" = {
              dev = true;
              key = "dequal/2.0.3";
            };
            "node_modules/didyoumean" = {
              key = "didyoumean/1.2.2";
            };
            "node_modules/dir-glob" = {
              dev = true;
              key = "dir-glob/3.0.1";
            };
            "node_modules/dlv" = {
              key = "dlv/1.1.3";
            };
            "node_modules/doctrine" = {
              dev = true;
              key = "doctrine/3.0.0";
            };
            "node_modules/dom-helpers" = {
              key = "dom-helpers/5.2.1";
            };
            "node_modules/electron-to-chromium" = {
              key = "electron-to-chromium/1.4.491";
            };
            "node_modules/emoji-regex" = {
              dev = true;
              key = "emoji-regex/9.2.2";
            };
            "node_modules/enhanced-resolve" = {
              dev = true;
              key = "enhanced-resolve/5.15.0";
            };
            "node_modules/enquirer" = {
              dev = true;
              key = "enquirer/2.4.1";
            };
            "node_modules/error-ex" = {
              key = "error-ex/1.3.2";
            };
            "node_modules/es-abstract" = {
              dev = true;
              key = "es-abstract/1.22.1";
            };
            "node_modules/es-aggregate-error" = {
              dev = true;
              key = "es-aggregate-error/1.0.9";
            };
            "node_modules/es-set-tostringtag" = {
              dev = true;
              key = "es-set-tostringtag/2.0.1";
            };
            "node_modules/es-shim-unscopables" = {
              dev = true;
              key = "es-shim-unscopables/1.0.0";
            };
            "node_modules/es-to-primitive" = {
              dev = true;
              key = "es-to-primitive/1.2.1";
            };
            "node_modules/es6-promise" = {
              dev = true;
              key = "es6-promise/3.3.1";
            };
            "node_modules/esbuild" = {
              dev = true;
              key = "esbuild/0.15.18";
            };
            "node_modules/esbuild-android-64" = {
              dev = true;
              key = "esbuild-android-64/0.15.18";
              optional = true;
            };
            "node_modules/esbuild-android-arm64" = {
              dev = true;
              key = "esbuild-android-arm64/0.15.18";
              optional = true;
            };
            "node_modules/esbuild-darwin-64" = {
              dev = true;
              key = "esbuild-darwin-64/0.15.18";
              optional = true;
            };
            "node_modules/esbuild-darwin-arm64" = {
              dev = true;
              key = "esbuild-darwin-arm64/0.15.18";
              optional = true;
            };
            "node_modules/esbuild-freebsd-64" = {
              dev = true;
              key = "esbuild-freebsd-64/0.15.18";
              optional = true;
            };
            "node_modules/esbuild-freebsd-arm64" = {
              dev = true;
              key = "esbuild-freebsd-arm64/0.15.18";
              optional = true;
            };
            "node_modules/esbuild-linux-32" = {
              dev = true;
              key = "esbuild-linux-32/0.15.18";
              optional = true;
            };
            "node_modules/esbuild-linux-64" = {
              dev = true;
              key = "esbuild-linux-64/0.15.18";
              optional = true;
            };
            "node_modules/esbuild-linux-arm" = {
              dev = true;
              key = "esbuild-linux-arm/0.15.18";
              optional = true;
            };
            "node_modules/esbuild-linux-arm64" = {
              dev = true;
              key = "esbuild-linux-arm64/0.15.18";
              optional = true;
            };
            "node_modules/esbuild-linux-mips64le" = {
              dev = true;
              key = "esbuild-linux-mips64le/0.15.18";
              optional = true;
            };
            "node_modules/esbuild-linux-ppc64le" = {
              dev = true;
              key = "esbuild-linux-ppc64le/0.15.18";
              optional = true;
            };
            "node_modules/esbuild-linux-riscv64" = {
              dev = true;
              key = "esbuild-linux-riscv64/0.15.18";
              optional = true;
            };
            "node_modules/esbuild-linux-s390x" = {
              dev = true;
              key = "esbuild-linux-s390x/0.15.18";
              optional = true;
            };
            "node_modules/esbuild-netbsd-64" = {
              dev = true;
              key = "esbuild-netbsd-64/0.15.18";
              optional = true;
            };
            "node_modules/esbuild-openbsd-64" = {
              dev = true;
              key = "esbuild-openbsd-64/0.15.18";
              optional = true;
            };
            "node_modules/esbuild-sunos-64" = {
              dev = true;
              key = "esbuild-sunos-64/0.15.18";
              optional = true;
            };
            "node_modules/esbuild-windows-32" = {
              dev = true;
              key = "esbuild-windows-32/0.15.18";
              optional = true;
            };
            "node_modules/esbuild-windows-64" = {
              dev = true;
              key = "esbuild-windows-64/0.15.18";
              optional = true;
            };
            "node_modules/esbuild-windows-arm64" = {
              dev = true;
              key = "esbuild-windows-arm64/0.15.18";
              optional = true;
            };
            "node_modules/escalade" = {
              key = "escalade/3.1.1";
            };
            "node_modules/escape-string-regexp" = {
              key = "escape-string-regexp/4.0.0";
            };
            "node_modules/eslint" = {
              dev = true;
              key = "eslint/8.46.0";
            };
            "node_modules/eslint-config-next" = {
              dev = true;
              key = "eslint-config-next/13.4.12";
            };
            "node_modules/eslint-import-resolver-node" = {
              dev = true;
              key = "eslint-import-resolver-node/0.3.9";
            };
            "node_modules/eslint-import-resolver-node/node_modules/debug" = {
              dev = true;
              key = "debug/3.2.7";
            };
            "node_modules/eslint-import-resolver-typescript" = {
              dev = true;
              key = "eslint-import-resolver-typescript/3.6.0";
            };
            "node_modules/eslint-module-utils" = {
              dev = true;
              key = "eslint-module-utils/2.8.0";
            };
            "node_modules/eslint-module-utils/node_modules/debug" = {
              dev = true;
              key = "debug/3.2.7";
            };
            "node_modules/eslint-plugin-import" = {
              dev = true;
              key = "eslint-plugin-import/2.28.0";
            };
            "node_modules/eslint-plugin-import/node_modules/debug" = {
              dev = true;
              key = "debug/3.2.7";
            };
            "node_modules/eslint-plugin-import/node_modules/doctrine" = {
              dev = true;
              key = "doctrine/2.1.0";
            };
            "node_modules/eslint-plugin-import/node_modules/semver" = {
              dev = true;
              key = "semver/6.3.1";
            };
            "node_modules/eslint-plugin-jsx-a11y" = {
              dev = true;
              key = "eslint-plugin-jsx-a11y/6.7.1";
            };
            "node_modules/eslint-plugin-jsx-a11y/node_modules/semver" = {
              dev = true;
              key = "semver/6.3.1";
            };
            "node_modules/eslint-plugin-react" = {
              dev = true;
              key = "eslint-plugin-react/7.33.1";
            };
            "node_modules/eslint-plugin-react-hooks" = {
              dev = true;
              key = "eslint-plugin-react-hooks/5.0.0-canary-7118f5dd7-20230705";
            };
            "node_modules/eslint-plugin-react/node_modules/doctrine" = {
              dev = true;
              key = "doctrine/2.1.0";
            };
            "node_modules/eslint-plugin-react/node_modules/resolve" = {
              dev = true;
              key = "resolve/2.0.0-next.4";
            };
            "node_modules/eslint-plugin-react/node_modules/semver" = {
              dev = true;
              key = "semver/6.3.1";
            };
            "node_modules/eslint-plugin-tailwindcss" = {
              dev = true;
              key = "eslint-plugin-tailwindcss/3.13.0";
            };
            "node_modules/eslint-scope" = {
              dev = true;
              key = "eslint-scope/7.2.2";
            };
            "node_modules/eslint-visitor-keys" = {
              dev = true;
              key = "eslint-visitor-keys/3.4.3";
            };
            "node_modules/espree" = {
              dev = true;
              key = "espree/9.6.1";
            };
            "node_modules/esprima" = {
              dev = true;
              key = "esprima/4.0.1";
            };
            "node_modules/esquery" = {
              dev = true;
              key = "esquery/1.5.0";
            };
            "node_modules/esrecurse" = {
              dev = true;
              key = "esrecurse/4.3.0";
            };
            "node_modules/estraverse" = {
              dev = true;
              key = "estraverse/5.3.0";
            };
            "node_modules/estree-walker" = {
              dev = true;
              key = "estree-walker/2.0.2";
            };
            "node_modules/esutils" = {
              dev = true;
              key = "esutils/2.0.3";
            };
            "node_modules/event-target-shim" = {
              dev = true;
              key = "event-target-shim/5.0.1";
            };
            "node_modules/eventemitter3" = {
              key = "eventemitter3/4.0.7";
            };
            "node_modules/execa" = {
              dev = true;
              key = "execa/5.1.1";
            };
            "node_modules/fast-deep-equal" = {
              dev = true;
              key = "fast-deep-equal/3.1.3";
            };
            "node_modules/fast-equals" = {
              key = "fast-equals/5.0.1";
            };
            "node_modules/fast-glob" = {
              key = "fast-glob/3.3.1";
            };
            "node_modules/fast-glob/node_modules/glob-parent" = {
              key = "glob-parent/5.1.2";
            };
            "node_modules/fast-json-stable-stringify" = {
              dev = true;
              key = "fast-json-stable-stringify/2.1.0";
            };
            "node_modules/fast-levenshtein" = {
              dev = true;
              key = "fast-levenshtein/2.0.6";
            };
            "node_modules/fast-memoize" = {
              dev = true;
              key = "fast-memoize/2.5.2";
            };
            "node_modules/fast-safe-stringify" = {
              dev = true;
              key = "fast-safe-stringify/2.1.1";
            };
            "node_modules/fastq" = {
              key = "fastq/1.15.0";
            };
            "node_modules/file-entry-cache" = {
              dev = true;
              key = "file-entry-cache/6.0.1";
            };
            "node_modules/fill-range" = {
              key = "fill-range/7.0.1";
            };
            "node_modules/find-root" = {
              key = "find-root/1.1.0";
            };
            "node_modules/find-up" = {
              dev = true;
              key = "find-up/5.0.0";
            };
            "node_modules/flat-cache" = {
              dev = true;
              key = "flat-cache/3.0.4";
            };
            "node_modules/flatted" = {
              dev = true;
              key = "flatted/3.2.7";
            };
            "node_modules/follow-redirects" = {
              key = "follow-redirects/1.15.2";
            };
            "node_modules/for-each" = {
              dev = true;
              key = "for-each/0.3.3";
            };
            "node_modules/form-data" = {
              key = "form-data/4.0.0";
            };
            "node_modules/format-util" = {
              dev = true;
              key = "format-util/1.0.5";
            };
            "node_modules/fraction.js" = {
              key = "fraction.js/4.2.0";
            };
            "node_modules/fs-extra" = {
              dev = true;
              key = "fs-extra/10.1.0";
            };
            "node_modules/fs.realpath" = {
              key = "fs.realpath/1.0.0";
            };
            "node_modules/fsevents" = {
              key = "fsevents/2.3.2";
              optional = true;
            };
            "node_modules/function-bind" = {
              key = "function-bind/1.1.1";
            };
            "node_modules/function.prototype.name" = {
              dev = true;
              key = "function.prototype.name/1.1.5";
            };
            "node_modules/functions-have-names" = {
              dev = true;
              key = "functions-have-names/1.2.3";
            };
            "node_modules/get-caller-file" = {
              dev = true;
              key = "get-caller-file/2.0.5";
            };
            "node_modules/get-intrinsic" = {
              dev = true;
              key = "get-intrinsic/1.2.1";
            };
            "node_modules/get-source" = {
              dev = true;
              key = "get-source/2.0.12";
            };
            "node_modules/get-source/node_modules/source-map" = {
              dev = true;
              key = "source-map/0.6.1";
            };
            "node_modules/get-stream" = {
              dev = true;
              key = "get-stream/6.0.1";
            };
            "node_modules/get-symbol-description" = {
              dev = true;
              key = "get-symbol-description/1.0.0";
            };
            "node_modules/get-tsconfig" = {
              dev = true;
              key = "get-tsconfig/4.7.0";
            };
            "node_modules/glob" = {
              dev = true;
              key = "glob/7.1.7";
            };
            "node_modules/glob-parent" = {
              key = "glob-parent/6.0.2";
            };
            "node_modules/glob-to-regexp" = {
              key = "glob-to-regexp/0.4.1";
            };
            "node_modules/globals" = {
              dev = true;
              key = "globals/13.21.0";
            };
            "node_modules/globalthis" = {
              dev = true;
              key = "globalthis/1.0.3";
            };
            "node_modules/globby" = {
              dev = true;
              key = "globby/11.1.0";
            };
            "node_modules/goober" = {
              key = "goober/2.1.13";
            };
            "node_modules/gopd" = {
              dev = true;
              key = "gopd/1.0.1";
            };
            "node_modules/graceful-fs" = {
              key = "graceful-fs/4.2.11";
            };
            "node_modules/graphemer" = {
              dev = true;
              key = "graphemer/1.4.0";
            };
            "node_modules/has" = {
              key = "has/1.0.3";
            };
            "node_modules/has-bigints" = {
              dev = true;
              key = "has-bigints/1.0.2";
            };
            "node_modules/has-flag" = {
              dev = true;
              key = "has-flag/4.0.0";
            };
            "node_modules/has-property-descriptors" = {
              dev = true;
              key = "has-property-descriptors/1.0.0";
            };
            "node_modules/has-proto" = {
              dev = true;
              key = "has-proto/1.0.1";
            };
            "node_modules/has-symbols" = {
              dev = true;
              key = "has-symbols/1.0.3";
            };
            "node_modules/has-tostringtag" = {
              dev = true;
              key = "has-tostringtag/1.0.0";
            };
            "node_modules/hex-rgb" = {
              key = "hex-rgb/5.0.0";
            };
            "node_modules/hoist-non-react-statics" = {
              key = "hoist-non-react-statics/3.3.2";
            };
            "node_modules/hoist-non-react-statics/node_modules/react-is" = {
              key = "react-is/16.13.1";
            };
            "node_modules/hpagent" = {
              dev = true;
              key = "hpagent/1.2.0";
            };
            "node_modules/http2-client" = {
              dev = true;
              key = "http2-client/1.3.5";
            };
            "node_modules/human-signals" = {
              dev = true;
              key = "human-signals/2.1.0";
            };
            "node_modules/ibm-openapi-validator" = {
              dev = true;
              key = "ibm-openapi-validator/0.97.5";
            };
            "node_modules/ibm-openapi-validator/node_modules/argparse" = {
              dev = true;
              key = "argparse/1.0.10";
            };
            "node_modules/ibm-openapi-validator/node_modules/commander" = {
              dev = true;
              key = "commander/2.20.3";
            };
            "node_modules/ibm-openapi-validator/node_modules/find-up" = {
              dev = true;
              key = "find-up/3.0.0";
            };
            "node_modules/ibm-openapi-validator/node_modules/js-yaml" = {
              dev = true;
              key = "js-yaml/3.14.1";
            };
            "node_modules/ibm-openapi-validator/node_modules/locate-path" = {
              dev = true;
              key = "locate-path/3.0.0";
            };
            "node_modules/ibm-openapi-validator/node_modules/p-limit" = {
              dev = true;
              key = "p-limit/2.3.0";
            };
            "node_modules/ibm-openapi-validator/node_modules/p-locate" = {
              dev = true;
              key = "p-locate/3.0.0";
            };
            "node_modules/ibm-openapi-validator/node_modules/path-exists" = {
              dev = true;
              key = "path-exists/3.0.0";
            };
            "node_modules/ibm-openapi-validator/node_modules/semver" = {
              dev = true;
              key = "semver/5.7.2";
            };
            "node_modules/ignore" = {
              dev = true;
              key = "ignore/5.2.4";
            };
            "node_modules/immer" = {
              dev = true;
              key = "immer/9.0.21";
            };
            "node_modules/import-fresh" = {
              key = "import-fresh/3.3.0";
            };
            "node_modules/imurmurhash" = {
              dev = true;
              key = "imurmurhash/0.1.4";
            };
            "node_modules/inflight" = {
              key = "inflight/1.0.6";
            };
            "node_modules/inherits" = {
              key = "inherits/2.0.4";
            };
            "node_modules/internal-slot" = {
              dev = true;
              key = "internal-slot/1.0.5";
            };
            "node_modules/internmap" = {
              key = "internmap/2.0.3";
            };
            "node_modules/is-array-buffer" = {
              dev = true;
              key = "is-array-buffer/3.0.2";
            };
            "node_modules/is-arrayish" = {
              key = "is-arrayish/0.2.1";
            };
            "node_modules/is-bigint" = {
              dev = true;
              key = "is-bigint/1.0.4";
            };
            "node_modules/is-binary-path" = {
              key = "is-binary-path/2.1.0";
            };
            "node_modules/is-boolean-object" = {
              dev = true;
              key = "is-boolean-object/1.1.2";
            };
            "node_modules/is-callable" = {
              dev = true;
              key = "is-callable/1.2.7";
            };
            "node_modules/is-core-module" = {
              key = "is-core-module/2.13.0";
            };
            "node_modules/is-date-object" = {
              dev = true;
              key = "is-date-object/1.0.5";
            };
            "node_modules/is-extglob" = {
              key = "is-extglob/2.1.1";
            };
            "node_modules/is-fullwidth-code-point" = {
              dev = true;
              key = "is-fullwidth-code-point/3.0.0";
            };
            "node_modules/is-glob" = {
              key = "is-glob/4.0.3";
            };
            "node_modules/is-negative-zero" = {
              dev = true;
              key = "is-negative-zero/2.0.2";
            };
            "node_modules/is-number" = {
              key = "is-number/7.0.0";
            };
            "node_modules/is-number-object" = {
              dev = true;
              key = "is-number-object/1.0.7";
            };
            "node_modules/is-path-inside" = {
              dev = true;
              key = "is-path-inside/3.0.3";
            };
            "node_modules/is-reference" = {
              dev = true;
              key = "is-reference/1.2.1";
            };
            "node_modules/is-regex" = {
              dev = true;
              key = "is-regex/1.1.4";
            };
            "node_modules/is-shared-array-buffer" = {
              dev = true;
              key = "is-shared-array-buffer/1.0.2";
            };
            "node_modules/is-stream" = {
              dev = true;
              key = "is-stream/2.0.1";
            };
            "node_modules/is-string" = {
              dev = true;
              key = "is-string/1.0.7";
            };
            "node_modules/is-symbol" = {
              dev = true;
              key = "is-symbol/1.0.4";
            };
            "node_modules/is-typed-array" = {
              dev = true;
              key = "is-typed-array/1.1.12";
            };
            "node_modules/is-weakref" = {
              dev = true;
              key = "is-weakref/1.0.2";
            };
            "node_modules/isarray" = {
              dev = true;
              key = "isarray/2.0.5";
            };
            "node_modules/isexe" = {
              dev = true;
              key = "isexe/2.0.0";
            };
            "node_modules/jiti" = {
              key = "jiti/1.19.1";
            };
            "node_modules/js-tokens" = {
              key = "js-tokens/4.0.0";
            };
            "node_modules/js-yaml" = {
              dev = true;
              key = "js-yaml/4.1.0";
            };
            "node_modules/jsep" = {
              dev = true;
              key = "jsep/1.3.8";
            };
            "node_modules/json-dup-key-validator" = {
              dev = true;
              key = "json-dup-key-validator/1.0.3";
            };
            "node_modules/json-parse-even-better-errors" = {
              key = "json-parse-even-better-errors/2.3.1";
            };
            "node_modules/json-schema-ref-parser" = {
              dev = true;
              key = "json-schema-ref-parser/5.1.3";
            };
            "node_modules/json-schema-ref-parser/node_modules/argparse" = {
              dev = true;
              key = "argparse/1.0.10";
            };
            "node_modules/json-schema-ref-parser/node_modules/debug" = {
              dev = true;
              key = "debug/3.2.7";
            };
            "node_modules/json-schema-ref-parser/node_modules/js-yaml" = {
              dev = true;
              key = "js-yaml/3.14.1";
            };
            "node_modules/json-schema-traverse" = {
              dev = true;
              key = "json-schema-traverse/0.4.1";
            };
            "node_modules/json-stable-stringify-without-jsonify" = {
              dev = true;
              key = "json-stable-stringify-without-jsonify/1.0.1";
            };
            "node_modules/json5" = {
              dev = true;
              key = "json5/1.0.2";
            };
            "node_modules/jsonc-parser" = {
              dev = true;
              key = "jsonc-parser/2.2.1";
            };
            "node_modules/jsonfile" = {
              dev = true;
              key = "jsonfile/6.1.0";
            };
            "node_modules/jsonpath-plus" = {
              dev = true;
              key = "jsonpath-plus/7.1.0";
            };
            "node_modules/jsonpointer" = {
              dev = true;
              key = "jsonpointer/5.0.1";
            };
            "node_modules/jsonschema" = {
              dev = true;
              key = "jsonschema/1.4.1";
            };
            "node_modules/jsx-ast-utils" = {
              dev = true;
              key = "jsx-ast-utils/3.3.5";
            };
            "node_modules/language-subtag-registry" = {
              dev = true;
              key = "language-subtag-registry/0.3.22";
            };
            "node_modules/language-tags" = {
              dev = true;
              key = "language-tags/1.0.5";
            };
            "node_modules/leven" = {
              dev = true;
              key = "leven/3.1.0";
            };
            "node_modules/levn" = {
              dev = true;
              key = "levn/0.4.1";
            };
            "node_modules/lilconfig" = {
              key = "lilconfig/2.1.0";
            };
            "node_modules/lines-and-columns" = {
              key = "lines-and-columns/1.2.4";
            };
            "node_modules/locate-path" = {
              dev = true;
              key = "locate-path/6.0.0";
            };
            "node_modules/lodash" = {
              key = "lodash/4.17.21";
            };
            "node_modules/lodash.get" = {
              dev = true;
              key = "lodash.get/4.4.2";
            };
            "node_modules/lodash.isempty" = {
              dev = true;
              key = "lodash.isempty/4.4.0";
            };
            "node_modules/lodash.merge" = {
              dev = true;
              key = "lodash.merge/4.6.2";
            };
            "node_modules/lodash.omit" = {
              dev = true;
              key = "lodash.omit/4.5.0";
            };
            "node_modules/lodash.omitby" = {
              dev = true;
              key = "lodash.omitby/4.6.0";
            };
            "node_modules/lodash.topath" = {
              dev = true;
              key = "lodash.topath/4.5.2";
            };
            "node_modules/lodash.uniq" = {
              dev = true;
              key = "lodash.uniq/4.5.0";
            };
            "node_modules/lodash.uniqby" = {
              dev = true;
              key = "lodash.uniqby/4.7.0";
            };
            "node_modules/lodash.uniqwith" = {
              dev = true;
              key = "lodash.uniqwith/4.5.0";
            };
            "node_modules/loose-envify" = {
              key = "loose-envify/1.4.0";
            };
            "node_modules/lru-cache" = {
              dev = true;
              key = "lru-cache/6.0.0";
            };
            "node_modules/magic-string" = {
              dev = true;
              key = "magic-string/0.25.9";
            };
            "node_modules/matcher" = {
              dev = true;
              key = "matcher/1.1.1";
            };
            "node_modules/matcher/node_modules/escape-string-regexp" = {
              dev = true;
              key = "escape-string-regexp/1.0.5";
            };
            "node_modules/merge-stream" = {
              dev = true;
              key = "merge-stream/2.0.0";
            };
            "node_modules/merge2" = {
              key = "merge2/1.4.1";
            };
            "node_modules/micromatch" = {
              key = "micromatch/4.0.5";
            };
            "node_modules/mime-db" = {
              key = "mime-db/1.52.0";
            };
            "node_modules/mime-types" = {
              key = "mime-types/2.1.35";
            };
            "node_modules/mimic-fn" = {
              dev = true;
              key = "mimic-fn/2.1.0";
            };
            "node_modules/minimatch" = {
              key = "minimatch/3.1.2";
            };
            "node_modules/minimist" = {
              dev = true;
              key = "minimist/1.2.8";
            };
            "node_modules/ms" = {
              dev = true;
              key = "ms/2.1.2";
            };
            "node_modules/mz" = {
              key = "mz/2.7.0";
            };
            "node_modules/nanoid" = {
              key = "nanoid/3.3.6";
            };
            "node_modules/natural-compare" = {
              dev = true;
              key = "natural-compare/1.4.0";
            };
            "node_modules/next" = {
              key = "next/13.4.12";
            };
            "node_modules/next/node_modules/postcss" = {
              key = "postcss/8.4.14";
            };
            "node_modules/nimma" = {
              dev = true;
              key = "nimma/0.2.2";
            };
            "node_modules/nimma/node_modules/jsonpath-plus" = {
              dev = true;
              key = "jsonpath-plus/6.0.1";
              optional = true;
            };
            "node_modules/node-fetch" = {
              dev = true;
              key = "node-fetch/2.7.0";
            };
            "node_modules/node-fetch-h2" = {
              dev = true;
              key = "node-fetch-h2/2.3.0";
            };
            "node_modules/node-readfiles" = {
              dev = true;
              key = "node-readfiles/0.2.0";
            };
            "node_modules/node-releases" = {
              key = "node-releases/2.0.13";
            };
            "node_modules/normalize-path" = {
              key = "normalize-path/3.0.0";
            };
            "node_modules/normalize-range" = {
              key = "normalize-range/0.1.2";
            };
            "node_modules/npm-run-path" = {
              dev = true;
              key = "npm-run-path/4.0.1";
            };
            "node_modules/oas-kit-common" = {
              dev = true;
              key = "oas-kit-common/1.0.8";
            };
            "node_modules/oas-linter" = {
              dev = true;
              key = "oas-linter/3.2.2";
            };
            "node_modules/oas-resolver" = {
              dev = true;
              key = "oas-resolver/2.5.6";
            };
            "node_modules/oas-schema-walker" = {
              dev = true;
              key = "oas-schema-walker/1.1.5";
            };
            "node_modules/oas-validator" = {
              dev = true;
              key = "oas-validator/5.0.8";
            };
            "node_modules/object-assign" = {
              key = "object-assign/4.1.1";
            };
            "node_modules/object-hash" = {
              key = "object-hash/3.0.0";
            };
            "node_modules/object-inspect" = {
              dev = true;
              key = "object-inspect/1.12.3";
            };
            "node_modules/object-keys" = {
              dev = true;
              key = "object-keys/1.1.1";
            };
            "node_modules/object.assign" = {
              dev = true;
              key = "object.assign/4.1.4";
            };
            "node_modules/object.entries" = {
              dev = true;
              key = "object.entries/1.1.6";
            };
            "node_modules/object.fromentries" = {
              dev = true;
              key = "object.fromentries/2.0.6";
            };
            "node_modules/object.groupby" = {
              dev = true;
              key = "object.groupby/1.0.0";
            };
            "node_modules/object.hasown" = {
              dev = true;
              key = "object.hasown/1.1.2";
            };
            "node_modules/object.values" = {
              dev = true;
              key = "object.values/1.1.6";
            };
            "node_modules/once" = {
              key = "once/1.4.0";
            };
            "node_modules/onetime" = {
              dev = true;
              key = "onetime/5.1.2";
            };
            "node_modules/ono" = {
              dev = true;
              key = "ono/4.0.11";
            };
            "node_modules/openapi-types" = {
              dev = true;
              key = "openapi-types/12.1.3";
            };
            "node_modules/openapi3-ts" = {
              dev = true;
              key = "openapi3-ts/3.2.0";
            };
            "node_modules/openapi3-ts/node_modules/yaml" = {
              dev = true;
              key = "yaml/2.3.1";
            };
            "node_modules/optionator" = {
              dev = true;
              key = "optionator/0.9.3";
            };
            "node_modules/orval" = {
              dev = true;
              key = "orval/6.17.0";
            };
            "node_modules/orval/node_modules/ajv" = {
              dev = true;
              key = "ajv/8.12.0";
            };
            "node_modules/orval/node_modules/json-schema-traverse" = {
              dev = true;
              key = "json-schema-traverse/1.0.0";
            };
            "node_modules/p-limit" = {
              dev = true;
              key = "p-limit/3.1.0";
            };
            "node_modules/p-locate" = {
              dev = true;
              key = "p-locate/5.0.0";
            };
            "node_modules/p-try" = {
              dev = true;
              key = "p-try/2.2.0";
            };
            "node_modules/pad" = {
              dev = true;
              key = "pad/2.3.0";
            };
            "node_modules/parent-module" = {
              key = "parent-module/1.0.1";
            };
            "node_modules/parse-json" = {
              key = "parse-json/5.2.0";
            };
            "node_modules/path-exists" = {
              dev = true;
              key = "path-exists/4.0.0";
            };
            "node_modules/path-is-absolute" = {
              key = "path-is-absolute/1.0.1";
            };
            "node_modules/path-key" = {
              dev = true;
              key = "path-key/3.1.1";
            };
            "node_modules/path-parse" = {
              key = "path-parse/1.0.7";
            };
            "node_modules/path-type" = {
              key = "path-type/4.0.0";
            };
            "node_modules/picocolors" = {
              key = "picocolors/1.0.0";
            };
            "node_modules/picomatch" = {
              key = "picomatch/2.3.1";
            };
            "node_modules/pify" = {
              key = "pify/2.3.0";
            };
            "node_modules/pirates" = {
              key = "pirates/4.0.6";
            };
            "node_modules/pony-cause" = {
              dev = true;
              key = "pony-cause/1.1.1";
            };
            "node_modules/postcss" = {
              key = "postcss/8.4.27";
            };
            "node_modules/postcss-import" = {
              key = "postcss-import/15.1.0";
            };
            "node_modules/postcss-js" = {
              key = "postcss-js/4.0.1";
            };
            "node_modules/postcss-load-config" = {
              key = "postcss-load-config/4.0.1";
            };
            "node_modules/postcss-load-config/node_modules/yaml" = {
              key = "yaml/2.3.1";
            };
            "node_modules/postcss-nested" = {
              key = "postcss-nested/6.0.1";
            };
            "node_modules/postcss-selector-parser" = {
              key = "postcss-selector-parser/6.0.13";
            };
            "node_modules/postcss-value-parser" = {
              key = "postcss-value-parser/4.2.0";
            };
            "node_modules/prelude-ls" = {
              dev = true;
              key = "prelude-ls/1.2.1";
            };
            "node_modules/prettier" = {
              dev = true;
              key = "prettier/3.0.1";
            };
            "node_modules/prettier-plugin-tailwindcss" = {
              dev = true;
              key = "prettier-plugin-tailwindcss/0.4.1";
            };
            "node_modules/printable-characters" = {
              dev = true;
              key = "printable-characters/1.0.42";
            };
            "node_modules/prop-types" = {
              key = "prop-types/15.8.1";
            };
            "node_modules/prop-types/node_modules/react-is" = {
              key = "react-is/16.13.1";
            };
            "node_modules/proxy-from-env" = {
              key = "proxy-from-env/1.1.0";
            };
            "node_modules/punycode" = {
              dev = true;
              key = "punycode/2.3.0";
            };
            "node_modules/queue-microtask" = {
              key = "queue-microtask/1.2.3";
            };
            "node_modules/react" = {
              key = "react/18.2.0";
            };
            "node_modules/react-dom" = {
              key = "react-dom/18.2.0";
            };
            "node_modules/react-hook-form" = {
              key = "react-hook-form/7.45.4";
            };
            "node_modules/react-hot-toast" = {
              key = "react-hot-toast/2.4.1";
            };
            "node_modules/react-is" = {
              key = "react-is/18.2.0";
            };
            "node_modules/react-lifecycles-compat" = {
              key = "react-lifecycles-compat/3.0.4";
            };
            "node_modules/react-resize-detector" = {
              key = "react-resize-detector/8.1.0";
            };
            "node_modules/react-smooth" = {
              key = "react-smooth/2.0.3";
            };
            "node_modules/react-smooth/node_modules/dom-helpers" = {
              key = "dom-helpers/3.4.0";
            };
            "node_modules/react-smooth/node_modules/react-transition-group" = {
              key = "react-transition-group/2.9.0";
            };
            "node_modules/react-transition-group" = {
              key = "react-transition-group/4.4.5";
            };
            "node_modules/read-cache" = {
              key = "read-cache/1.0.0";
            };
            "node_modules/readdirp" = {
              key = "readdirp/3.6.0";
            };
            "node_modules/recharts" = {
              key = "recharts/2.7.3";
            };
            "node_modules/recharts-scale" = {
              key = "recharts-scale/0.4.5";
            };
            "node_modules/recharts/node_modules/react-is" = {
              key = "react-is/16.13.1";
            };
            "node_modules/reduce-css-calc" = {
              key = "reduce-css-calc/2.1.8";
            };
            "node_modules/reduce-css-calc/node_modules/postcss-value-parser" = {
              key = "postcss-value-parser/3.3.1";
            };
            "node_modules/reftools" = {
              dev = true;
              key = "reftools/1.1.9";
            };
            "node_modules/regenerator-runtime" = {
              key = "regenerator-runtime/0.14.0";
            };
            "node_modules/regexp.prototype.flags" = {
              dev = true;
              key = "regexp.prototype.flags/1.5.0";
            };
            "node_modules/require-all" = {
              dev = true;
              key = "require-all/3.0.0";
            };
            "node_modules/require-directory" = {
              dev = true;
              key = "require-directory/2.1.1";
            };
            "node_modules/require-from-string" = {
              dev = true;
              key = "require-from-string/2.0.2";
            };
            "node_modules/reserved" = {
              dev = true;
              key = "reserved/0.1.2";
            };
            "node_modules/resolve" = {
              key = "resolve/1.22.4";
            };
            "node_modules/resolve-from" = {
              key = "resolve-from/4.0.0";
            };
            "node_modules/resolve-pkg-maps" = {
              dev = true;
              key = "resolve-pkg-maps/1.0.0";
            };
            "node_modules/reusify" = {
              key = "reusify/1.0.4";
            };
            "node_modules/rimraf" = {
              dev = true;
              key = "rimraf/3.0.2";
            };
            "node_modules/rollup" = {
              dev = true;
              key = "rollup/2.79.1";
            };
            "node_modules/run-parallel" = {
              key = "run-parallel/1.2.0";
            };
            "node_modules/safe-array-concat" = {
              dev = true;
              key = "safe-array-concat/1.0.0";
            };
            "node_modules/safe-regex-test" = {
              dev = true;
              key = "safe-regex-test/1.0.0";
            };
            "node_modules/safe-stable-stringify" = {
              dev = true;
              key = "safe-stable-stringify/1.1.1";
            };
            "node_modules/scheduler" = {
              key = "scheduler/0.23.0";
            };
            "node_modules/semver" = {
              dev = true;
              key = "semver/7.5.4";
            };
            "node_modules/shebang-command" = {
              dev = true;
              key = "shebang-command/2.0.0";
            };
            "node_modules/shebang-regex" = {
              dev = true;
              key = "shebang-regex/3.0.0";
            };
            "node_modules/should" = {
              dev = true;
              key = "should/13.2.3";
            };
            "node_modules/should-equal" = {
              dev = true;
              key = "should-equal/2.0.0";
            };
            "node_modules/should-format" = {
              dev = true;
              key = "should-format/3.0.3";
            };
            "node_modules/should-type" = {
              dev = true;
              key = "should-type/1.4.0";
            };
            "node_modules/should-type-adaptors" = {
              dev = true;
              key = "should-type-adaptors/1.1.0";
            };
            "node_modules/should-util" = {
              dev = true;
              key = "should-util/1.0.1";
            };
            "node_modules/side-channel" = {
              dev = true;
              key = "side-channel/1.0.4";
            };
            "node_modules/signal-exit" = {
              dev = true;
              key = "signal-exit/3.0.7";
            };
            "node_modules/simple-eval" = {
              dev = true;
              key = "simple-eval/1.0.0";
            };
            "node_modules/slash" = {
              dev = true;
              key = "slash/3.0.0";
            };
            "node_modules/source-map" = {
              key = "source-map/0.5.7";
            };
            "node_modules/source-map-js" = {
              key = "source-map-js/1.0.2";
            };
            "node_modules/sourcemap-codec" = {
              dev = true;
              key = "sourcemap-codec/1.4.8";
            };
            "node_modules/sprintf-js" = {
              dev = true;
              key = "sprintf-js/1.0.3";
            };
            "node_modules/stacktracey" = {
              dev = true;
              key = "stacktracey/2.1.8";
            };
            "node_modules/streamsearch" = {
              key = "streamsearch/1.1.0";
            };
            "node_modules/string-argv" = {
              dev = true;
              key = "string-argv/0.3.2";
            };
            "node_modules/string-width" = {
              dev = true;
              key = "string-width/4.2.3";
            };
            "node_modules/string-width/node_modules/emoji-regex" = {
              dev = true;
              key = "emoji-regex/8.0.0";
            };
            "node_modules/string.prototype.matchall" = {
              dev = true;
              key = "string.prototype.matchall/4.0.8";
            };
            "node_modules/string.prototype.trim" = {
              dev = true;
              key = "string.prototype.trim/1.2.7";
            };
            "node_modules/string.prototype.trimend" = {
              dev = true;
              key = "string.prototype.trimend/1.0.6";
            };
            "node_modules/string.prototype.trimstart" = {
              dev = true;
              key = "string.prototype.trimstart/1.0.6";
            };
            "node_modules/strip-ansi" = {
              dev = true;
              key = "strip-ansi/6.0.1";
            };
            "node_modules/strip-bom" = {
              dev = true;
              key = "strip-bom/3.0.0";
            };
            "node_modules/strip-final-newline" = {
              dev = true;
              key = "strip-final-newline/2.0.0";
            };
            "node_modules/strip-json-comments" = {
              dev = true;
              key = "strip-json-comments/3.1.1";
            };
            "node_modules/styled-jsx" = {
              key = "styled-jsx/5.1.1";
            };
            "node_modules/stylis" = {
              key = "stylis/4.2.0";
            };
            "node_modules/sucrase" = {
              key = "sucrase/3.34.0";
            };
            "node_modules/sucrase/node_modules/glob" = {
              key = "glob/7.1.6";
            };
            "node_modules/supports-color" = {
              dev = true;
              key = "supports-color/7.2.0";
            };
            "node_modules/supports-preserve-symlinks-flag" = {
              key = "supports-preserve-symlinks-flag/1.0.0";
            };
            "node_modules/swagger2openapi" = {
              dev = true;
              key = "swagger2openapi/7.0.8";
            };
            "node_modules/swr" = {
              key = "swr/2.2.1";
            };
            "node_modules/tailwindcss" = {
              key = "tailwindcss/3.3.3";
            };
            "node_modules/tapable" = {
              dev = true;
              key = "tapable/2.2.1";
            };
            "node_modules/text-table" = {
              dev = true;
              key = "text-table/0.2.0";
            };
            "node_modules/thenify" = {
              key = "thenify/3.3.1";
            };
            "node_modules/thenify-all" = {
              key = "thenify-all/1.6.0";
            };
            "node_modules/to-fast-properties" = {
              key = "to-fast-properties/2.0.0";
            };
            "node_modules/to-regex-range" = {
              key = "to-regex-range/5.0.1";
            };
            "node_modules/tr46" = {
              dev = true;
              key = "tr46/0.0.3";
            };
            "node_modules/ts-interface-checker" = {
              key = "ts-interface-checker/0.1.13";
            };
            "node_modules/tsconfck" = {
              dev = true;
              key = "tsconfck/2.1.2";
            };
            "node_modules/tsconfig-paths" = {
              dev = true;
              key = "tsconfig-paths/3.14.2";
            };
            "node_modules/tslib" = {
              key = "tslib/2.6.1";
            };
            "node_modules/tsutils" = {
              dev = true;
              key = "tsutils/3.21.0";
            };
            "node_modules/tsutils/node_modules/tslib" = {
              dev = true;
              key = "tslib/1.14.1";
            };
            "node_modules/type-check" = {
              dev = true;
              key = "type-check/0.4.0";
            };
            "node_modules/type-fest" = {
              dev = true;
              key = "type-fest/0.20.2";
            };
            "node_modules/typed-array-buffer" = {
              dev = true;
              key = "typed-array-buffer/1.0.0";
            };
            "node_modules/typed-array-byte-length" = {
              dev = true;
              key = "typed-array-byte-length/1.0.0";
            };
            "node_modules/typed-array-byte-offset" = {
              dev = true;
              key = "typed-array-byte-offset/1.0.0";
            };
            "node_modules/typed-array-length" = {
              dev = true;
              key = "typed-array-length/1.0.4";
            };
            "node_modules/typescript" = {
              dev = true;
              key = "typescript/5.1.6";
            };
            "node_modules/unbox-primitive" = {
              dev = true;
              key = "unbox-primitive/1.0.2";
            };
            "node_modules/universalify" = {
              dev = true;
              key = "universalify/2.0.0";
            };
            "node_modules/update-browserslist-db" = {
              key = "update-browserslist-db/1.0.11";
            };
            "node_modules/uri-js" = {
              dev = true;
              key = "uri-js/4.4.1";
            };
            "node_modules/urijs" = {
              dev = true;
              key = "urijs/1.19.11";
            };
            "node_modules/use-sync-external-store" = {
              key = "use-sync-external-store/1.2.0";
            };
            "node_modules/util-deprecate" = {
              key = "util-deprecate/1.0.2";
            };
            "node_modules/utility-types" = {
              dev = true;
              key = "utility-types/3.10.0";
            };
            "node_modules/validate-npm-package-name" = {
              dev = true;
              key = "validate-npm-package-name/3.0.0";
            };
            "node_modules/validator" = {
              dev = true;
              key = "validator/13.11.0";
            };
            "node_modules/victory-vendor" = {
              key = "victory-vendor/36.6.11";
            };
            "node_modules/watchpack" = {
              key = "watchpack/2.4.0";
            };
            "node_modules/wcwidth" = {
              dev = true;
              key = "wcwidth/1.0.1";
            };
            "node_modules/webidl-conversions" = {
              dev = true;
              key = "webidl-conversions/3.0.1";
            };
            "node_modules/whatwg-url" = {
              dev = true;
              key = "whatwg-url/5.0.0";
            };
            "node_modules/which" = {
              dev = true;
              key = "which/2.0.2";
            };
            "node_modules/which-boxed-primitive" = {
              dev = true;
              key = "which-boxed-primitive/1.0.2";
            };
            "node_modules/which-typed-array" = {
              dev = true;
              key = "which-typed-array/1.1.11";
            };
            "node_modules/wrap-ansi" = {
              dev = true;
              key = "wrap-ansi/7.0.0";
            };
            "node_modules/wrappy" = {
              key = "wrappy/1.0.2";
            };
            "node_modules/y18n" = {
              dev = true;
              key = "y18n/5.0.8";
            };
            "node_modules/yallist" = {
              dev = true;
              key = "yallist/4.0.0";
            };
            "node_modules/yaml" = {
              key = "yaml/1.10.2";
            };
            "node_modules/yaml-js" = {
              dev = true;
              key = "yaml-js/0.2.3";
            };
            "node_modules/yargs" = {
              dev = true;
              key = "yargs/17.3.1";
            };
            "node_modules/yargs-parser" = {
              dev = true;
              key = "yargs-parser/21.1.1";
            };
            "node_modules/yocto-queue" = {
              dev = true;
              key = "yocto-queue/0.1.0";
            };
            "node_modules/zod" = {
              key = "zod/3.21.4";
            };
          };
          version = "0.1.0";
        };
      };
      mz = {
        "2.7.0" = {
          depInfo = {
            any-promise = {
              descriptor = "^1.0.0";
              pin = "1.3.0";
              runtime = true;
            };
            object-assign = {
              descriptor = "^4.0.1";
              pin = "4.1.1";
              runtime = true;
            };
            thenify-all = {
              descriptor = "^1.0.0";
              pin = "1.6.0";
              runtime = true;
            };
          };
          fetchInfo = {
            narHash = "sha256-xtRKoVYhGvpEIPwaiiD2Dtiz0JYmS+Q4GRsl0cUOB0I=";
            type = "tarball";
            url = "https://registry.npmjs.org/mz/-/mz-2.7.0.tgz";
          };
          ident = "mz";
          ltype = "file";
          version = "2.7.0";
        };
      };
      nanoid = {
        "3.3.6" = {
          binInfo = {
            binPairs = {
              nanoid = "bin/nanoid.cjs";
            };
          };
          fetchInfo = {
            narHash = "sha256-TC35pZLwvWuHS/SaLOeDIXrqvNEHJP7uJHs7uB/dzIc=";
            type = "tarball";
            url = "https://registry.npmjs.org/nanoid/-/nanoid-3.3.6.tgz";
          };
          ident = "nanoid";
          ltype = "file";
          treeInfo = { };
          version = "3.3.6";
        };
      };
      natural-compare = {
        "1.4.0" = {
          fetchInfo = {
            narHash = "sha256-wx+m763bR0Auq7WpVJREb2xXTIHcZMYL9T/G+Y0FQlY=";
            type = "tarball";
            url = "https://registry.npmjs.org/natural-compare/-/natural-compare-1.4.0.tgz";
          };
          ident = "natural-compare";
          ltype = "file";
          treeInfo = { };
          version = "1.4.0";
        };
      };
      next = {
        "13.4.12" = {
          binInfo = {
            binPairs = {
              next = "dist/bin/next";
            };
          };
          depInfo = {
            "@next/env" = {
              descriptor = "13.4.12";
              pin = "13.4.12";
              runtime = true;
            };
            "@next/swc-darwin-arm64" = {
              descriptor = "13.4.12";
              optional = true;
              pin = "13.4.12";
              runtime = true;
            };
            "@next/swc-darwin-x64" = {
              descriptor = "13.4.12";
              optional = true;
              pin = "13.4.12";
              runtime = true;
            };
            "@next/swc-linux-arm64-gnu" = {
              descriptor = "13.4.12";
              optional = true;
              pin = "13.4.12";
              runtime = true;
            };
            "@next/swc-linux-arm64-musl" = {
              descriptor = "13.4.12";
              optional = true;
              pin = "13.4.12";
              runtime = true;
            };
            "@next/swc-linux-x64-gnu" = {
              descriptor = "13.4.12";
              optional = true;
              pin = "13.4.12";
              runtime = true;
            };
            "@next/swc-linux-x64-musl" = {
              descriptor = "13.4.12";
              optional = true;
              pin = "13.4.12";
              runtime = true;
            };
            "@next/swc-win32-arm64-msvc" = {
              descriptor = "13.4.12";
              optional = true;
              pin = "13.4.12";
              runtime = true;
            };
            "@next/swc-win32-ia32-msvc" = {
              descriptor = "13.4.12";
              optional = true;
              pin = "13.4.12";
              runtime = true;
            };
            "@next/swc-win32-x64-msvc" = {
              descriptor = "13.4.12";
              optional = true;
              pin = "13.4.12";
              runtime = true;
            };
            "@swc/helpers" = {
              descriptor = "0.5.1";
              pin = "0.5.1";
              runtime = true;
            };
            busboy = {
              descriptor = "1.6.0";
              pin = "1.6.0";
              runtime = true;
            };
            caniuse-lite = {
              descriptor = "^1.0.30001406";
              pin = "1.0.30001520";
              runtime = true;
            };
            postcss = {
              descriptor = "8.4.14";
              pin = "8.4.14";
              runtime = true;
            };
            styled-jsx = {
              descriptor = "5.1.1";
              pin = "5.1.1";
              runtime = true;
            };
            watchpack = {
              descriptor = "2.4.0";
              pin = "2.4.0";
              runtime = true;
            };
            zod = {
              descriptor = "3.21.4";
              pin = "3.21.4";
              runtime = true;
            };
          };
          fetchInfo = {
            narHash = "sha256-BW5bbAuPbG2W3utMOP0i82eKQo/SVZ+upAN3+JH96pc=";
            type = "tarball";
            url = "https://registry.npmjs.org/next/-/next-13.4.12.tgz";
          };
          ident = "next";
          ltype = "file";
          peerInfo = {
            "@opentelemetry/api" = {
              descriptor = "^1.1.0";
              optional = true;
            };
            fibers = {
              descriptor = ">= 3.1.0";
              optional = true;
            };
            react = {
              descriptor = "^18.2.0";
            };
            react-dom = {
              descriptor = "^18.2.0";
            };
            sass = {
              descriptor = "^1.3.0";
              optional = true;
            };
          };
          version = "13.4.12";
        };
      };
      nimma = {
        "0.2.2" = {
          depInfo = {
            "@jsep-plugin/regex" = {
              descriptor = "^1.0.1";
              pin = "1.0.3";
              runtime = true;
            };
            "@jsep-plugin/ternary" = {
              descriptor = "^1.0.2";
              pin = "1.1.3";
              runtime = true;
            };
            astring = {
              descriptor = "^1.8.1";
              pin = "1.8.6";
              runtime = true;
            };
            jsep = {
              descriptor = "^1.2.0";
              pin = "1.3.8";
              runtime = true;
            };
            jsonpath-plus = {
              descriptor = "^6.0.1";
              optional = true;
              pin = "6.0.1";
              runtime = true;
            };
            "lodash.topath" = {
              descriptor = "^4.5.2";
              optional = true;
              pin = "4.5.2";
              runtime = true;
            };
          };
          fetchInfo = {
            narHash = "sha256-WDwZHG+KF+IkVPY/YqjfeN3WbKTztNu2c+JcQ22zYgM=";
            type = "tarball";
            url = "https://registry.npmjs.org/nimma/-/nimma-0.2.2.tgz";
          };
          ident = "nimma";
          ltype = "file";
          version = "0.2.2";
        };
      };
      node-fetch = {
        "2.7.0" = {
          depInfo = {
            whatwg-url = {
              descriptor = "^5.0.0";
              pin = "5.0.0";
              runtime = true;
            };
          };
          fetchInfo = {
            narHash = "sha256-sYu30V8Lq3yMIV1AvBOq2RoF8TZNp372Gi5cvBsYDSY=";
            type = "tarball";
            url = "https://registry.npmjs.org/node-fetch/-/node-fetch-2.7.0.tgz";
          };
          ident = "node-fetch";
          ltype = "file";
          peerInfo = {
            encoding = {
              descriptor = "^0.1.0";
              optional = true;
            };
          };
          version = "2.7.0";
        };
      };
      node-fetch-h2 = {
        "2.3.0" = {
          depInfo = {
            http2-client = {
              descriptor = "^1.2.5";
              pin = "1.3.5";
              runtime = true;
            };
          };
          fetchInfo = {
            narHash = "sha256-erLShNVHKoJW1hKMMTboDxnlRZah9MHZlHiG+6Cl4mk=";
            type = "tarball";
            url = "https://registry.npmjs.org/node-fetch-h2/-/node-fetch-h2-2.3.0.tgz";
          };
          ident = "node-fetch-h2";
          ltype = "file";
          version = "2.3.0";
        };
      };
      node-readfiles = {
        "0.2.0" = {
          depInfo = {
            es6-promise = {
              descriptor = "^3.2.1";
              pin = "3.3.1";
              runtime = true;
            };
          };
          fetchInfo = {
            narHash = "sha256-HDWZGYa+Mhns8g4nlTcOQLiTojzsXAR4FnWivw0k3hg=";
            type = "tarball";
            url = "https://registry.npmjs.org/node-readfiles/-/node-readfiles-0.2.0.tgz";
          };
          ident = "node-readfiles";
          ltype = "file";
          version = "0.2.0";
        };
      };
      node-releases = {
        "2.0.13" = {
          fetchInfo = {
            narHash = "sha256-IZeGucMI6b4AS9l5MWAkvQQq1bBfc0ZfzdKmt44Y9pg=";
            type = "tarball";
            url = "https://registry.npmjs.org/node-releases/-/node-releases-2.0.13.tgz";
          };
          ident = "node-releases";
          ltype = "file";
          treeInfo = { };
          version = "2.0.13";
        };
      };
      normalize-path = {
        "3.0.0" = {
          fetchInfo = {
            narHash = "sha256-dEESYAs01W+lUXWyDzFkbIwz/dIe85OeDKy23RRoa6E=";
            type = "tarball";
            url = "https://registry.npmjs.org/normalize-path/-/normalize-path-3.0.0.tgz";
          };
          ident = "normalize-path";
          ltype = "file";
          treeInfo = { };
          version = "3.0.0";
        };
      };
      normalize-range = {
        "0.1.2" = {
          fetchInfo = {
            narHash = "sha256-+vANMie3QIxDi4WkHdgNELzg+YZp6/GzUEyvTAVWlgc=";
            type = "tarball";
            url = "https://registry.npmjs.org/normalize-range/-/normalize-range-0.1.2.tgz";
          };
          ident = "normalize-range";
          ltype = "file";
          treeInfo = { };
          version = "0.1.2";
        };
      };
      npm-run-path = {
        "4.0.1" = {
          depInfo = {
            path-key = {
              descriptor = "^3.0.0";
              pin = "3.1.1";
              runtime = true;
            };
          };
          fetchInfo = {
            narHash = "sha256-ZefVxdnSyuTRRctCRlLr8Ga7HtLhuFKX4CPVtLLPQvU=";
            type = "tarball";
            url = "https://registry.npmjs.org/npm-run-path/-/npm-run-path-4.0.1.tgz";
          };
          ident = "npm-run-path";
          ltype = "file";
          version = "4.0.1";
        };
      };
      oas-kit-common = {
        "1.0.8" = {
          depInfo = {
            fast-safe-stringify = {
              descriptor = "^2.0.7";
              pin = "2.1.1";
              runtime = true;
            };
          };
          fetchInfo = {
            narHash = "sha256-t7EJXo88oiCZ86iAu9CcSoxvHptzvdggc36Q+8/NQm4=";
            type = "tarball";
            url = "https://registry.npmjs.org/oas-kit-common/-/oas-kit-common-1.0.8.tgz";
          };
          ident = "oas-kit-common";
          ltype = "file";
          version = "1.0.8";
        };
      };
      oas-linter = {
        "3.2.2" = {
          depInfo = {
            "@exodus/schemasafe" = {
              descriptor = "^1.0.0-rc.2";
              pin = "1.2.4";
              runtime = true;
            };
            should = {
              descriptor = "^13.2.1";
              pin = "13.2.3";
              runtime = true;
            };
            yaml = {
              descriptor = "^1.10.0";
              pin = "1.10.2";
              runtime = true;
            };
          };
          fetchInfo = {
            narHash = "sha256-tOlflDW8DTgSPibm9lEzc+Z8k/ud3zXsf8VHzNdoSow=";
            type = "tarball";
            url = "https://registry.npmjs.org/oas-linter/-/oas-linter-3.2.2.tgz";
          };
          ident = "oas-linter";
          ltype = "file";
          version = "3.2.2";
        };
      };
      oas-resolver = {
        "2.5.6" = {
          binInfo = {
            binPairs = {
              resolve = "resolve.js";
            };
          };
          depInfo = {
            node-fetch-h2 = {
              descriptor = "^2.3.0";
              pin = "2.3.0";
              runtime = true;
            };
            oas-kit-common = {
              descriptor = "^1.0.8";
              pin = "1.0.8";
              runtime = true;
            };
            reftools = {
              descriptor = "^1.1.9";
              pin = "1.1.9";
              runtime = true;
            };
            yaml = {
              descriptor = "^1.10.0";
              pin = "1.10.2";
              runtime = true;
            };
            yargs = {
              descriptor = "^17.0.1";
              pin = "17.3.1";
              runtime = true;
            };
          };
          fetchInfo = {
            narHash = "sha256-DKT6M1zibNhnx+ZW/6tPdP5qXV+PIkj0WZGrlElFJ+o=";
            type = "tarball";
            url = "https://registry.npmjs.org/oas-resolver/-/oas-resolver-2.5.6.tgz";
          };
          ident = "oas-resolver";
          ltype = "file";
          version = "2.5.6";
        };
      };
      oas-schema-walker = {
        "1.1.5" = {
          fetchInfo = {
            narHash = "sha256-VL31fUIhBgmsTBEnQ3wkBWSXXE9bwC96FOK8DHDHkIs=";
            type = "tarball";
            url = "https://registry.npmjs.org/oas-schema-walker/-/oas-schema-walker-1.1.5.tgz";
          };
          ident = "oas-schema-walker";
          ltype = "file";
          treeInfo = { };
          version = "1.1.5";
        };
      };
      oas-validator = {
        "5.0.8" = {
          depInfo = {
            call-me-maybe = {
              descriptor = "^1.0.1";
              pin = "1.0.2";
              runtime = true;
            };
            oas-kit-common = {
              descriptor = "^1.0.8";
              pin = "1.0.8";
              runtime = true;
            };
            oas-linter = {
              descriptor = "^3.2.2";
              pin = "3.2.2";
              runtime = true;
            };
            oas-resolver = {
              descriptor = "^2.5.6";
              pin = "2.5.6";
              runtime = true;
            };
            oas-schema-walker = {
              descriptor = "^1.1.5";
              pin = "1.1.5";
              runtime = true;
            };
            reftools = {
              descriptor = "^1.1.9";
              pin = "1.1.9";
              runtime = true;
            };
            should = {
              descriptor = "^13.2.1";
              pin = "13.2.3";
              runtime = true;
            };
            yaml = {
              descriptor = "^1.10.0";
              pin = "1.10.2";
              runtime = true;
            };
          };
          fetchInfo = {
            narHash = "sha256-ajBJGOtF1imjvYq8IBaopmBC42RhlAqlsJZSPlRuy8c=";
            type = "tarball";
            url = "https://registry.npmjs.org/oas-validator/-/oas-validator-5.0.8.tgz";
          };
          ident = "oas-validator";
          ltype = "file";
          version = "5.0.8";
        };
      };
      object-assign = {
        "4.1.1" = {
          fetchInfo = {
            narHash = "sha256-fy4mKEXjhbY13vj3gcgJUn+6sWqwAFywEe9ioQJAia4=";
            type = "tarball";
            url = "https://registry.npmjs.org/object-assign/-/object-assign-4.1.1.tgz";
          };
          ident = "object-assign";
          ltype = "file";
          treeInfo = { };
          version = "4.1.1";
        };
      };
      object-hash = {
        "3.0.0" = {
          fetchInfo = {
            narHash = "sha256-YvFDzZa3ZcRs4KxjcEGEURlFg0jXgmlJMJnGAl1rCOk=";
            type = "tarball";
            url = "https://registry.npmjs.org/object-hash/-/object-hash-3.0.0.tgz";
          };
          ident = "object-hash";
          ltype = "file";
          treeInfo = { };
          version = "3.0.0";
        };
      };
      object-inspect = {
        "1.12.3" = {
          fetchInfo = {
            narHash = "sha256-wu/RyTeITWU9Ra2bspc4D6tdV4jdFcHbXJgXNwFC+xg=";
            type = "tarball";
            url = "https://registry.npmjs.org/object-inspect/-/object-inspect-1.12.3.tgz";
          };
          ident = "object-inspect";
          ltype = "file";
          treeInfo = { };
          version = "1.12.3";
        };
      };
      object-keys = {
        "1.1.1" = {
          fetchInfo = {
            narHash = "sha256-+dy1F/wtvIQTjofLf3Di9Rn3vSDAWUPsn0YG2KMj0Is=";
            type = "tarball";
            url = "https://registry.npmjs.org/object-keys/-/object-keys-1.1.1.tgz";
          };
          ident = "object-keys";
          ltype = "file";
          treeInfo = { };
          version = "1.1.1";
        };
      };
      "object.assign" = {
        "4.1.4" = {
          depInfo = {
            call-bind = {
              descriptor = "^1.0.2";
              pin = "1.0.2";
              runtime = true;
            };
            define-properties = {
              descriptor = "^1.1.4";
              pin = "1.2.0";
              runtime = true;
            };
            has-symbols = {
              descriptor = "^1.0.3";
              pin = "1.0.3";
              runtime = true;
            };
            object-keys = {
              descriptor = "^1.1.1";
              pin = "1.1.1";
              runtime = true;
            };
          };
          fetchInfo = {
            narHash = "sha256-LRPf0GUtnnskbRHcm5RoTjwHW3WBHhusmHgapO1xJlY=";
            type = "tarball";
            url = "https://registry.npmjs.org/object.assign/-/object.assign-4.1.4.tgz";
          };
          ident = "object.assign";
          ltype = "file";
          version = "4.1.4";
        };
      };
      "object.entries" = {
        "1.1.6" = {
          depInfo = {
            call-bind = {
              descriptor = "^1.0.2";
              pin = "1.0.2";
              runtime = true;
            };
            define-properties = {
              descriptor = "^1.1.4";
              pin = "1.2.0";
              runtime = true;
            };
            es-abstract = {
              descriptor = "^1.20.4";
              pin = "1.22.1";
              runtime = true;
            };
          };
          fetchInfo = {
            narHash = "sha256-U4vEuu0EODNo4Wxqh3TdDfGXFtVvPtMuDu555fYuwAE=";
            type = "tarball";
            url = "https://registry.npmjs.org/object.entries/-/object.entries-1.1.6.tgz";
          };
          ident = "object.entries";
          ltype = "file";
          version = "1.1.6";
        };
      };
      "object.fromentries" = {
        "2.0.6" = {
          depInfo = {
            call-bind = {
              descriptor = "^1.0.2";
              pin = "1.0.2";
              runtime = true;
            };
            define-properties = {
              descriptor = "^1.1.4";
              pin = "1.2.0";
              runtime = true;
            };
            es-abstract = {
              descriptor = "^1.20.4";
              pin = "1.22.1";
              runtime = true;
            };
          };
          fetchInfo = {
            narHash = "sha256-qomWdBftnIM/0AVC78wy3ODaQSJPz0GAt6IRZoUDO00=";
            type = "tarball";
            url = "https://registry.npmjs.org/object.fromentries/-/object.fromentries-2.0.6.tgz";
          };
          ident = "object.fromentries";
          ltype = "file";
          version = "2.0.6";
        };
      };
      "object.groupby" = {
        "1.0.0" = {
          depInfo = {
            call-bind = {
              descriptor = "^1.0.2";
              pin = "1.0.2";
              runtime = true;
            };
            define-properties = {
              descriptor = "^1.2.0";
              pin = "1.2.0";
              runtime = true;
            };
            es-abstract = {
              descriptor = "^1.21.2";
              pin = "1.22.1";
              runtime = true;
            };
            get-intrinsic = {
              descriptor = "^1.2.1";
              pin = "1.2.1";
              runtime = true;
            };
          };
          fetchInfo = {
            narHash = "sha256-e4G8AO5zjw3yL6EbIL9o5SDbZAQGjbhFPhl/N6dZev0=";
            type = "tarball";
            url = "https://registry.npmjs.org/object.groupby/-/object.groupby-1.0.0.tgz";
          };
          ident = "object.groupby";
          ltype = "file";
          version = "1.0.0";
        };
      };
      "object.hasown" = {
        "1.1.2" = {
          depInfo = {
            define-properties = {
              descriptor = "^1.1.4";
              pin = "1.2.0";
              runtime = true;
            };
            es-abstract = {
              descriptor = "^1.20.4";
              pin = "1.22.1";
              runtime = true;
            };
          };
          fetchInfo = {
            narHash = "sha256-AFJRnavAkYUjVW+1ZDvq0JeFuXCmSrABAm75TuVCZSU=";
            type = "tarball";
            url = "https://registry.npmjs.org/object.hasown/-/object.hasown-1.1.2.tgz";
          };
          ident = "object.hasown";
          ltype = "file";
          version = "1.1.2";
        };
      };
      "object.values" = {
        "1.1.6" = {
          depInfo = {
            call-bind = {
              descriptor = "^1.0.2";
              pin = "1.0.2";
              runtime = true;
            };
            define-properties = {
              descriptor = "^1.1.4";
              pin = "1.2.0";
              runtime = true;
            };
            es-abstract = {
              descriptor = "^1.20.4";
              pin = "1.22.1";
              runtime = true;
            };
          };
          fetchInfo = {
            narHash = "sha256-dcKYzLvyFIzr4YpeMQGUmS5azmLAusP6dLPnl0uhzww=";
            type = "tarball";
            url = "https://registry.npmjs.org/object.values/-/object.values-1.1.6.tgz";
          };
          ident = "object.values";
          ltype = "file";
          version = "1.1.6";
        };
      };
      once = {
        "1.4.0" = {
          depInfo = {
            wrappy = {
              descriptor = "1";
              pin = "1.0.2";
              runtime = true;
            };
          };
          fetchInfo = {
            narHash = "sha256-2NvvDZICNRZJPY258mO8rrRBg4fY7mlMjFEl2R+m348=";
            type = "tarball";
            url = "https://registry.npmjs.org/once/-/once-1.4.0.tgz";
          };
          ident = "once";
          ltype = "file";
          version = "1.4.0";
        };
      };
      onetime = {
        "5.1.2" = {
          depInfo = {
            mimic-fn = {
              descriptor = "^2.1.0";
              pin = "2.1.0";
              runtime = true;
            };
          };
          fetchInfo = {
            narHash = "sha256-IlWxpAaeV+41VqHMcJLBSFazIsiYMEs5PrBtQGQyqrg=";
            type = "tarball";
            url = "https://registry.npmjs.org/onetime/-/onetime-5.1.2.tgz";
          };
          ident = "onetime";
          ltype = "file";
          version = "5.1.2";
        };
      };
      ono = {
        "4.0.11" = {
          depInfo = {
            format-util = {
              descriptor = "^1.0.3";
              pin = "1.0.5";
              runtime = true;
            };
          };
          fetchInfo = {
            narHash = "sha256-EgfsLJ003Phl4PUP/5pASgnuJ8VSdl5cbmGuKzSL5eE=";
            type = "tarball";
            url = "https://registry.npmjs.org/ono/-/ono-4.0.11.tgz";
          };
          ident = "ono";
          ltype = "file";
          version = "4.0.11";
        };
      };
      openapi-types = {
        "12.1.3" = {
          fetchInfo = {
            narHash = "sha256-zJ5CP8io8gp+TS1p3yxRM/LDTUvS3dFRFM0gFl+aKIE=";
            type = "tarball";
            url = "https://registry.npmjs.org/openapi-types/-/openapi-types-12.1.3.tgz";
          };
          ident = "openapi-types";
          ltype = "file";
          treeInfo = { };
          version = "12.1.3";
        };
      };
      openapi3-ts = {
        "3.2.0" = {
          depInfo = {
            yaml = {
              descriptor = "^2.2.1";
              pin = "2.3.1";
              runtime = true;
            };
          };
          fetchInfo = {
            narHash = "sha256-ZOp7oCC5G5JwoMhseyiukKlYqXvrr2rowIpRrHrj0MQ=";
            type = "tarball";
            url = "https://registry.npmjs.org/openapi3-ts/-/openapi3-ts-3.2.0.tgz";
          };
          ident = "openapi3-ts";
          ltype = "file";
          version = "3.2.0";
        };
      };
      optionator = {
        "0.9.3" = {
          depInfo = {
            "@aashutoshrathi/word-wrap" = {
              descriptor = "^1.2.3";
              pin = "1.2.6";
              runtime = true;
            };
            deep-is = {
              descriptor = "^0.1.3";
              pin = "0.1.4";
              runtime = true;
            };
            fast-levenshtein = {
              descriptor = "^2.0.6";
              pin = "2.0.6";
              runtime = true;
            };
            levn = {
              descriptor = "^0.4.1";
              pin = "0.4.1";
              runtime = true;
            };
            prelude-ls = {
              descriptor = "^1.2.1";
              pin = "1.2.1";
              runtime = true;
            };
            type-check = {
              descriptor = "^0.4.0";
              pin = "0.4.0";
              runtime = true;
            };
          };
          fetchInfo = {
            narHash = "sha256-KIkFMXhW+cbxs1mcsFmLoTB9x8M4ZWxwz+TB7Kgd2s4=";
            type = "tarball";
            url = "https://registry.npmjs.org/optionator/-/optionator-0.9.3.tgz";
          };
          ident = "optionator";
          ltype = "file";
          version = "0.9.3";
        };
      };
      orval = {
        "6.17.0" = {
          binInfo = {
            binPairs = {
              orval = "dist/bin/orval.js";
            };
          };
          depInfo = {
            "@apidevtools/swagger-parser" = {
              descriptor = "^10.1.0";
              pin = "10.1.0";
              runtime = true;
            };
            "@orval/angular" = {
              descriptor = "6.17.0";
              pin = "6.17.0";
              runtime = true;
            };
            "@orval/axios" = {
              descriptor = "6.17.0";
              pin = "6.17.0";
              runtime = true;
            };
            "@orval/core" = {
              descriptor = "6.17.0";
              pin = "6.17.0";
              runtime = true;
            };
            "@orval/msw" = {
              descriptor = "6.17.0";
              pin = "6.17.0";
              runtime = true;
            };
            "@orval/query" = {
              descriptor = "6.17.0";
              pin = "6.17.0";
              runtime = true;
            };
            "@orval/swr" = {
              descriptor = "6.17.0";
              pin = "6.17.0";
              runtime = true;
            };
            "@orval/zod" = {
              descriptor = "6.17.0";
              pin = "6.17.0";
              runtime = true;
            };
            ajv = {
              descriptor = "^8.11.0";
              pin = "8.12.0";
              runtime = true;
            };
            cac = {
              descriptor = "^6.7.12";
              pin = "6.7.14";
              runtime = true;
            };
            chalk = {
              descriptor = "^4.1.2";
              pin = "4.1.2";
              runtime = true;
            };
            chokidar = {
              descriptor = "^3.5.3";
              pin = "3.5.3";
              runtime = true;
            };
            enquirer = {
              descriptor = "^2.3.6";
              pin = "2.4.1";
              runtime = true;
            };
            execa = {
              descriptor = "^5.1.1";
              pin = "5.1.1";
              runtime = true;
            };
            find-up = {
              descriptor = "5.0.0";
              pin = "5.0.0";
              runtime = true;
            };
            fs-extra = {
              descriptor = "^10.1.0";
              pin = "10.1.0";
              runtime = true;
            };
            "lodash.uniq" = {
              descriptor = "^4.5.0";
              pin = "4.5.0";
              runtime = true;
            };
            openapi3-ts = {
              descriptor = "^3.0.0";
              pin = "3.2.0";
              runtime = true;
            };
            string-argv = {
              descriptor = "^0.3.1";
              pin = "0.3.2";
              runtime = true;
            };
            tsconfck = {
              descriptor = "^2.0.1";
              pin = "2.1.2";
              runtime = true;
            };
          };
          fetchInfo = {
            narHash = "sha256-Ce/TJyV+E/iWybQfnJglgfU3NWrhmn2QuDp7mtUCQoo=";
            type = "tarball";
            url = "https://registry.npmjs.org/orval/-/orval-6.17.0.tgz";
          };
          ident = "orval";
          ltype = "file";
          version = "6.17.0";
        };
      };
      p-limit = {
        "2.3.0" = {
          depInfo = {
            p-try = {
              descriptor = "^2.0.0";
              pin = "2.2.0";
              runtime = true;
            };
          };
          fetchInfo = {
            narHash = "sha256-7PNmPQsmrW5wFWP6LW8btESW7zOsfly2tYn6R/oXdPA=";
            type = "tarball";
            url = "https://registry.npmjs.org/p-limit/-/p-limit-2.3.0.tgz";
          };
          ident = "p-limit";
          ltype = "file";
          version = "2.3.0";
        };
        "3.1.0" = {
          depInfo = {
            yocto-queue = {
              descriptor = "^0.1.0";
              pin = "0.1.0";
              runtime = true;
            };
          };
          fetchInfo = {
            narHash = "sha256-AMCtIV7mGwSuZn7PDlsDCHQ4n/pm5S5WG4H1FJC/sR8=";
            type = "tarball";
            url = "https://registry.npmjs.org/p-limit/-/p-limit-3.1.0.tgz";
          };
          ident = "p-limit";
          ltype = "file";
          version = "3.1.0";
        };
      };
      p-locate = {
        "3.0.0" = {
          depInfo = {
            p-limit = {
              descriptor = "^2.0.0";
              pin = "2.3.0";
              runtime = true;
            };
          };
          fetchInfo = {
            narHash = "sha256-AwkvbOlL5bpUghe+DtWDg4tct048Ebo3koEgmgOtlFE=";
            type = "tarball";
            url = "https://registry.npmjs.org/p-locate/-/p-locate-3.0.0.tgz";
          };
          ident = "p-locate";
          ltype = "file";
          version = "3.0.0";
        };
        "5.0.0" = {
          depInfo = {
            p-limit = {
              descriptor = "^3.0.2";
              pin = "3.1.0";
              runtime = true;
            };
          };
          fetchInfo = {
            narHash = "sha256-trcSEXcZAqQr13/oSsJmVMRbMAMi6flvssbXHUsG9PY=";
            type = "tarball";
            url = "https://registry.npmjs.org/p-locate/-/p-locate-5.0.0.tgz";
          };
          ident = "p-locate";
          ltype = "file";
          version = "5.0.0";
        };
      };
      p-try = {
        "2.2.0" = {
          fetchInfo = {
            narHash = "sha256-qGxjcs9tIM3yrGOljhpcGxq08MuQAPaXo7Hape2dmyw=";
            type = "tarball";
            url = "https://registry.npmjs.org/p-try/-/p-try-2.2.0.tgz";
          };
          ident = "p-try";
          ltype = "file";
          treeInfo = { };
          version = "2.2.0";
        };
      };
      pad = {
        "2.3.0" = {
          depInfo = {
            wcwidth = {
              descriptor = "^1.0.1";
              pin = "1.0.1";
              runtime = true;
            };
          };
          fetchInfo = {
            narHash = "sha256-ueJDJtGLzZ09Mtd2nTMbN9KBunSo+FlnAwJag6vLfK4=";
            type = "tarball";
            url = "https://registry.npmjs.org/pad/-/pad-2.3.0.tgz";
          };
          ident = "pad";
          ltype = "file";
          version = "2.3.0";
        };
      };
      parent-module = {
        "1.0.1" = {
          depInfo = {
            callsites = {
              descriptor = "^3.0.0";
              pin = "3.1.0";
              runtime = true;
            };
          };
          fetchInfo = {
            narHash = "sha256-di+kefBp4+PYz6izBuMghrrb7tOQQfrW/7tMfibKBI8=";
            type = "tarball";
            url = "https://registry.npmjs.org/parent-module/-/parent-module-1.0.1.tgz";
          };
          ident = "parent-module";
          ltype = "file";
          version = "1.0.1";
        };
      };
      parse-json = {
        "5.2.0" = {
          depInfo = {
            "@babel/code-frame" = {
              descriptor = "^7.0.0";
              pin = "7.22.10";
              runtime = true;
            };
            error-ex = {
              descriptor = "^1.3.1";
              pin = "1.3.2";
              runtime = true;
            };
            json-parse-even-better-errors = {
              descriptor = "^2.3.0";
              pin = "2.3.1";
              runtime = true;
            };
            lines-and-columns = {
              descriptor = "^1.1.6";
              pin = "1.2.4";
              runtime = true;
            };
          };
          fetchInfo = {
            narHash = "sha256-hxVxyGV3iUu2t/nGE+bdgp9C38FU/lZU2iPbtazHLy4=";
            type = "tarball";
            url = "https://registry.npmjs.org/parse-json/-/parse-json-5.2.0.tgz";
          };
          ident = "parse-json";
          ltype = "file";
          version = "5.2.0";
        };
      };
      path-exists = {
        "3.0.0" = {
          fetchInfo = {
            narHash = "sha256-mRfy5SKmSH6Ns9jlgetqt+IAaj6hIHO/HcUvrdT1Nqs=";
            type = "tarball";
            url = "https://registry.npmjs.org/path-exists/-/path-exists-3.0.0.tgz";
          };
          ident = "path-exists";
          ltype = "file";
          treeInfo = { };
          version = "3.0.0";
        };
        "4.0.0" = {
          fetchInfo = {
            narHash = "sha256-QmsShSY8p68eX9bNeinv/8VO0/+P2c+Rv82mtPqtpjE=";
            type = "tarball";
            url = "https://registry.npmjs.org/path-exists/-/path-exists-4.0.0.tgz";
          };
          ident = "path-exists";
          ltype = "file";
          treeInfo = { };
          version = "4.0.0";
        };
      };
      path-is-absolute = {
        "1.0.1" = {
          fetchInfo = {
            narHash = "sha256-+DjPlEsONpIJ3kBveAhTRCV2aRZt3KN8RNLsgoC+jXk=";
            type = "tarball";
            url = "https://registry.npmjs.org/path-is-absolute/-/path-is-absolute-1.0.1.tgz";
          };
          ident = "path-is-absolute";
          ltype = "file";
          treeInfo = { };
          version = "1.0.1";
        };
      };
      path-key = {
        "3.1.1" = {
          fetchInfo = {
            narHash = "sha256-gj4CYT2AeZ5jyhV6m/eAq4pETAxmqd5kAcw/Iw0yxiI=";
            type = "tarball";
            url = "https://registry.npmjs.org/path-key/-/path-key-3.1.1.tgz";
          };
          ident = "path-key";
          ltype = "file";
          treeInfo = { };
          version = "3.1.1";
        };
      };
      path-parse = {
        "1.0.7" = {
          fetchInfo = {
            narHash = "sha256-IO0Y8yjZA6xJ63eLG/nFzWTGjI5tREyNKttz4DXoKYo=";
            type = "tarball";
            url = "https://registry.npmjs.org/path-parse/-/path-parse-1.0.7.tgz";
          };
          ident = "path-parse";
          ltype = "file";
          treeInfo = { };
          version = "1.0.7";
        };
      };
      path-type = {
        "4.0.0" = {
          fetchInfo = {
            narHash = "sha256-1ZtKKsM6jwAJslIh8ux8QgCyLpviZNMFpQJRjVnRxL4=";
            type = "tarball";
            url = "https://registry.npmjs.org/path-type/-/path-type-4.0.0.tgz";
          };
          ident = "path-type";
          ltype = "file";
          treeInfo = { };
          version = "4.0.0";
        };
      };
      picocolors = {
        "1.0.0" = {
          fetchInfo = {
            narHash = "sha256-zo0dDKQASSCpixflPOwG61jzA9IqjZMBN8dwojRu+l8=";
            type = "tarball";
            url = "https://registry.npmjs.org/picocolors/-/picocolors-1.0.0.tgz";
          };
          ident = "picocolors";
          ltype = "file";
          treeInfo = { };
          version = "1.0.0";
        };
      };
      picomatch = {
        "2.3.1" = {
          fetchInfo = {
            narHash = "sha256-8N7a/2Aei6DYLZ9EvhCEbdxTSTb5pmy0OqHYuN/IJac=";
            type = "tarball";
            url = "https://registry.npmjs.org/picomatch/-/picomatch-2.3.1.tgz";
          };
          ident = "picomatch";
          ltype = "file";
          treeInfo = { };
          version = "2.3.1";
        };
      };
      pify = {
        "2.3.0" = {
          fetchInfo = {
            narHash = "sha256-c++MxUctkx7igWbY+9CPJduQfusEULEeIb7B+mHyCE8=";
            type = "tarball";
            url = "https://registry.npmjs.org/pify/-/pify-2.3.0.tgz";
          };
          ident = "pify";
          ltype = "file";
          treeInfo = { };
          version = "2.3.0";
        };
      };
      pirates = {
        "4.0.6" = {
          fetchInfo = {
            narHash = "sha256-1D5F4EYUFcnXgnVISOqKkSt5EAYAfiUU710iM24fa4U=";
            type = "tarball";
            url = "https://registry.npmjs.org/pirates/-/pirates-4.0.6.tgz";
          };
          ident = "pirates";
          ltype = "file";
          treeInfo = { };
          version = "4.0.6";
        };
      };
      pony-cause = {
        "1.1.1" = {
          fetchInfo = {
            narHash = "sha256-PH5Bn5GluT1g6N4/uGChgtbIzUkvu3pFmFO5ea7CRyE=";
            type = "tarball";
            url = "https://registry.npmjs.org/pony-cause/-/pony-cause-1.1.1.tgz";
          };
          ident = "pony-cause";
          ltype = "file";
          treeInfo = { };
          version = "1.1.1";
        };
      };
      postcss = {
        "8.4.14" = {
          depInfo = {
            nanoid = {
              descriptor = "^3.3.4";
              pin = "3.3.6";
              runtime = true;
            };
            picocolors = {
              descriptor = "^1.0.0";
              pin = "1.0.0";
              runtime = true;
            };
            source-map-js = {
              descriptor = "^1.0.2";
              pin = "1.0.2";
              runtime = true;
            };
          };
          fetchInfo = {
            narHash = "sha256-Bf4PY1yCabPcvyfgY8lSN6uqK7E27LwlsJWDlpcbWGM=";
            type = "tarball";
            url = "https://registry.npmjs.org/postcss/-/postcss-8.4.14.tgz";
          };
          ident = "postcss";
          ltype = "file";
          version = "8.4.14";
        };
        "8.4.27" = {
          depInfo = {
            nanoid = {
              descriptor = "^3.3.6";
              pin = "3.3.6";
              runtime = true;
            };
            picocolors = {
              descriptor = "^1.0.0";
              pin = "1.0.0";
              runtime = true;
            };
            source-map-js = {
              descriptor = "^1.0.2";
              pin = "1.0.2";
              runtime = true;
            };
          };
          fetchInfo = {
            narHash = "sha256-wQzOJCWYqGunG75UTVW16dPcIBn5iBE/OHZFlE2XeRs=";
            type = "tarball";
            url = "https://registry.npmjs.org/postcss/-/postcss-8.4.27.tgz";
          };
          ident = "postcss";
          ltype = "file";
          version = "8.4.27";
        };
      };
      postcss-import = {
        "15.1.0" = {
          depInfo = {
            postcss-value-parser = {
              descriptor = "^4.0.0";
              pin = "4.2.0";
              runtime = true;
            };
            read-cache = {
              descriptor = "^1.0.0";
              pin = "1.0.0";
              runtime = true;
            };
            resolve = {
              descriptor = "^1.1.7";
              pin = "1.22.4";
              runtime = true;
            };
          };
          fetchInfo = {
            narHash = "sha256-BOGiGeZzKtS1AXkpfmGT+YOsBpIuGomVk5pPJUc1zMA=";
            type = "tarball";
            url = "https://registry.npmjs.org/postcss-import/-/postcss-import-15.1.0.tgz";
          };
          ident = "postcss-import";
          ltype = "file";
          peerInfo = {
            postcss = {
              descriptor = "^8.0.0";
            };
          };
          version = "15.1.0";
        };
      };
      postcss-js = {
        "4.0.1" = {
          depInfo = {
            camelcase-css = {
              descriptor = "^2.0.1";
              pin = "2.0.1";
              runtime = true;
            };
          };
          fetchInfo = {
            narHash = "sha256-TLaEzPP9pnahR6llQNOb5SMPzPwkTy72GmND6cRriT4=";
            type = "tarball";
            url = "https://registry.npmjs.org/postcss-js/-/postcss-js-4.0.1.tgz";
          };
          ident = "postcss-js";
          ltype = "file";
          peerInfo = {
            postcss = {
              descriptor = "^8.4.21";
            };
          };
          version = "4.0.1";
        };
      };
      postcss-load-config = {
        "4.0.1" = {
          depInfo = {
            lilconfig = {
              descriptor = "^2.0.5";
              pin = "2.1.0";
              runtime = true;
            };
            yaml = {
              descriptor = "^2.1.1";
              pin = "2.3.1";
              runtime = true;
            };
          };
          fetchInfo = {
            narHash = "sha256-RnP20SgI+qIPKWyMWAmmTN/TW5vt4dkVHD/IcS8dfks=";
            type = "tarball";
            url = "https://registry.npmjs.org/postcss-load-config/-/postcss-load-config-4.0.1.tgz";
          };
          ident = "postcss-load-config";
          ltype = "file";
          peerInfo = {
            postcss = {
              descriptor = ">=8.0.9";
              optional = true;
            };
            ts-node = {
              descriptor = ">=9.0.0";
              optional = true;
            };
          };
          version = "4.0.1";
        };
      };
      postcss-nested = {
        "6.0.1" = {
          depInfo = {
            postcss-selector-parser = {
              descriptor = "^6.0.11";
              pin = "6.0.13";
              runtime = true;
            };
          };
          fetchInfo = {
            narHash = "sha256-aFqkXAfaZd3MU0wb+P633ETKN8eh4xtFfDRUQkYRbCs=";
            type = "tarball";
            url = "https://registry.npmjs.org/postcss-nested/-/postcss-nested-6.0.1.tgz";
          };
          ident = "postcss-nested";
          ltype = "file";
          peerInfo = {
            postcss = {
              descriptor = "^8.2.14";
            };
          };
          version = "6.0.1";
        };
      };
      postcss-selector-parser = {
        "6.0.13" = {
          depInfo = {
            cssesc = {
              descriptor = "^3.0.0";
              pin = "3.0.0";
              runtime = true;
            };
            util-deprecate = {
              descriptor = "^1.0.2";
              pin = "1.0.2";
              runtime = true;
            };
          };
          fetchInfo = {
            narHash = "sha256-MSegul9y+ER3eSN8yi+I2qK0DRsydj2flQbtYVmcagI=";
            type = "tarball";
            url = "https://registry.npmjs.org/postcss-selector-parser/-/postcss-selector-parser-6.0.13.tgz";
          };
          ident = "postcss-selector-parser";
          ltype = "file";
          version = "6.0.13";
        };
      };
      postcss-value-parser = {
        "3.3.1" = {
          fetchInfo = {
            narHash = "sha256-pYN/lUhJz7K+hIgMd/Njg8X3o1npAFaVSfbv4Ysz7oI=";
            type = "tarball";
            url = "https://registry.npmjs.org/postcss-value-parser/-/postcss-value-parser-3.3.1.tgz";
          };
          ident = "postcss-value-parser";
          ltype = "file";
          treeInfo = { };
          version = "3.3.1";
        };
        "4.2.0" = {
          fetchInfo = {
            narHash = "sha256-5QJdBMm9vf0MTlnK3ayj0dJ9ij+TajeCZbsesvPXxug=";
            type = "tarball";
            url = "https://registry.npmjs.org/postcss-value-parser/-/postcss-value-parser-4.2.0.tgz";
          };
          ident = "postcss-value-parser";
          ltype = "file";
          treeInfo = { };
          version = "4.2.0";
        };
      };
      prelude-ls = {
        "1.2.1" = {
          fetchInfo = {
            narHash = "sha256-jC9FXbfy9euuL95bO+VZT03+rR3CqpwVKxBmj5hSYls=";
            type = "tarball";
            url = "https://registry.npmjs.org/prelude-ls/-/prelude-ls-1.2.1.tgz";
          };
          ident = "prelude-ls";
          ltype = "file";
          treeInfo = { };
          version = "1.2.1";
        };
      };
      prettier = {
        "3.0.1" = {
          binInfo = {
            binPairs = {
              prettier = "bin/prettier.cjs";
            };
          };
          fetchInfo = {
            narHash = "sha256-rgaO4WYmjoHtlOu8SnOau8b/O9lIEDtt26ovEY7qseY=";
            type = "tarball";
            url = "https://registry.npmjs.org/prettier/-/prettier-3.0.1.tgz";
          };
          ident = "prettier";
          ltype = "file";
          treeInfo = { };
          version = "3.0.1";
        };
      };
      prettier-plugin-tailwindcss = {
        "0.4.1" = {
          fetchInfo = {
            narHash = "sha256-39DJn6lvrLmDYTN/lXXuWzMC9pLI4+HNrhnHlYuOMRM=";
            type = "tarball";
            url = "https://registry.npmjs.org/prettier-plugin-tailwindcss/-/prettier-plugin-tailwindcss-0.4.1.tgz";
          };
          ident = "prettier-plugin-tailwindcss";
          ltype = "file";
          peerInfo = {
            "@ianvs/prettier-plugin-sort-imports" = {
              descriptor = "*";
              optional = true;
            };
            "@prettier/plugin-pug" = {
              descriptor = "*";
              optional = true;
            };
            "@shopify/prettier-plugin-liquid" = {
              descriptor = "*";
              optional = true;
            };
            "@shufo/prettier-plugin-blade" = {
              descriptor = "*";
              optional = true;
            };
            "@trivago/prettier-plugin-sort-imports" = {
              descriptor = "*";
              optional = true;
            };
            prettier = {
              descriptor = "^2.2 || ^3.0";
            };
            prettier-plugin-astro = {
              descriptor = "*";
              optional = true;
            };
            prettier-plugin-css-order = {
              descriptor = "*";
              optional = true;
            };
            prettier-plugin-import-sort = {
              descriptor = "*";
              optional = true;
            };
            prettier-plugin-jsdoc = {
              descriptor = "*";
              optional = true;
            };
            prettier-plugin-marko = {
              descriptor = "*";
              optional = true;
            };
            prettier-plugin-organize-attributes = {
              descriptor = "*";
              optional = true;
            };
            prettier-plugin-organize-imports = {
              descriptor = "*";
              optional = true;
            };
            prettier-plugin-style-order = {
              descriptor = "*";
              optional = true;
            };
            prettier-plugin-svelte = {
              descriptor = "*";
              optional = true;
            };
            prettier-plugin-twig-melody = {
              descriptor = "*";
              optional = true;
            };
          };
          treeInfo = { };
          version = "0.4.1";
        };
      };
      printable-characters = {
        "1.0.42" = {
          fetchInfo = {
            narHash = "sha256-unX8xPDZprlU9WUPK5Lyuow31XJucZsYAC/C/EBsGAM=";
            type = "tarball";
            url = "https://registry.npmjs.org/printable-characters/-/printable-characters-1.0.42.tgz";
          };
          ident = "printable-characters";
          ltype = "file";
          treeInfo = { };
          version = "1.0.42";
        };
      };
      prop-types = {
        "15.8.1" = {
          depInfo = {
            loose-envify = {
              descriptor = "^1.4.0";
              pin = "1.4.0";
              runtime = true;
            };
            object-assign = {
              descriptor = "^4.1.1";
              pin = "4.1.1";
              runtime = true;
            };
            react-is = {
              descriptor = "^16.13.1";
              pin = "16.13.1";
              runtime = true;
            };
          };
          fetchInfo = {
            narHash = "sha256-LfGJAVpvlP48OlCxprPHi3B88Wczi+luuJ9wEQmtqWs=";
            type = "tarball";
            url = "https://registry.npmjs.org/prop-types/-/prop-types-15.8.1.tgz";
          };
          ident = "prop-types";
          ltype = "file";
          version = "15.8.1";
        };
      };
      proxy-from-env = {
        "1.1.0" = {
          fetchInfo = {
            narHash = "sha256-hWI48SYmBlNnhQgUK/v05p6WiZDu2+UaemuGKrb16g8=";
            type = "tarball";
            url = "https://registry.npmjs.org/proxy-from-env/-/proxy-from-env-1.1.0.tgz";
          };
          ident = "proxy-from-env";
          ltype = "file";
          treeInfo = { };
          version = "1.1.0";
        };
      };
      punycode = {
        "2.3.0" = {
          fetchInfo = {
            narHash = "sha256-KVHAdIKAV7xPRhb1ae9NZ0dwfOVMPUHK/TA4qAx9o48=";
            type = "tarball";
            url = "https://registry.npmjs.org/punycode/-/punycode-2.3.0.tgz";
          };
          ident = "punycode";
          ltype = "file";
          treeInfo = { };
          version = "2.3.0";
        };
      };
      queue-microtask = {
        "1.2.3" = {
          fetchInfo = {
            narHash = "sha256-toA5eXCuEXuopI11sr2erVOgFPTNlS3krZO/l7Ob2CQ=";
            type = "tarball";
            url = "https://registry.npmjs.org/queue-microtask/-/queue-microtask-1.2.3.tgz";
          };
          ident = "queue-microtask";
          ltype = "file";
          treeInfo = { };
          version = "1.2.3";
        };
      };
      react = {
        "18.2.0" = {
          depInfo = {
            loose-envify = {
              descriptor = "^1.1.0";
              pin = "1.4.0";
              runtime = true;
            };
          };
          fetchInfo = {
            narHash = "sha256-xu467N3gZPKlkRpCGepCleV8dYW1zlZFTWTypSzAJnY=";
            type = "tarball";
            url = "https://registry.npmjs.org/react/-/react-18.2.0.tgz";
          };
          ident = "react";
          ltype = "file";
          version = "18.2.0";
        };
      };
      react-dom = {
        "18.2.0" = {
          depInfo = {
            loose-envify = {
              descriptor = "^1.1.0";
              pin = "1.4.0";
              runtime = true;
            };
            scheduler = {
              descriptor = "^0.23.0";
              pin = "0.23.0";
              runtime = true;
            };
          };
          fetchInfo = {
            narHash = "sha256-HDf0V4CIsZPnNqNr2YpXvyGY1wwI+wDrvJ/VO0CDSbw=";
            type = "tarball";
            url = "https://registry.npmjs.org/react-dom/-/react-dom-18.2.0.tgz";
          };
          ident = "react-dom";
          ltype = "file";
          peerInfo = {
            react = {
              descriptor = "^18.2.0";
            };
          };
          version = "18.2.0";
        };
      };
      react-hook-form = {
        "7.45.4" = {
          fetchInfo = {
            narHash = "sha256-1KTcjCunLhoFE9YSufzf4K8APHin0cGMsElm26sY5wc=";
            type = "tarball";
            url = "https://registry.npmjs.org/react-hook-form/-/react-hook-form-7.45.4.tgz";
          };
          ident = "react-hook-form";
          ltype = "file";
          peerInfo = {
            react = {
              descriptor = "^16.8.0 || ^17 || ^18";
            };
          };
          treeInfo = { };
          version = "7.45.4";
        };
      };
      react-hot-toast = {
        "2.4.1" = {
          depInfo = {
            goober = {
              descriptor = "^2.1.10";
              pin = "2.1.13";
              runtime = true;
            };
          };
          fetchInfo = {
            narHash = "sha256-seRTGGyQWjwU+PNqAU71f8sLus509310whSQ4xNKs4Q=";
            type = "tarball";
            url = "https://registry.npmjs.org/react-hot-toast/-/react-hot-toast-2.4.1.tgz";
          };
          ident = "react-hot-toast";
          ltype = "file";
          peerInfo = {
            react = {
              descriptor = ">=16";
            };
            react-dom = {
              descriptor = ">=16";
            };
          };
          version = "2.4.1";
        };
      };
      react-is = {
        "16.13.1" = {
          fetchInfo = {
            narHash = "sha256-84sHi9+fCX1q22phJuI2fsbjQQXoHXeAQTa3jmKsw/U=";
            type = "tarball";
            url = "https://registry.npmjs.org/react-is/-/react-is-16.13.1.tgz";
          };
          ident = "react-is";
          ltype = "file";
          treeInfo = { };
          version = "16.13.1";
        };
        "18.2.0" = {
          fetchInfo = {
            narHash = "sha256-eSOGsY/IVNB/U36bUYaUctK4n5DEM9hmzm1keaypG2c=";
            type = "tarball";
            url = "https://registry.npmjs.org/react-is/-/react-is-18.2.0.tgz";
          };
          ident = "react-is";
          ltype = "file";
          treeInfo = { };
          version = "18.2.0";
        };
      };
      react-lifecycles-compat = {
        "3.0.4" = {
          fetchInfo = {
            narHash = "sha256-XHLO6U5lwgBNKcuglPA22YDxh65I5OrvzJUAYXbophs=";
            type = "tarball";
            url = "https://registry.npmjs.org/react-lifecycles-compat/-/react-lifecycles-compat-3.0.4.tgz";
          };
          ident = "react-lifecycles-compat";
          ltype = "file";
          treeInfo = { };
          version = "3.0.4";
        };
      };
      react-resize-detector = {
        "8.1.0" = {
          depInfo = {
            lodash = {
              descriptor = "^4.17.21";
              pin = "4.17.21";
              runtime = true;
            };
          };
          fetchInfo = {
            narHash = "sha256-eJLM8qrCEqXas4OIMV4K7xE4PABkNA+CBNbHo7OTeJE=";
            type = "tarball";
            url = "https://registry.npmjs.org/react-resize-detector/-/react-resize-detector-8.1.0.tgz";
          };
          ident = "react-resize-detector";
          ltype = "file";
          peerInfo = {
            react = {
              descriptor = "^16.0.0 || ^17.0.0 || ^18.0.0";
            };
            react-dom = {
              descriptor = "^16.0.0 || ^17.0.0 || ^18.0.0";
            };
          };
          version = "8.1.0";
        };
      };
      react-smooth = {
        "2.0.3" = {
          depInfo = {
            fast-equals = {
              descriptor = "^5.0.0";
              pin = "5.0.1";
              runtime = true;
            };
            react-transition-group = {
              descriptor = "2.9.0";
              pin = "2.9.0";
              runtime = true;
            };
          };
          fetchInfo = {
            narHash = "sha256-G/FZfs/lgqomfdB9q9tjoaVNwnMGX8osCOLjoRc6oyI=";
            type = "tarball";
            url = "https://registry.npmjs.org/react-smooth/-/react-smooth-2.0.3.tgz";
          };
          ident = "react-smooth";
          ltype = "file";
          peerInfo = {
            prop-types = {
              descriptor = "^15.6.0";
            };
            react = {
              descriptor = "^15.0.0 || ^16.0.0 || ^17.0.0 || ^18.0.0";
            };
            react-dom = {
              descriptor = "^15.0.0 || ^16.0.0 || ^17.0.0 || ^18.0.0";
            };
          };
          version = "2.0.3";
        };
      };
      react-transition-group = {
        "2.9.0" = {
          depInfo = {
            dom-helpers = {
              descriptor = "^3.4.0";
              pin = "3.4.0";
              runtime = true;
            };
            loose-envify = {
              descriptor = "^1.4.0";
              pin = "1.4.0";
              runtime = true;
            };
            prop-types = {
              descriptor = "^15.6.2";
              pin = "15.8.1";
              runtime = true;
            };
            react-lifecycles-compat = {
              descriptor = "^3.0.4";
              pin = "3.0.4";
              runtime = true;
            };
          };
          fetchInfo = {
            narHash = "sha256-zvvpBDdYSkf3ApCuY/k9uvRXLjRuVekmrgTLo3zLOQ4=";
            type = "tarball";
            url = "https://registry.npmjs.org/react-transition-group/-/react-transition-group-2.9.0.tgz";
          };
          ident = "react-transition-group";
          ltype = "file";
          peerInfo = {
            react = {
              descriptor = ">=15.0.0";
            };
            react-dom = {
              descriptor = ">=15.0.0";
            };
          };
          version = "2.9.0";
        };
        "4.4.5" = {
          depInfo = {
            "@babel/runtime" = {
              descriptor = "^7.5.5";
              pin = "7.22.10";
              runtime = true;
            };
            dom-helpers = {
              descriptor = "^5.0.1";
              pin = "5.2.1";
              runtime = true;
            };
            loose-envify = {
              descriptor = "^1.4.0";
              pin = "1.4.0";
              runtime = true;
            };
            prop-types = {
              descriptor = "^15.6.2";
              pin = "15.8.1";
              runtime = true;
            };
          };
          fetchInfo = {
            narHash = "sha256-rxK890I79kcB9FwueWOWluR5hIg7XFq0nvxWwRA30e0=";
            type = "tarball";
            url = "https://registry.npmjs.org/react-transition-group/-/react-transition-group-4.4.5.tgz";
          };
          ident = "react-transition-group";
          ltype = "file";
          peerInfo = {
            react = {
              descriptor = ">=16.6.0";
            };
            react-dom = {
              descriptor = ">=16.6.0";
            };
          };
          version = "4.4.5";
        };
      };
      read-cache = {
        "1.0.0" = {
          depInfo = {
            pify = {
              descriptor = "^2.3.0";
              pin = "2.3.0";
              runtime = true;
            };
          };
          fetchInfo = {
            narHash = "sha256-WmFTvXvWdsv/OwKjXqw1cf1m9vx7878GgSyhMESO75I=";
            type = "tarball";
            url = "https://registry.npmjs.org/read-cache/-/read-cache-1.0.0.tgz";
          };
          ident = "read-cache";
          ltype = "file";
          version = "1.0.0";
        };
      };
      readdirp = {
        "3.6.0" = {
          depInfo = {
            picomatch = {
              descriptor = "^2.2.1";
              pin = "2.3.1";
              runtime = true;
            };
          };
          fetchInfo = {
            narHash = "sha256-MpmVWT8izPROQ0Z1uwPFUP6CBTg3Hl+T0O+wJsdxWBY=";
            type = "tarball";
            url = "https://registry.npmjs.org/readdirp/-/readdirp-3.6.0.tgz";
          };
          ident = "readdirp";
          ltype = "file";
          version = "3.6.0";
        };
      };
      recharts = {
        "2.7.3" = {
          depInfo = {
            classnames = {
              descriptor = "^2.2.5";
              pin = "2.3.2";
              runtime = true;
            };
            eventemitter3 = {
              descriptor = "^4.0.1";
              pin = "4.0.7";
              runtime = true;
            };
            lodash = {
              descriptor = "^4.17.19";
              pin = "4.17.21";
              runtime = true;
            };
            react-is = {
              descriptor = "^16.10.2";
              pin = "16.13.1";
              runtime = true;
            };
            react-resize-detector = {
              descriptor = "^8.0.4";
              pin = "8.1.0";
              runtime = true;
            };
            react-smooth = {
              descriptor = "^2.0.2";
              pin = "2.0.3";
              runtime = true;
            };
            recharts-scale = {
              descriptor = "^0.4.4";
              pin = "0.4.5";
              runtime = true;
            };
            reduce-css-calc = {
              descriptor = "^2.1.8";
              pin = "2.1.8";
              runtime = true;
            };
            victory-vendor = {
              descriptor = "^36.6.8";
              pin = "36.6.11";
              runtime = true;
            };
          };
          fetchInfo = {
            narHash = "sha256-Rb3A7lTS0oCO/Gp/DcGf38UL3orV7aCfavnVdpKbHEM=";
            type = "tarball";
            url = "https://registry.npmjs.org/recharts/-/recharts-2.7.3.tgz";
          };
          ident = "recharts";
          ltype = "file";
          peerInfo = {
            prop-types = {
              descriptor = "^15.6.0";
            };
            react = {
              descriptor = "^16.0.0 || ^17.0.0 || ^18.0.0";
            };
            react-dom = {
              descriptor = "^16.0.0 || ^17.0.0 || ^18.0.0";
            };
          };
          version = "2.7.3";
        };
      };
      recharts-scale = {
        "0.4.5" = {
          depInfo = {
            "decimal.js-light" = {
              descriptor = "^2.4.1";
              pin = "2.5.1";
              runtime = true;
            };
          };
          fetchInfo = {
            narHash = "sha256-dFsJKknOkkuwpPDqF5iFbbjhVVO9FT/cIzSCberRPdQ=";
            type = "tarball";
            url = "https://registry.npmjs.org/recharts-scale/-/recharts-scale-0.4.5.tgz";
          };
          ident = "recharts-scale";
          ltype = "file";
          version = "0.4.5";
        };
      };
      reduce-css-calc = {
        "2.1.8" = {
          depInfo = {
            css-unit-converter = {
              descriptor = "^1.1.1";
              pin = "1.1.2";
              runtime = true;
            };
            postcss-value-parser = {
              descriptor = "^3.3.0";
              pin = "3.3.1";
              runtime = true;
            };
          };
          fetchInfo = {
            narHash = "sha256-kMSRxzkJThER3joDq68H++0FIEafFYMVzx5+J3sAGbI=";
            type = "tarball";
            url = "https://registry.npmjs.org/reduce-css-calc/-/reduce-css-calc-2.1.8.tgz";
          };
          ident = "reduce-css-calc";
          ltype = "file";
          version = "2.1.8";
        };
      };
      reftools = {
        "1.1.9" = {
          fetchInfo = {
            narHash = "sha256-o3ewKEBU+h8PRvvnViKOS61nBja7hC3Sl3nd9NsA8/k=";
            type = "tarball";
            url = "https://registry.npmjs.org/reftools/-/reftools-1.1.9.tgz";
          };
          ident = "reftools";
          ltype = "file";
          treeInfo = { };
          version = "1.1.9";
        };
      };
      regenerator-runtime = {
        "0.14.0" = {
          fetchInfo = {
            narHash = "sha256-dQQ+7V/uRRNdQZb5XniSHWCfY5VIwOrYFC1iUFBjEh4=";
            type = "tarball";
            url = "https://registry.npmjs.org/regenerator-runtime/-/regenerator-runtime-0.14.0.tgz";
          };
          ident = "regenerator-runtime";
          ltype = "file";
          treeInfo = { };
          version = "0.14.0";
        };
      };
      "regexp.prototype.flags" = {
        "1.5.0" = {
          depInfo = {
            call-bind = {
              descriptor = "^1.0.2";
              pin = "1.0.2";
              runtime = true;
            };
            define-properties = {
              descriptor = "^1.2.0";
              pin = "1.2.0";
              runtime = true;
            };
            functions-have-names = {
              descriptor = "^1.2.3";
              pin = "1.2.3";
              runtime = true;
            };
          };
          fetchInfo = {
            narHash = "sha256-pEe+nnF52N/a73ioro0a9zQ8s846lNj/gbPxqUh42hM=";
            type = "tarball";
            url = "https://registry.npmjs.org/regexp.prototype.flags/-/regexp.prototype.flags-1.5.0.tgz";
          };
          ident = "regexp.prototype.flags";
          ltype = "file";
          version = "1.5.0";
        };
      };
      require-all = {
        "3.0.0" = {
          fetchInfo = {
            narHash = "sha256-bTLwdk+CgvC6448X7yb4S8ixXCO7PcNSsUtaVwJGTAU=";
            type = "tarball";
            url = "https://registry.npmjs.org/require-all/-/require-all-3.0.0.tgz";
          };
          ident = "require-all";
          ltype = "file";
          treeInfo = { };
          version = "3.0.0";
        };
      };
      require-directory = {
        "2.1.1" = {
          fetchInfo = {
            narHash = "sha256-nAP28KKDIP7JZZfCTBI0EHdJcuAa6hsYOVfXNdVn7xY=";
            type = "tarball";
            url = "https://registry.npmjs.org/require-directory/-/require-directory-2.1.1.tgz";
          };
          ident = "require-directory";
          ltype = "file";
          treeInfo = { };
          version = "2.1.1";
        };
      };
      require-from-string = {
        "2.0.2" = {
          fetchInfo = {
            narHash = "sha256-R0m+cS25k7csaqHl5tWyBoImM7R1Ru7tHSX3SVI6XqI=";
            type = "tarball";
            url = "https://registry.npmjs.org/require-from-string/-/require-from-string-2.0.2.tgz";
          };
          ident = "require-from-string";
          ltype = "file";
          treeInfo = { };
          version = "2.0.2";
        };
      };
      reserved = {
        "0.1.2" = {
          fetchInfo = {
            narHash = "sha256-+yUItSE/0HYIbiyfw5YYZ/aWgE0dQ10yeguh+6G/y8g=";
            type = "tarball";
            url = "https://registry.npmjs.org/reserved/-/reserved-0.1.2.tgz";
          };
          ident = "reserved";
          ltype = "file";
          treeInfo = { };
          version = "0.1.2";
        };
      };
      resolve = {
        "1.22.4" = {
          binInfo = {
            binPairs = {
              resolve = "bin/resolve";
            };
          };
          depInfo = {
            is-core-module = {
              descriptor = "^2.13.0";
              pin = "2.13.0";
              runtime = true;
            };
            path-parse = {
              descriptor = "^1.0.7";
              pin = "1.0.7";
              runtime = true;
            };
            supports-preserve-symlinks-flag = {
              descriptor = "^1.0.0";
              pin = "1.0.0";
              runtime = true;
            };
          };
          fetchInfo = {
            narHash = "sha256-rhvJBIMvXjHbzslSRUWJg+CT7NKLJMuCWgm6mKQrVB0=";
            type = "tarball";
            url = "https://registry.npmjs.org/resolve/-/resolve-1.22.4.tgz";
          };
          ident = "resolve";
          ltype = "file";
          version = "1.22.4";
        };
        "2.0.0-next.4" = {
          binInfo = {
            binPairs = {
              resolve = "bin/resolve";
            };
          };
          depInfo = {
            is-core-module = {
              descriptor = "^2.9.0";
              pin = "2.13.0";
              runtime = true;
            };
            path-parse = {
              descriptor = "^1.0.7";
              pin = "1.0.7";
              runtime = true;
            };
            supports-preserve-symlinks-flag = {
              descriptor = "^1.0.0";
              pin = "1.0.0";
              runtime = true;
            };
          };
          fetchInfo = {
            narHash = "sha256-Ljjrw8eKPK1aGtqcxFQfwccOIRJTP68XIgR38vkPunc=";
            type = "tarball";
            url = "https://registry.npmjs.org/resolve/-/resolve-2.0.0-next.4.tgz";
          };
          ident = "resolve";
          ltype = "file";
          version = "2.0.0-next.4";
        };
      };
      resolve-from = {
        "4.0.0" = {
          fetchInfo = {
            narHash = "sha256-nD9AJZmCaf+wEw0JYsv2/4VWsD1nFdSK+pwFWFiRf5M=";
            type = "tarball";
            url = "https://registry.npmjs.org/resolve-from/-/resolve-from-4.0.0.tgz";
          };
          ident = "resolve-from";
          ltype = "file";
          treeInfo = { };
          version = "4.0.0";
        };
      };
      resolve-pkg-maps = {
        "1.0.0" = {
          fetchInfo = {
            narHash = "sha256-WhDCNuft7AEjoatAOEQOHp17eYsaft0BFCkgDRPRwNQ=";
            type = "tarball";
            url = "https://registry.npmjs.org/resolve-pkg-maps/-/resolve-pkg-maps-1.0.0.tgz";
          };
          ident = "resolve-pkg-maps";
          ltype = "file";
          treeInfo = { };
          version = "1.0.0";
        };
      };
      reusify = {
        "1.0.4" = {
          fetchInfo = {
            narHash = "sha256-WKyHwdjM4zpbJDXA61+Ixsv1uY418K36PcjbZfua5fY=";
            type = "tarball";
            url = "https://registry.npmjs.org/reusify/-/reusify-1.0.4.tgz";
          };
          ident = "reusify";
          ltype = "file";
          treeInfo = { };
          version = "1.0.4";
        };
      };
      rimraf = {
        "3.0.2" = {
          binInfo = {
            binPairs = {
              rimraf = "bin.js";
            };
          };
          depInfo = {
            glob = {
              descriptor = "^7.1.3";
              pin = "7.1.7";
              runtime = true;
            };
          };
          fetchInfo = {
            narHash = "sha256-5ZflqftTdzdyQtoHawWDKLP29TBYks2sneUZTaH6VJM=";
            type = "tarball";
            url = "https://registry.npmjs.org/rimraf/-/rimraf-3.0.2.tgz";
          };
          ident = "rimraf";
          ltype = "file";
          version = "3.0.2";
        };
      };
      rollup = {
        "2.79.1" = {
          binInfo = {
            binPairs = {
              rollup = "dist/bin/rollup";
            };
          };
          depInfo = {
            fsevents = {
              descriptor = "~2.3.2";
              optional = true;
              pin = "2.3.2";
              runtime = true;
            };
          };
          fetchInfo = {
            narHash = "sha256-z0EkOqloUFcURhTX11cb5s1aGKjhzH6Y5t01Mab0OOk=";
            type = "tarball";
            url = "https://registry.npmjs.org/rollup/-/rollup-2.79.1.tgz";
          };
          ident = "rollup";
          ltype = "file";
          version = "2.79.1";
        };
      };
      run-parallel = {
        "1.2.0" = {
          depInfo = {
            queue-microtask = {
              descriptor = "^1.2.2";
              pin = "1.2.3";
              runtime = true;
            };
          };
          fetchInfo = {
            narHash = "sha256-u5XLCbdOHvL+vVMeQBK5Ha1Y/ZkdCSQM9X8KZL4EvsM=";
            type = "tarball";
            url = "https://registry.npmjs.org/run-parallel/-/run-parallel-1.2.0.tgz";
          };
          ident = "run-parallel";
          ltype = "file";
          version = "1.2.0";
        };
      };
      safe-array-concat = {
        "1.0.0" = {
          depInfo = {
            call-bind = {
              descriptor = "^1.0.2";
              pin = "1.0.2";
              runtime = true;
            };
            get-intrinsic = {
              descriptor = "^1.2.0";
              pin = "1.2.1";
              runtime = true;
            };
            has-symbols = {
              descriptor = "^1.0.3";
              pin = "1.0.3";
              runtime = true;
            };
            isarray = {
              descriptor = "^2.0.5";
              pin = "2.0.5";
              runtime = true;
            };
          };
          fetchInfo = {
            narHash = "sha256-c1g5sEeL0TZLyduNXlRYa9J2KZNrZzTR0a/OtDdAnmw=";
            type = "tarball";
            url = "https://registry.npmjs.org/safe-array-concat/-/safe-array-concat-1.0.0.tgz";
          };
          ident = "safe-array-concat";
          ltype = "file";
          version = "1.0.0";
        };
      };
      safe-regex-test = {
        "1.0.0" = {
          depInfo = {
            call-bind = {
              descriptor = "^1.0.2";
              pin = "1.0.2";
              runtime = true;
            };
            get-intrinsic = {
              descriptor = "^1.1.3";
              pin = "1.2.1";
              runtime = true;
            };
            is-regex = {
              descriptor = "^1.1.4";
              pin = "1.1.4";
              runtime = true;
            };
          };
          fetchInfo = {
            narHash = "sha256-t4WUzmIn1J/dQmvCgstUBe2IhPGsjPJ6puiyNHFDwE0=";
            type = "tarball";
            url = "https://registry.npmjs.org/safe-regex-test/-/safe-regex-test-1.0.0.tgz";
          };
          ident = "safe-regex-test";
          ltype = "file";
          version = "1.0.0";
        };
      };
      safe-stable-stringify = {
        "1.1.1" = {
          fetchInfo = {
            narHash = "sha256-wvQ7CXG6pnOmaK/EUnMTZOvGaCSy3fIzovYvQav8sbM=";
            type = "tarball";
            url = "https://registry.npmjs.org/safe-stable-stringify/-/safe-stable-stringify-1.1.1.tgz";
          };
          ident = "safe-stable-stringify";
          ltype = "file";
          treeInfo = { };
          version = "1.1.1";
        };
      };
      scheduler = {
        "0.23.0" = {
          depInfo = {
            loose-envify = {
              descriptor = "^1.1.0";
              pin = "1.4.0";
              runtime = true;
            };
          };
          fetchInfo = {
            narHash = "sha256-MkP/d5ZP19g52SJ9CyyLfE6TZWT1h7CLzTgVbuaWYcQ=";
            type = "tarball";
            url = "https://registry.npmjs.org/scheduler/-/scheduler-0.23.0.tgz";
          };
          ident = "scheduler";
          ltype = "file";
          version = "0.23.0";
        };
      };
      semver = {
        "5.7.2" = {
          binInfo = {
            binPairs = {
              semver = "bin/semver";
            };
          };
          fetchInfo = {
            narHash = "sha256-K+AnH5MbdkMm92SAjpOL2yMNwjevpyt7se03l1MXoT4=";
            type = "tarball";
            url = "https://registry.npmjs.org/semver/-/semver-5.7.2.tgz";
          };
          ident = "semver";
          ltype = "file";
          treeInfo = { };
          version = "5.7.2";
        };
        "6.3.1" = {
          binInfo = {
            binPairs = {
              semver = "bin/semver.js";
            };
          };
          fetchInfo = {
            narHash = "sha256-MQRm3hmLzbMAUnG+ciAtmx+grQjBQwAMQTdD3jGqUKU=";
            type = "tarball";
            url = "https://registry.npmjs.org/semver/-/semver-6.3.1.tgz";
          };
          ident = "semver";
          ltype = "file";
          treeInfo = { };
          version = "6.3.1";
        };
        "7.5.4" = {
          binInfo = {
            binPairs = {
              semver = "bin/semver.js";
            };
          };
          depInfo = {
            lru-cache = {
              descriptor = "^6.0.0";
              pin = "6.0.0";
              runtime = true;
            };
          };
          fetchInfo = {
            narHash = "sha256-x60C+6mtJ77+PYZO2beSGkjhFxgTYVZGLGXJdYKv4hQ=";
            type = "tarball";
            url = "https://registry.npmjs.org/semver/-/semver-7.5.4.tgz";
          };
          ident = "semver";
          ltype = "file";
          version = "7.5.4";
        };
      };
      shebang-command = {
        "2.0.0" = {
          depInfo = {
            shebang-regex = {
              descriptor = "^3.0.0";
              pin = "3.0.0";
              runtime = true;
            };
          };
          fetchInfo = {
            narHash = "sha256-hQ8ZmBxEUTBeAoFsrXtJSMXkxZPNJhOEvKatEpvbpaE=";
            type = "tarball";
            url = "https://registry.npmjs.org/shebang-command/-/shebang-command-2.0.0.tgz";
          };
          ident = "shebang-command";
          ltype = "file";
          version = "2.0.0";
        };
      };
      shebang-regex = {
        "3.0.0" = {
          fetchInfo = {
            narHash = "sha256-20gU7k4uzL2AgOQ9iw2L1KH8sC6GaQCZtjyUBY5ayQ0=";
            type = "tarball";
            url = "https://registry.npmjs.org/shebang-regex/-/shebang-regex-3.0.0.tgz";
          };
          ident = "shebang-regex";
          ltype = "file";
          treeInfo = { };
          version = "3.0.0";
        };
      };
      should = {
        "13.2.3" = {
          depInfo = {
            should-equal = {
              descriptor = "^2.0.0";
              pin = "2.0.0";
              runtime = true;
            };
            should-format = {
              descriptor = "^3.0.3";
              pin = "3.0.3";
              runtime = true;
            };
            should-type = {
              descriptor = "^1.4.0";
              pin = "1.4.0";
              runtime = true;
            };
            should-type-adaptors = {
              descriptor = "^1.0.1";
              pin = "1.1.0";
              runtime = true;
            };
            should-util = {
              descriptor = "^1.0.0";
              pin = "1.0.1";
              runtime = true;
            };
          };
          fetchInfo = {
            narHash = "sha256-XXQQmhZ9VfHf63MsLjRrYeM1So7O76gK3kS9m4ibn5M=";
            type = "tarball";
            url = "https://registry.npmjs.org/should/-/should-13.2.3.tgz";
          };
          ident = "should";
          ltype = "file";
          version = "13.2.3";
        };
      };
      should-equal = {
        "2.0.0" = {
          depInfo = {
            should-type = {
              descriptor = "^1.4.0";
              pin = "1.4.0";
              runtime = true;
            };
          };
          fetchInfo = {
            narHash = "sha256-8qfOCzx55EfI1kXmZHmMGdBJyKbtDtafq0YbLqj9uDc=";
            type = "tarball";
            url = "https://registry.npmjs.org/should-equal/-/should-equal-2.0.0.tgz";
          };
          ident = "should-equal";
          ltype = "file";
          version = "2.0.0";
        };
      };
      should-format = {
        "3.0.3" = {
          depInfo = {
            should-type = {
              descriptor = "^1.3.0";
              pin = "1.4.0";
              runtime = true;
            };
            should-type-adaptors = {
              descriptor = "^1.0.1";
              pin = "1.1.0";
              runtime = true;
            };
          };
          fetchInfo = {
            narHash = "sha256-7AdOB2Eh1HL5ZUlnCb52O/1ZIfL+NeE9F/zw1G8hyn8=";
            type = "tarball";
            url = "https://registry.npmjs.org/should-format/-/should-format-3.0.3.tgz";
          };
          ident = "should-format";
          ltype = "file";
          version = "3.0.3";
        };
      };
      should-type = {
        "1.4.0" = {
          fetchInfo = {
            narHash = "sha256-Z/KKvEbn5KlsJtRqPDeLt5YzrPeoTTV6ngCUbN1QZIE=";
            type = "tarball";
            url = "https://registry.npmjs.org/should-type/-/should-type-1.4.0.tgz";
          };
          ident = "should-type";
          ltype = "file";
          treeInfo = { };
          version = "1.4.0";
        };
      };
      should-type-adaptors = {
        "1.1.0" = {
          depInfo = {
            should-type = {
              descriptor = "^1.3.0";
              pin = "1.4.0";
              runtime = true;
            };
            should-util = {
              descriptor = "^1.0.0";
              pin = "1.0.1";
              runtime = true;
            };
          };
          fetchInfo = {
            narHash = "sha256-4RvGTYsWB6pWg7XNdTHPOndebQnkGuMqW9iohor0gQo=";
            type = "tarball";
            url = "https://registry.npmjs.org/should-type-adaptors/-/should-type-adaptors-1.1.0.tgz";
          };
          ident = "should-type-adaptors";
          ltype = "file";
          version = "1.1.0";
        };
      };
      should-util = {
        "1.0.1" = {
          fetchInfo = {
            narHash = "sha256-qUr/i4rO5Le7+XYLaOi3deJIoPPeyHeFDqrUJFxDXV4=";
            type = "tarball";
            url = "https://registry.npmjs.org/should-util/-/should-util-1.0.1.tgz";
          };
          ident = "should-util";
          ltype = "file";
          treeInfo = { };
          version = "1.0.1";
        };
      };
      side-channel = {
        "1.0.4" = {
          depInfo = {
            call-bind = {
              descriptor = "^1.0.0";
              pin = "1.0.2";
              runtime = true;
            };
            get-intrinsic = {
              descriptor = "^1.0.2";
              pin = "1.2.1";
              runtime = true;
            };
            object-inspect = {
              descriptor = "^1.9.0";
              pin = "1.12.3";
              runtime = true;
            };
          };
          fetchInfo = {
            narHash = "sha256-wbIXp1Q7Ui1ZcUXO3B1Oa24PZlezJx6cYM/33GtpVu8=";
            type = "tarball";
            url = "https://registry.npmjs.org/side-channel/-/side-channel-1.0.4.tgz";
          };
          ident = "side-channel";
          ltype = "file";
          version = "1.0.4";
        };
      };
      signal-exit = {
        "3.0.7" = {
          fetchInfo = {
            narHash = "sha256-2mSrADWJKHoX/YwLWk/Mdb4mjpL/6QYU8Evqtm24fdE=";
            type = "tarball";
            url = "https://registry.npmjs.org/signal-exit/-/signal-exit-3.0.7.tgz";
          };
          ident = "signal-exit";
          ltype = "file";
          treeInfo = { };
          version = "3.0.7";
        };
      };
      simple-eval = {
        "1.0.0" = {
          depInfo = {
            jsep = {
              descriptor = "^1.1.2";
              pin = "1.3.8";
              runtime = true;
            };
          };
          fetchInfo = {
            narHash = "sha256-uZFOq4Ig6ZAVaLbKxjji/Anz0xSta7V6funbrHPvP4w=";
            type = "tarball";
            url = "https://registry.npmjs.org/simple-eval/-/simple-eval-1.0.0.tgz";
          };
          ident = "simple-eval";
          ltype = "file";
          version = "1.0.0";
        };
      };
      slash = {
        "3.0.0" = {
          fetchInfo = {
            narHash = "sha256-tZzgTJwTD+eFikcawSO8plEa7YR2/RULHUs98d+5EC4=";
            type = "tarball";
            url = "https://registry.npmjs.org/slash/-/slash-3.0.0.tgz";
          };
          ident = "slash";
          ltype = "file";
          treeInfo = { };
          version = "3.0.0";
        };
      };
      source-map = {
        "0.5.7" = {
          fetchInfo = {
            narHash = "sha256-TfLkcoel84umresRhkiSAJkWIZ9bCfn9ZA9cZk8qGRU=";
            type = "tarball";
            url = "https://registry.npmjs.org/source-map/-/source-map-0.5.7.tgz";
          };
          ident = "source-map";
          ltype = "file";
          treeInfo = { };
          version = "0.5.7";
        };
        "0.6.1" = {
          fetchInfo = {
            narHash = "sha256-kOXyuKVrD3Fzez65GwPnNC615Ju17D00wsIgKcCWTJk=";
            type = "tarball";
            url = "https://registry.npmjs.org/source-map/-/source-map-0.6.1.tgz";
          };
          ident = "source-map";
          ltype = "file";
          treeInfo = { };
          version = "0.6.1";
        };
      };
      source-map-js = {
        "1.0.2" = {
          fetchInfo = {
            narHash = "sha256-gT4AthiqS/fwwos9E1ub0GC3sX14QIkJxiByo5/2IGc=";
            type = "tarball";
            url = "https://registry.npmjs.org/source-map-js/-/source-map-js-1.0.2.tgz";
          };
          ident = "source-map-js";
          ltype = "file";
          treeInfo = { };
          version = "1.0.2";
        };
      };
      sourcemap-codec = {
        "1.4.8" = {
          fetchInfo = {
            narHash = "sha256-h4MU0roZ/UTdTO0HNwwS836V10/FmiMv/A7nejyO4vc=";
            type = "tarball";
            url = "https://registry.npmjs.org/sourcemap-codec/-/sourcemap-codec-1.4.8.tgz";
          };
          ident = "sourcemap-codec";
          ltype = "file";
          treeInfo = { };
          version = "1.4.8";
        };
      };
      sprintf-js = {
        "1.0.3" = {
          fetchInfo = {
            narHash = "sha256-uUKz9y/hyOs58YEaXDOeVK7nhGxpTdNWE7IFSsdAtAc=";
            type = "tarball";
            url = "https://registry.npmjs.org/sprintf-js/-/sprintf-js-1.0.3.tgz";
          };
          ident = "sprintf-js";
          ltype = "file";
          treeInfo = { };
          version = "1.0.3";
        };
      };
      stacktracey = {
        "2.1.8" = {
          depInfo = {
            as-table = {
              descriptor = "^1.0.36";
              pin = "1.0.55";
              runtime = true;
            };
            get-source = {
              descriptor = "^2.0.12";
              pin = "2.0.12";
              runtime = true;
            };
          };
          fetchInfo = {
            narHash = "sha256-IiNcVIK2d/zWTZzHgby5+Nwnx/Zhd2wb/kqTAlKResY=";
            type = "tarball";
            url = "https://registry.npmjs.org/stacktracey/-/stacktracey-2.1.8.tgz";
          };
          ident = "stacktracey";
          ltype = "file";
          version = "2.1.8";
        };
      };
      streamsearch = {
        "1.1.0" = {
          fetchInfo = {
            narHash = "sha256-79vktBOYiUIv4NTm8wdH6icmGjNB4Znf9d6zJLXFuHs=";
            type = "tarball";
            url = "https://registry.npmjs.org/streamsearch/-/streamsearch-1.1.0.tgz";
          };
          ident = "streamsearch";
          ltype = "file";
          treeInfo = { };
          version = "1.1.0";
        };
      };
      string-argv = {
        "0.3.2" = {
          fetchInfo = {
            narHash = "sha256-kGx+HRV7CeDaZFsl6frgsC3mV0XS0GuMNfnXIEoabRg=";
            type = "tarball";
            url = "https://registry.npmjs.org/string-argv/-/string-argv-0.3.2.tgz";
          };
          ident = "string-argv";
          ltype = "file";
          treeInfo = { };
          version = "0.3.2";
        };
      };
      string-width = {
        "4.2.3" = {
          depInfo = {
            emoji-regex = {
              descriptor = "^8.0.0";
              pin = "8.0.0";
              runtime = true;
            };
            is-fullwidth-code-point = {
              descriptor = "^3.0.0";
              pin = "3.0.0";
              runtime = true;
            };
            strip-ansi = {
              descriptor = "^6.0.1";
              pin = "6.0.1";
              runtime = true;
            };
          };
          fetchInfo = {
            narHash = "sha256-UkdpzgZbqh+d2lMxcCqdnxter5D6KYGgaYMta2Dhqn4=";
            type = "tarball";
            url = "https://registry.npmjs.org/string-width/-/string-width-4.2.3.tgz";
          };
          ident = "string-width";
          ltype = "file";
          version = "4.2.3";
        };
      };
      "string.prototype.matchall" = {
        "4.0.8" = {
          depInfo = {
            call-bind = {
              descriptor = "^1.0.2";
              pin = "1.0.2";
              runtime = true;
            };
            define-properties = {
              descriptor = "^1.1.4";
              pin = "1.2.0";
              runtime = true;
            };
            es-abstract = {
              descriptor = "^1.20.4";
              pin = "1.22.1";
              runtime = true;
            };
            get-intrinsic = {
              descriptor = "^1.1.3";
              pin = "1.2.1";
              runtime = true;
            };
            has-symbols = {
              descriptor = "^1.0.3";
              pin = "1.0.3";
              runtime = true;
            };
            internal-slot = {
              descriptor = "^1.0.3";
              pin = "1.0.5";
              runtime = true;
            };
            "regexp.prototype.flags" = {
              descriptor = "^1.4.3";
              pin = "1.5.0";
              runtime = true;
            };
            side-channel = {
              descriptor = "^1.0.4";
              pin = "1.0.4";
              runtime = true;
            };
          };
          fetchInfo = {
            narHash = "sha256-VweNCSKCGx++CMO9cztKGoIiQs6MCxYYcvrW9qdJEy4=";
            type = "tarball";
            url = "https://registry.npmjs.org/string.prototype.matchall/-/string.prototype.matchall-4.0.8.tgz";
          };
          ident = "string.prototype.matchall";
          ltype = "file";
          version = "4.0.8";
        };
      };
      "string.prototype.trim" = {
        "1.2.7" = {
          depInfo = {
            call-bind = {
              descriptor = "^1.0.2";
              pin = "1.0.2";
              runtime = true;
            };
            define-properties = {
              descriptor = "^1.1.4";
              pin = "1.2.0";
              runtime = true;
            };
            es-abstract = {
              descriptor = "^1.20.4";
              pin = "1.22.1";
              runtime = true;
            };
          };
          fetchInfo = {
            narHash = "sha256-2UOC/v/o5JV8ALy5qXfTV2K8f2OPTNBoeJwLrmnqSzE=";
            type = "tarball";
            url = "https://registry.npmjs.org/string.prototype.trim/-/string.prototype.trim-1.2.7.tgz";
          };
          ident = "string.prototype.trim";
          ltype = "file";
          version = "1.2.7";
        };
      };
      "string.prototype.trimend" = {
        "1.0.6" = {
          depInfo = {
            call-bind = {
              descriptor = "^1.0.2";
              pin = "1.0.2";
              runtime = true;
            };
            define-properties = {
              descriptor = "^1.1.4";
              pin = "1.2.0";
              runtime = true;
            };
            es-abstract = {
              descriptor = "^1.20.4";
              pin = "1.22.1";
              runtime = true;
            };
          };
          fetchInfo = {
            narHash = "sha256-xMpi87OuAENhgYXeU+pSVc0G5MrASZG5Xlrsza5RMtA=";
            type = "tarball";
            url = "https://registry.npmjs.org/string.prototype.trimend/-/string.prototype.trimend-1.0.6.tgz";
          };
          ident = "string.prototype.trimend";
          ltype = "file";
          version = "1.0.6";
        };
      };
      "string.prototype.trimstart" = {
        "1.0.6" = {
          depInfo = {
            call-bind = {
              descriptor = "^1.0.2";
              pin = "1.0.2";
              runtime = true;
            };
            define-properties = {
              descriptor = "^1.1.4";
              pin = "1.2.0";
              runtime = true;
            };
            es-abstract = {
              descriptor = "^1.20.4";
              pin = "1.22.1";
              runtime = true;
            };
          };
          fetchInfo = {
            narHash = "sha256-1/L66FiWZGsYmo+hue4PXAVc1rfBERlrrpKuPbkP3K0=";
            type = "tarball";
            url = "https://registry.npmjs.org/string.prototype.trimstart/-/string.prototype.trimstart-1.0.6.tgz";
          };
          ident = "string.prototype.trimstart";
          ltype = "file";
          version = "1.0.6";
        };
      };
      strip-ansi = {
        "6.0.1" = {
          depInfo = {
            ansi-regex = {
              descriptor = "^5.0.1";
              pin = "5.0.1";
              runtime = true;
            };
          };
          fetchInfo = {
            narHash = "sha256-mMRzEL6fWJXYmQ2ZhRAhnYMcjdNCfvGF3Y7NekoLgXc=";
            type = "tarball";
            url = "https://registry.npmjs.org/strip-ansi/-/strip-ansi-6.0.1.tgz";
          };
          ident = "strip-ansi";
          ltype = "file";
          version = "6.0.1";
        };
      };
      strip-bom = {
        "3.0.0" = {
          fetchInfo = {
            narHash = "sha256-J87gjr955s09mqu6GTyZDmNOXqX1FJDX4CLFTMuM+zU=";
            type = "tarball";
            url = "https://registry.npmjs.org/strip-bom/-/strip-bom-3.0.0.tgz";
          };
          ident = "strip-bom";
          ltype = "file";
          treeInfo = { };
          version = "3.0.0";
        };
      };
      strip-final-newline = {
        "2.0.0" = {
          fetchInfo = {
            narHash = "sha256-t0BevRoiiF/ujVHWQykmRSeUyIkGkVcXidbu5eFromE=";
            type = "tarball";
            url = "https://registry.npmjs.org/strip-final-newline/-/strip-final-newline-2.0.0.tgz";
          };
          ident = "strip-final-newline";
          ltype = "file";
          treeInfo = { };
          version = "2.0.0";
        };
      };
      strip-json-comments = {
        "3.1.1" = {
          fetchInfo = {
            narHash = "sha256-kG9XiGtBCKfDljwOWaSI7pZbk5I7uywJFm4jNdBERYw=";
            type = "tarball";
            url = "https://registry.npmjs.org/strip-json-comments/-/strip-json-comments-3.1.1.tgz";
          };
          ident = "strip-json-comments";
          ltype = "file";
          treeInfo = { };
          version = "3.1.1";
        };
      };
      styled-jsx = {
        "5.1.1" = {
          depInfo = {
            client-only = {
              descriptor = "0.0.1";
              pin = "0.0.1";
              runtime = true;
            };
          };
          fetchInfo = {
            narHash = "sha256-I5qv/D8y+LC3HmTDCvCEqB3TnWnuk1e+Z0u/0D31Ix4=";
            type = "tarball";
            url = "https://registry.npmjs.org/styled-jsx/-/styled-jsx-5.1.1.tgz";
          };
          ident = "styled-jsx";
          ltype = "file";
          peerInfo = {
            "@babel/core" = {
              descriptor = "*";
              optional = true;
            };
            babel-plugin-macros = {
              descriptor = "*";
              optional = true;
            };
            react = {
              descriptor = ">= 16.8.0 || 17.x.x || ^18.0.0-0";
            };
          };
          version = "5.1.1";
        };
      };
      stylis = {
        "4.2.0" = {
          fetchInfo = {
            narHash = "sha256-uBRk2Ja5qhHSROWOjmJ6+K/k2NNHGK37SD7nuKxR6F4=";
            type = "tarball";
            url = "https://registry.npmjs.org/stylis/-/stylis-4.2.0.tgz";
          };
          ident = "stylis";
          ltype = "file";
          treeInfo = { };
          version = "4.2.0";
        };
      };
      sucrase = {
        "3.34.0" = {
          binInfo = {
            binPairs = {
              sucrase = "bin/sucrase";
              sucrase-node = "bin/sucrase-node";
            };
          };
          depInfo = {
            "@jridgewell/gen-mapping" = {
              descriptor = "^0.3.2";
              pin = "0.3.3";
              runtime = true;
            };
            commander = {
              descriptor = "^4.0.0";
              pin = "4.1.1";
              runtime = true;
            };
            glob = {
              descriptor = "7.1.6";
              pin = "7.1.6";
              runtime = true;
            };
            lines-and-columns = {
              descriptor = "^1.1.6";
              pin = "1.2.4";
              runtime = true;
            };
            mz = {
              descriptor = "^2.7.0";
              pin = "2.7.0";
              runtime = true;
            };
            pirates = {
              descriptor = "^4.0.1";
              pin = "4.0.6";
              runtime = true;
            };
            ts-interface-checker = {
              descriptor = "^0.1.9";
              pin = "0.1.13";
              runtime = true;
            };
          };
          fetchInfo = {
            narHash = "sha256-fwMqtq76DhJ00EsGVs2na8feKHKrrkOpc6GsTNpOPqU=";
            type = "tarball";
            url = "https://registry.npmjs.org/sucrase/-/sucrase-3.34.0.tgz";
          };
          ident = "sucrase";
          ltype = "file";
          version = "3.34.0";
        };
      };
      supports-color = {
        "5.5.0" = {
          depInfo = {
            has-flag = {
              descriptor = "^3.0.0";
              pin = "3.0.0";
              runtime = true;
            };
          };
          fetchInfo = {
            narHash = "sha256-CFEl8ukJUaXQ4RzTSFYfqd09tqgYfgJuU/Kem/DkKe4=";
            type = "tarball";
            url = "https://registry.npmjs.org/supports-color/-/supports-color-5.5.0.tgz";
          };
          ident = "supports-color";
          ltype = "file";
          version = "5.5.0";
        };
        "7.2.0" = {
          depInfo = {
            has-flag = {
              descriptor = "^4.0.0";
              pin = "4.0.0";
              runtime = true;
            };
          };
          fetchInfo = {
            narHash = "sha256-ALfHRAgnkUrOOyywhxLVllKKtKkFQZ3IvetXiR72flk=";
            type = "tarball";
            url = "https://registry.npmjs.org/supports-color/-/supports-color-7.2.0.tgz";
          };
          ident = "supports-color";
          ltype = "file";
          version = "7.2.0";
        };
      };
      supports-preserve-symlinks-flag = {
        "1.0.0" = {
          fetchInfo = {
            narHash = "sha256-Gwf/IHn+m17+KsKxcOrhCxAjvH8uxQx8Bud+qeCNwKg=";
            type = "tarball";
            url = "https://registry.npmjs.org/supports-preserve-symlinks-flag/-/supports-preserve-symlinks-flag-1.0.0.tgz";
          };
          ident = "supports-preserve-symlinks-flag";
          ltype = "file";
          treeInfo = { };
          version = "1.0.0";
        };
      };
      swagger2openapi = {
        "7.0.8" = {
          binInfo = {
            binPairs = {
              boast = "boast.js";
              oas-validate = "oas-validate.js";
              swagger2openapi = "swagger2openapi.js";
            };
          };
          depInfo = {
            call-me-maybe = {
              descriptor = "^1.0.1";
              pin = "1.0.2";
              runtime = true;
            };
            node-fetch = {
              descriptor = "^2.6.1";
              pin = "2.7.0";
              runtime = true;
            };
            node-fetch-h2 = {
              descriptor = "^2.3.0";
              pin = "2.3.0";
              runtime = true;
            };
            node-readfiles = {
              descriptor = "^0.2.0";
              pin = "0.2.0";
              runtime = true;
            };
            oas-kit-common = {
              descriptor = "^1.0.8";
              pin = "1.0.8";
              runtime = true;
            };
            oas-resolver = {
              descriptor = "^2.5.6";
              pin = "2.5.6";
              runtime = true;
            };
            oas-schema-walker = {
              descriptor = "^1.1.5";
              pin = "1.1.5";
              runtime = true;
            };
            oas-validator = {
              descriptor = "^5.0.8";
              pin = "5.0.8";
              runtime = true;
            };
            reftools = {
              descriptor = "^1.1.9";
              pin = "1.1.9";
              runtime = true;
            };
            yaml = {
              descriptor = "^1.10.0";
              pin = "1.10.2";
              runtime = true;
            };
            yargs = {
              descriptor = "^17.0.1";
              pin = "17.3.1";
              runtime = true;
            };
          };
          fetchInfo = {
            narHash = "sha256-2mdz7SwMlbeOzmXz97d3QtRAzl71lqTyLVmrYasjVFg=";
            type = "tarball";
            url = "https://registry.npmjs.org/swagger2openapi/-/swagger2openapi-7.0.8.tgz";
          };
          ident = "swagger2openapi";
          ltype = "file";
          version = "7.0.8";
        };
      };
      swr = {
        "2.2.1" = {
          depInfo = {
            client-only = {
              descriptor = "^0.0.1";
              pin = "0.0.1";
              runtime = true;
            };
            use-sync-external-store = {
              descriptor = "^1.2.0";
              pin = "1.2.0";
              runtime = true;
            };
          };
          fetchInfo = {
            narHash = "sha256-oGItSbZ/fULa49fo4W5TfwUzP1bJymCki81raWfpD7Y=";
            type = "tarball";
            url = "https://registry.npmjs.org/swr/-/swr-2.2.1.tgz";
          };
          ident = "swr";
          ltype = "file";
          peerInfo = {
            react = {
              descriptor = "^16.11.0 || ^17.0.0 || ^18.0.0";
            };
          };
          version = "2.2.1";
        };
      };
      tailwindcss = {
        "3.3.3" = {
          binInfo = {
            binPairs = {
              tailwind = "lib/cli.js";
              tailwindcss = "lib/cli.js";
            };
          };
          depInfo = {
            "@alloc/quick-lru" = {
              descriptor = "^5.2.0";
              pin = "5.2.0";
              runtime = true;
            };
            arg = {
              descriptor = "^5.0.2";
              pin = "5.0.2";
              runtime = true;
            };
            chokidar = {
              descriptor = "^3.5.3";
              pin = "3.5.3";
              runtime = true;
            };
            didyoumean = {
              descriptor = "^1.2.2";
              pin = "1.2.2";
              runtime = true;
            };
            dlv = {
              descriptor = "^1.1.3";
              pin = "1.1.3";
              runtime = true;
            };
            fast-glob = {
              descriptor = "^3.2.12";
              pin = "3.3.1";
              runtime = true;
            };
            glob-parent = {
              descriptor = "^6.0.2";
              pin = "6.0.2";
              runtime = true;
            };
            is-glob = {
              descriptor = "^4.0.3";
              pin = "4.0.3";
              runtime = true;
            };
            jiti = {
              descriptor = "^1.18.2";
              pin = "1.19.1";
              runtime = true;
            };
            lilconfig = {
              descriptor = "^2.1.0";
              pin = "2.1.0";
              runtime = true;
            };
            micromatch = {
              descriptor = "^4.0.5";
              pin = "4.0.5";
              runtime = true;
            };
            normalize-path = {
              descriptor = "^3.0.0";
              pin = "3.0.0";
              runtime = true;
            };
            object-hash = {
              descriptor = "^3.0.0";
              pin = "3.0.0";
              runtime = true;
            };
            picocolors = {
              descriptor = "^1.0.0";
              pin = "1.0.0";
              runtime = true;
            };
            postcss = {
              descriptor = "^8.4.23";
              pin = "8.4.27";
              runtime = true;
            };
            postcss-import = {
              descriptor = "^15.1.0";
              pin = "15.1.0";
              runtime = true;
            };
            postcss-js = {
              descriptor = "^4.0.1";
              pin = "4.0.1";
              runtime = true;
            };
            postcss-load-config = {
              descriptor = "^4.0.1";
              pin = "4.0.1";
              runtime = true;
            };
            postcss-nested = {
              descriptor = "^6.0.1";
              pin = "6.0.1";
              runtime = true;
            };
            postcss-selector-parser = {
              descriptor = "^6.0.11";
              pin = "6.0.13";
              runtime = true;
            };
            resolve = {
              descriptor = "^1.22.2";
              pin = "1.22.4";
              runtime = true;
            };
            sucrase = {
              descriptor = "^3.32.0";
              pin = "3.34.0";
              runtime = true;
            };
          };
          fetchInfo = {
            narHash = "sha256-mXn6Tjujds7HVZnfdAJS344jxBHIddyNOZE125xSndg=";
            type = "tarball";
            url = "https://registry.npmjs.org/tailwindcss/-/tailwindcss-3.3.3.tgz";
          };
          ident = "tailwindcss";
          ltype = "file";
          version = "3.3.3";
        };
      };
      tapable = {
        "2.2.1" = {
          fetchInfo = {
            narHash = "sha256-chSmdQSJK5rfmP009tDM0j225LM2HDH9qoi0dJoWFac=";
            type = "tarball";
            url = "https://registry.npmjs.org/tapable/-/tapable-2.2.1.tgz";
          };
          ident = "tapable";
          ltype = "file";
          treeInfo = { };
          version = "2.2.1";
        };
      };
      text-table = {
        "0.2.0" = {
          fetchInfo = {
            narHash = "sha256-5aLlgyS88H30N4WzcI5Qz3o1o65EGaNt8BaYxKkTzF4=";
            type = "tarball";
            url = "https://registry.npmjs.org/text-table/-/text-table-0.2.0.tgz";
          };
          ident = "text-table";
          ltype = "file";
          treeInfo = { };
          version = "0.2.0";
        };
      };
      thenify = {
        "3.3.1" = {
          depInfo = {
            any-promise = {
              descriptor = "^1.0.0";
              pin = "1.3.0";
              runtime = true;
            };
          };
          fetchInfo = {
            narHash = "sha256-d2NfLIezl4DKTUh/9oxpLlyHJomcXfReg0HBB+I3kVU=";
            type = "tarball";
            url = "https://registry.npmjs.org/thenify/-/thenify-3.3.1.tgz";
          };
          ident = "thenify";
          ltype = "file";
          version = "3.3.1";
        };
      };
      thenify-all = {
        "1.6.0" = {
          depInfo = {
            thenify = {
              descriptor = ">= 3.1.0 < 4";
              pin = "3.3.1";
              runtime = true;
            };
          };
          fetchInfo = {
            narHash = "sha256-OVYy6Nm65TUSu0KN4CL7dX3S9pEytln0fY1IPlQJtpk=";
            type = "tarball";
            url = "https://registry.npmjs.org/thenify-all/-/thenify-all-1.6.0.tgz";
          };
          ident = "thenify-all";
          ltype = "file";
          version = "1.6.0";
        };
      };
      to-fast-properties = {
        "2.0.0" = {
          fetchInfo = {
            narHash = "sha256-REHa011PYD77WKQpm3pDqs8+640POdK6iqwfEhljtzk=";
            type = "tarball";
            url = "https://registry.npmjs.org/to-fast-properties/-/to-fast-properties-2.0.0.tgz";
          };
          ident = "to-fast-properties";
          ltype = "file";
          treeInfo = { };
          version = "2.0.0";
        };
      };
      to-regex-range = {
        "5.0.1" = {
          depInfo = {
            is-number = {
              descriptor = "^7.0.0";
              pin = "7.0.0";
              runtime = true;
            };
          };
          fetchInfo = {
            narHash = "sha256-+vtC2A5vM5ixOFrv1pRteDxoFLswFln/YcK09AmMbQM=";
            type = "tarball";
            url = "https://registry.npmjs.org/to-regex-range/-/to-regex-range-5.0.1.tgz";
          };
          ident = "to-regex-range";
          ltype = "file";
          version = "5.0.1";
        };
      };
      tr46 = {
        "0.0.3" = {
          fetchInfo = {
            narHash = "sha256-qY+tBl/8yq2nhwcQ84qyeuzY37EXL2RYQ8W3nIqNIZA=";
            type = "tarball";
            url = "https://registry.npmjs.org/tr46/-/tr46-0.0.3.tgz";
          };
          ident = "tr46";
          ltype = "file";
          treeInfo = { };
          version = "0.0.3";
        };
      };
      ts-interface-checker = {
        "0.1.13" = {
          fetchInfo = {
            narHash = "sha256-li0gewA/g/ORdXhocUhEdOXTjv3m8hl/2PGaeEEcIv0=";
            type = "tarball";
            url = "https://registry.npmjs.org/ts-interface-checker/-/ts-interface-checker-0.1.13.tgz";
          };
          ident = "ts-interface-checker";
          ltype = "file";
          treeInfo = { };
          version = "0.1.13";
        };
      };
      tsconfck = {
        "2.1.2" = {
          binInfo = {
            binPairs = {
              tsconfck = "bin/tsconfck.js";
            };
          };
          fetchInfo = {
            narHash = "sha256-RFg4vb6iLkHnm6+QDyPa511Dxengu/lqAwr4ChAJ/0o=";
            type = "tarball";
            url = "https://registry.npmjs.org/tsconfck/-/tsconfck-2.1.2.tgz";
          };
          ident = "tsconfck";
          ltype = "file";
          peerInfo = {
            typescript = {
              descriptor = "^4.3.5 || ^5.0.0";
              optional = true;
            };
          };
          treeInfo = { };
          version = "2.1.2";
        };
      };
      tsconfig-paths = {
        "3.14.2" = {
          depInfo = {
            "@types/json5" = {
              descriptor = "^0.0.29";
              pin = "0.0.29";
              runtime = true;
            };
            json5 = {
              descriptor = "^1.0.2";
              pin = "1.0.2";
              runtime = true;
            };
            minimist = {
              descriptor = "^1.2.6";
              pin = "1.2.8";
              runtime = true;
            };
            strip-bom = {
              descriptor = "^3.0.0";
              pin = "3.0.0";
              runtime = true;
            };
          };
          fetchInfo = {
            narHash = "sha256-Mye/YqIaz7tmXjZK4nJ5SBbjMZHak3AvaPKDwZDGH08=";
            type = "tarball";
            url = "https://registry.npmjs.org/tsconfig-paths/-/tsconfig-paths-3.14.2.tgz";
          };
          ident = "tsconfig-paths";
          ltype = "file";
          version = "3.14.2";
        };
      };
      tslib = {
        "1.14.1" = {
          fetchInfo = {
            narHash = "sha256-7y4Tt/r8MTDqLmGZXj/Drd0crGnXs+XXwT5QcgjdzPI=";
            type = "tarball";
            url = "https://registry.npmjs.org/tslib/-/tslib-1.14.1.tgz";
          };
          ident = "tslib";
          ltype = "file";
          treeInfo = { };
          version = "1.14.1";
        };
        "2.6.1" = {
          fetchInfo = {
            narHash = "sha256-FxpbGKS4kKKq9nXVHbv/BIW+G53Bv4eo5PR5wauVygg=";
            type = "tarball";
            url = "https://registry.npmjs.org/tslib/-/tslib-2.6.1.tgz";
          };
          ident = "tslib";
          ltype = "file";
          treeInfo = { };
          version = "2.6.1";
        };
      };
      tsutils = {
        "3.21.0" = {
          depInfo = {
            tslib = {
              descriptor = "^1.8.1";
              pin = "1.14.1";
              runtime = true;
            };
          };
          fetchInfo = {
            narHash = "sha256-OUV40+OFV28hA6hIVpzd7GRsroYSTvjoVLhJyxpcMLg=";
            type = "tarball";
            url = "https://registry.npmjs.org/tsutils/-/tsutils-3.21.0.tgz";
          };
          ident = "tsutils";
          ltype = "file";
          peerInfo = {
            typescript = {
              descriptor = ">=2.8.0 || >= 3.2.0-dev || >= 3.3.0-dev || >= 3.4.0-dev || >= 3.5.0-dev || >= 3.6.0-dev || >= 3.6.0-beta || >= 3.7.0-dev || >= 3.7.0-beta";
            };
          };
          version = "3.21.0";
        };
      };
      type-check = {
        "0.4.0" = {
          depInfo = {
            prelude-ls = {
              descriptor = "^1.2.1";
              pin = "1.2.1";
              runtime = true;
            };
          };
          fetchInfo = {
            narHash = "sha256-c7oK/LdUUDXwdCUbkbLmNDixyLJR9avZVfBbfOupE8g=";
            type = "tarball";
            url = "https://registry.npmjs.org/type-check/-/type-check-0.4.0.tgz";
          };
          ident = "type-check";
          ltype = "file";
          version = "0.4.0";
        };
      };
      type-fest = {
        "0.20.2" = {
          fetchInfo = {
            narHash = "sha256-79+ZefWFhtLpRLnn3BbQbMF+qxgvZC5A+RMdf992Hpw=";
            type = "tarball";
            url = "https://registry.npmjs.org/type-fest/-/type-fest-0.20.2.tgz";
          };
          ident = "type-fest";
          ltype = "file";
          treeInfo = { };
          version = "0.20.2";
        };
      };
      typed-array-buffer = {
        "1.0.0" = {
          depInfo = {
            call-bind = {
              descriptor = "^1.0.2";
              pin = "1.0.2";
              runtime = true;
            };
            get-intrinsic = {
              descriptor = "^1.2.1";
              pin = "1.2.1";
              runtime = true;
            };
            is-typed-array = {
              descriptor = "^1.1.10";
              pin = "1.1.12";
              runtime = true;
            };
          };
          fetchInfo = {
            narHash = "sha256-DMT/eFKOFASX3vNdE0CCYbgxZW9sAXUG99DrYCFDgRs=";
            type = "tarball";
            url = "https://registry.npmjs.org/typed-array-buffer/-/typed-array-buffer-1.0.0.tgz";
          };
          ident = "typed-array-buffer";
          ltype = "file";
          version = "1.0.0";
        };
      };
      typed-array-byte-length = {
        "1.0.0" = {
          depInfo = {
            call-bind = {
              descriptor = "^1.0.2";
              pin = "1.0.2";
              runtime = true;
            };
            for-each = {
              descriptor = "^0.3.3";
              pin = "0.3.3";
              runtime = true;
            };
            has-proto = {
              descriptor = "^1.0.1";
              pin = "1.0.1";
              runtime = true;
            };
            is-typed-array = {
              descriptor = "^1.1.10";
              pin = "1.1.12";
              runtime = true;
            };
          };
          fetchInfo = {
            narHash = "sha256-2u5lw/X7CvIx4xAbfoQR44zv7zGvzHGVwjyOL53phrk=";
            type = "tarball";
            url = "https://registry.npmjs.org/typed-array-byte-length/-/typed-array-byte-length-1.0.0.tgz";
          };
          ident = "typed-array-byte-length";
          ltype = "file";
          version = "1.0.0";
        };
      };
      typed-array-byte-offset = {
        "1.0.0" = {
          depInfo = {
            available-typed-arrays = {
              descriptor = "^1.0.5";
              pin = "1.0.5";
              runtime = true;
            };
            call-bind = {
              descriptor = "^1.0.2";
              pin = "1.0.2";
              runtime = true;
            };
            for-each = {
              descriptor = "^0.3.3";
              pin = "0.3.3";
              runtime = true;
            };
            has-proto = {
              descriptor = "^1.0.1";
              pin = "1.0.1";
              runtime = true;
            };
            is-typed-array = {
              descriptor = "^1.1.10";
              pin = "1.1.12";
              runtime = true;
            };
          };
          fetchInfo = {
            narHash = "sha256-bmP70ZRmIe43OHm3dxN9khqyiQOATrvLK8ANZOc5h2U=";
            type = "tarball";
            url = "https://registry.npmjs.org/typed-array-byte-offset/-/typed-array-byte-offset-1.0.0.tgz";
          };
          ident = "typed-array-byte-offset";
          ltype = "file";
          version = "1.0.0";
        };
      };
      typed-array-length = {
        "1.0.4" = {
          depInfo = {
            call-bind = {
              descriptor = "^1.0.2";
              pin = "1.0.2";
              runtime = true;
            };
            for-each = {
              descriptor = "^0.3.3";
              pin = "0.3.3";
              runtime = true;
            };
            is-typed-array = {
              descriptor = "^1.1.9";
              pin = "1.1.12";
              runtime = true;
            };
          };
          fetchInfo = {
            narHash = "sha256-dDukA6EG+m1cYtGjkSPo0oJA3Vb5ov5wBKIoQ0hCd5I=";
            type = "tarball";
            url = "https://registry.npmjs.org/typed-array-length/-/typed-array-length-1.0.4.tgz";
          };
          ident = "typed-array-length";
          ltype = "file";
          version = "1.0.4";
        };
      };
      typescript = {
        "5.1.6" = {
          binInfo = {
            binPairs = {
              tsc = "bin/tsc";
              tsserver = "bin/tsserver";
            };
          };
          fetchInfo = {
            narHash = "sha256-Ks1ouwQtjZjQt912v7UqEm+RmuNXmNtIl6LqU+xHXJU=";
            type = "tarball";
            url = "https://registry.npmjs.org/typescript/-/typescript-5.1.6.tgz";
          };
          ident = "typescript";
          ltype = "file";
          treeInfo = { };
          version = "5.1.6";
        };
      };
      unbox-primitive = {
        "1.0.2" = {
          depInfo = {
            call-bind = {
              descriptor = "^1.0.2";
              pin = "1.0.2";
              runtime = true;
            };
            has-bigints = {
              descriptor = "^1.0.2";
              pin = "1.0.2";
              runtime = true;
            };
            has-symbols = {
              descriptor = "^1.0.3";
              pin = "1.0.3";
              runtime = true;
            };
            which-boxed-primitive = {
              descriptor = "^1.0.2";
              pin = "1.0.2";
              runtime = true;
            };
          };
          fetchInfo = {
            narHash = "sha256-p4Tro2Ta5HLZQn/OcrTelo8hf9gSAtUJIoUDlhhVY84=";
            type = "tarball";
            url = "https://registry.npmjs.org/unbox-primitive/-/unbox-primitive-1.0.2.tgz";
          };
          ident = "unbox-primitive";
          ltype = "file";
          version = "1.0.2";
        };
      };
      universalify = {
        "2.0.0" = {
          fetchInfo = {
            narHash = "sha256-0ld8f/t33JjseUuroCnT/yjNIIwlGXekvICWB8dr5b4=";
            type = "tarball";
            url = "https://registry.npmjs.org/universalify/-/universalify-2.0.0.tgz";
          };
          ident = "universalify";
          ltype = "file";
          treeInfo = { };
          version = "2.0.0";
        };
      };
      update-browserslist-db = {
        "1.0.11" = {
          binInfo = {
            binPairs = {
              update-browserslist-db = "cli.js";
            };
          };
          depInfo = {
            escalade = {
              descriptor = "^3.1.1";
              pin = "3.1.1";
              runtime = true;
            };
            picocolors = {
              descriptor = "^1.0.0";
              pin = "1.0.0";
              runtime = true;
            };
          };
          fetchInfo = {
            narHash = "sha256-jrUkCFn7UN5umslE/LVhGI61x/RpzBa+UVxAg9EeVhs=";
            type = "tarball";
            url = "https://registry.npmjs.org/update-browserslist-db/-/update-browserslist-db-1.0.11.tgz";
          };
          ident = "update-browserslist-db";
          ltype = "file";
          peerInfo = {
            browserslist = {
              descriptor = ">= 4.21.0";
            };
          };
          version = "1.0.11";
        };
      };
      uri-js = {
        "4.4.1" = {
          depInfo = {
            punycode = {
              descriptor = "^2.1.0";
              pin = "2.3.0";
              runtime = true;
            };
          };
          fetchInfo = {
            narHash = "sha256-iMLypOgKbMR/XBQ4pWT/gOyOA0W8YKt1rQ8BUBCNzoY=";
            type = "tarball";
            url = "https://registry.npmjs.org/uri-js/-/uri-js-4.4.1.tgz";
          };
          ident = "uri-js";
          ltype = "file";
          version = "4.4.1";
        };
      };
      urijs = {
        "1.19.11" = {
          fetchInfo = {
            narHash = "sha256-BcNLOxSJBXOwzUEMXYtoIpnGIu2fN3E71n2wLh8dFxg=";
            type = "tarball";
            url = "https://registry.npmjs.org/urijs/-/urijs-1.19.11.tgz";
          };
          ident = "urijs";
          ltype = "file";
          treeInfo = { };
          version = "1.19.11";
        };
      };
      use-sync-external-store = {
        "1.2.0" = {
          fetchInfo = {
            narHash = "sha256-K32BKXCvYuWk9DIt3rruSuZJFAQeGcrKGgJZ+QjTGrI=";
            type = "tarball";
            url = "https://registry.npmjs.org/use-sync-external-store/-/use-sync-external-store-1.2.0.tgz";
          };
          ident = "use-sync-external-store";
          ltype = "file";
          peerInfo = {
            react = {
              descriptor = "^16.8.0 || ^17.0.0 || ^18.0.0";
            };
          };
          treeInfo = { };
          version = "1.2.0";
        };
      };
      util-deprecate = {
        "1.0.2" = {
          fetchInfo = {
            narHash = "sha256-rIdgRwu72yh5o+nvWoU8FWww1LMLAIKmtv8wPKglaeY=";
            type = "tarball";
            url = "https://registry.npmjs.org/util-deprecate/-/util-deprecate-1.0.2.tgz";
          };
          ident = "util-deprecate";
          ltype = "file";
          treeInfo = { };
          version = "1.0.2";
        };
      };
      utility-types = {
        "3.10.0" = {
          fetchInfo = {
            narHash = "sha256-9qh08GKyoCZiX1krDEumLkvWJjHqghqH0KRxExP27PM=";
            type = "tarball";
            url = "https://registry.npmjs.org/utility-types/-/utility-types-3.10.0.tgz";
          };
          ident = "utility-types";
          ltype = "file";
          treeInfo = { };
          version = "3.10.0";
        };
      };
      validate-npm-package-name = {
        "3.0.0" = {
          depInfo = {
            builtins = {
              descriptor = "^1.0.3";
              pin = "1.0.3";
              runtime = true;
            };
          };
          fetchInfo = {
            narHash = "sha256-55fgzZHXlnXvSxslpzNNqnR6E0zlAHWjAY8hvW5Yv3c=";
            type = "tarball";
            url = "https://registry.npmjs.org/validate-npm-package-name/-/validate-npm-package-name-3.0.0.tgz";
          };
          ident = "validate-npm-package-name";
          ltype = "file";
          version = "3.0.0";
        };
      };
      validator = {
        "13.11.0" = {
          fetchInfo = {
            narHash = "sha256-02Ywn19Kj4DH8DQ8eHslXs/pwBe6vDtkip5k9rDkQEg=";
            type = "tarball";
            url = "https://registry.npmjs.org/validator/-/validator-13.11.0.tgz";
          };
          ident = "validator";
          ltype = "file";
          treeInfo = { };
          version = "13.11.0";
        };
      };
      victory-vendor = {
        "36.6.11" = {
          depInfo = {
            "@types/d3-array" = {
              descriptor = "^3.0.3";
              pin = "3.0.5";
              runtime = true;
            };
            "@types/d3-ease" = {
              descriptor = "^3.0.0";
              pin = "3.0.0";
              runtime = true;
            };
            "@types/d3-interpolate" = {
              descriptor = "^3.0.1";
              pin = "3.0.1";
              runtime = true;
            };
            "@types/d3-scale" = {
              descriptor = "^4.0.2";
              pin = "4.0.3";
              runtime = true;
            };
            "@types/d3-shape" = {
              descriptor = "^3.1.0";
              pin = "3.1.1";
              runtime = true;
            };
            "@types/d3-time" = {
              descriptor = "^3.0.0";
              pin = "3.0.0";
              runtime = true;
            };
            "@types/d3-timer" = {
              descriptor = "^3.0.0";
              pin = "3.0.0";
              runtime = true;
            };
            d3-array = {
              descriptor = "^3.1.6";
              pin = "3.2.4";
              runtime = true;
            };
            d3-ease = {
              descriptor = "^3.0.1";
              pin = "3.0.1";
              runtime = true;
            };
            d3-interpolate = {
              descriptor = "^3.0.1";
              pin = "3.0.1";
              runtime = true;
            };
            d3-scale = {
              descriptor = "^4.0.2";
              pin = "4.0.2";
              runtime = true;
            };
            d3-shape = {
              descriptor = "^3.1.0";
              pin = "3.2.0";
              runtime = true;
            };
            d3-time = {
              descriptor = "^3.0.0";
              pin = "3.1.0";
              runtime = true;
            };
            d3-timer = {
              descriptor = "^3.0.1";
              pin = "3.0.1";
              runtime = true;
            };
          };
          fetchInfo = {
            narHash = "sha256-n2h/WOevG6dVWXLReuRm5bJEFdDKSw2db5ea4HzVIlU=";
            type = "tarball";
            url = "https://registry.npmjs.org/victory-vendor/-/victory-vendor-36.6.11.tgz";
          };
          ident = "victory-vendor";
          ltype = "file";
          version = "36.6.11";
        };
      };
      watchpack = {
        "2.4.0" = {
          depInfo = {
            glob-to-regexp = {
              descriptor = "^0.4.1";
              pin = "0.4.1";
              runtime = true;
            };
            graceful-fs = {
              descriptor = "^4.1.2";
              pin = "4.2.11";
              runtime = true;
            };
          };
          fetchInfo = {
            narHash = "sha256-6gYkU/hjGQAirYRUBO2BEjcUdzm/FQT09ee4KGUplEI=";
            type = "tarball";
            url = "https://registry.npmjs.org/watchpack/-/watchpack-2.4.0.tgz";
          };
          ident = "watchpack";
          ltype = "file";
          version = "2.4.0";
        };
      };
      wcwidth = {
        "1.0.1" = {
          depInfo = {
            defaults = {
              descriptor = "^1.0.3";
              pin = "1.0.4";
              runtime = true;
            };
          };
          fetchInfo = {
            narHash = "sha256-DOhXTLlCkGwCsxYTRR7Ka9X/dlmPAt1ni3xGfULAyKI=";
            type = "tarball";
            url = "https://registry.npmjs.org/wcwidth/-/wcwidth-1.0.1.tgz";
          };
          ident = "wcwidth";
          ltype = "file";
          version = "1.0.1";
        };
      };
      webidl-conversions = {
        "3.0.1" = {
          fetchInfo = {
            narHash = "sha256-UMeIcOqew3KPWTe2NoYe714P0kLNWNMYG+YEqV5qTVg=";
            type = "tarball";
            url = "https://registry.npmjs.org/webidl-conversions/-/webidl-conversions-3.0.1.tgz";
          };
          ident = "webidl-conversions";
          ltype = "file";
          treeInfo = { };
          version = "3.0.1";
        };
      };
      whatwg-url = {
        "5.0.0" = {
          depInfo = {
            tr46 = {
              descriptor = "~0.0.3";
              pin = "0.0.3";
              runtime = true;
            };
            webidl-conversions = {
              descriptor = "^3.0.0";
              pin = "3.0.1";
              runtime = true;
            };
          };
          fetchInfo = {
            narHash = "sha256-GXbxi1vs/ypuwABnqV82s42jMh1mhmVR8gycudzD5vc=";
            type = "tarball";
            url = "https://registry.npmjs.org/whatwg-url/-/whatwg-url-5.0.0.tgz";
          };
          ident = "whatwg-url";
          ltype = "file";
          version = "5.0.0";
        };
      };
      which = {
        "2.0.2" = {
          binInfo = {
            binPairs = {
              node-which = "bin/node-which";
            };
          };
          depInfo = {
            isexe = {
              descriptor = "^2.0.0";
              pin = "2.0.0";
              runtime = true;
            };
          };
          fetchInfo = {
            narHash = "sha256-u114pFUXCCiUamLVVZma0Au+didZhD6RCoGTbrh2OhU=";
            type = "tarball";
            url = "https://registry.npmjs.org/which/-/which-2.0.2.tgz";
          };
          ident = "which";
          ltype = "file";
          version = "2.0.2";
        };
      };
      which-boxed-primitive = {
        "1.0.2" = {
          depInfo = {
            is-bigint = {
              descriptor = "^1.0.1";
              pin = "1.0.4";
              runtime = true;
            };
            is-boolean-object = {
              descriptor = "^1.1.0";
              pin = "1.1.2";
              runtime = true;
            };
            is-number-object = {
              descriptor = "^1.0.4";
              pin = "1.0.7";
              runtime = true;
            };
            is-string = {
              descriptor = "^1.0.5";
              pin = "1.0.7";
              runtime = true;
            };
            is-symbol = {
              descriptor = "^1.0.3";
              pin = "1.0.4";
              runtime = true;
            };
          };
          fetchInfo = {
            narHash = "sha256-5HiYamQ407qG7OtGSNwZSpYIUeWwcT+B54zHUJ5zk5U=";
            type = "tarball";
            url = "https://registry.npmjs.org/which-boxed-primitive/-/which-boxed-primitive-1.0.2.tgz";
          };
          ident = "which-boxed-primitive";
          ltype = "file";
          version = "1.0.2";
        };
      };
      which-typed-array = {
        "1.1.11" = {
          depInfo = {
            available-typed-arrays = {
              descriptor = "^1.0.5";
              pin = "1.0.5";
              runtime = true;
            };
            call-bind = {
              descriptor = "^1.0.2";
              pin = "1.0.2";
              runtime = true;
            };
            for-each = {
              descriptor = "^0.3.3";
              pin = "0.3.3";
              runtime = true;
            };
            gopd = {
              descriptor = "^1.0.1";
              pin = "1.0.1";
              runtime = true;
            };
            has-tostringtag = {
              descriptor = "^1.0.0";
              pin = "1.0.0";
              runtime = true;
            };
          };
          fetchInfo = {
            narHash = "sha256-EGELA1/ELVvjyXq2YrCoNU6Sar/u6UVVwAT9y1iMiBo=";
            type = "tarball";
            url = "https://registry.npmjs.org/which-typed-array/-/which-typed-array-1.1.11.tgz";
          };
          ident = "which-typed-array";
          ltype = "file";
          version = "1.1.11";
        };
      };
      wrap-ansi = {
        "7.0.0" = {
          depInfo = {
            ansi-styles = {
              descriptor = "^4.0.0";
              pin = "4.3.0";
              runtime = true;
            };
            string-width = {
              descriptor = "^4.1.0";
              pin = "4.2.3";
              runtime = true;
            };
            strip-ansi = {
              descriptor = "^6.0.0";
              pin = "6.0.1";
              runtime = true;
            };
          };
          fetchInfo = {
            narHash = "sha256-4STOnmSiJLwhYjl7yafCOFqX+PtBFdAbGTiZEHV+KZM=";
            type = "tarball";
            url = "https://registry.npmjs.org/wrap-ansi/-/wrap-ansi-7.0.0.tgz";
          };
          ident = "wrap-ansi";
          ltype = "file";
          version = "7.0.0";
        };
      };
      wrappy = {
        "1.0.2" = {
          fetchInfo = {
            narHash = "sha256-8EvxGsoK2efCTAOoAHPbfbCoPOJvkmOLPM4XA1rEcVU=";
            type = "tarball";
            url = "https://registry.npmjs.org/wrappy/-/wrappy-1.0.2.tgz";
          };
          ident = "wrappy";
          ltype = "file";
          treeInfo = { };
          version = "1.0.2";
        };
      };
      y18n = {
        "5.0.8" = {
          fetchInfo = {
            narHash = "sha256-iFm2pYwriQ4ikd/5Pw604ag5yU2D3/51Sl4UQ+0nleE=";
            type = "tarball";
            url = "https://registry.npmjs.org/y18n/-/y18n-5.0.8.tgz";
          };
          ident = "y18n";
          ltype = "file";
          treeInfo = { };
          version = "5.0.8";
        };
      };
      yallist = {
        "4.0.0" = {
          fetchInfo = {
            narHash = "sha256-JQNNkqswg1ZH4o8PQS2R8WsZWJtv/5R3vRgc4d1vDR0=";
            type = "tarball";
            url = "https://registry.npmjs.org/yallist/-/yallist-4.0.0.tgz";
          };
          ident = "yallist";
          ltype = "file";
          treeInfo = { };
          version = "4.0.0";
        };
      };
      yaml = {
        "1.10.2" = {
          fetchInfo = {
            narHash = "sha256-JPai4yAf+MK8wsaF0gmRNcCD2HiF2sBzf/YHgnjpWEs=";
            type = "tarball";
            url = "https://registry.npmjs.org/yaml/-/yaml-1.10.2.tgz";
          };
          ident = "yaml";
          ltype = "file";
          treeInfo = { };
          version = "1.10.2";
        };
        "2.3.1" = {
          fetchInfo = {
            narHash = "sha256-1t99bBjM6mNzwLZ7r52s4M818bVZiZSyoaX25kELdZc=";
            type = "tarball";
            url = "https://registry.npmjs.org/yaml/-/yaml-2.3.1.tgz";
          };
          ident = "yaml";
          ltype = "file";
          treeInfo = { };
          version = "2.3.1";
        };
      };
      yaml-js = {
        "0.2.3" = {
          fetchInfo = {
            narHash = "sha256-rSW2xluUlkv/XlYWHpIBcmuxh1GrgXN812qpY6n+JDQ=";
            type = "tarball";
            url = "https://registry.npmjs.org/yaml-js/-/yaml-js-0.2.3.tgz";
          };
          ident = "yaml-js";
          ltype = "file";
          treeInfo = { };
          version = "0.2.3";
        };
      };
      yargs = {
        "17.3.1" = {
          depInfo = {
            cliui = {
              descriptor = "^7.0.2";
              pin = "7.0.4";
              runtime = true;
            };
            escalade = {
              descriptor = "^3.1.1";
              pin = "3.1.1";
              runtime = true;
            };
            get-caller-file = {
              descriptor = "^2.0.5";
              pin = "2.0.5";
              runtime = true;
            };
            require-directory = {
              descriptor = "^2.1.1";
              pin = "2.1.1";
              runtime = true;
            };
            string-width = {
              descriptor = "^4.2.3";
              pin = "4.2.3";
              runtime = true;
            };
            y18n = {
              descriptor = "^5.0.5";
              pin = "5.0.8";
              runtime = true;
            };
            yargs-parser = {
              descriptor = "^21.0.0";
              pin = "21.1.1";
              runtime = true;
            };
          };
          fetchInfo = {
            narHash = "sha256-K1QklvfMEX4ZS83sMuG5Yl4ak4JfNtdPA/YOwqjeUDs=";
            type = "tarball";
            url = "https://registry.npmjs.org/yargs/-/yargs-17.3.1.tgz";
          };
          ident = "yargs";
          ltype = "file";
          version = "17.3.1";
        };
      };
      yargs-parser = {
        "21.1.1" = {
          fetchInfo = {
            narHash = "sha256-mbMbMuJ6Cit1Xns/Fi77RJytrnfC7+AzvAU+x5cdR6I=";
            type = "tarball";
            url = "https://registry.npmjs.org/yargs-parser/-/yargs-parser-21.1.1.tgz";
          };
          ident = "yargs-parser";
          ltype = "file";
          treeInfo = { };
          version = "21.1.1";
        };
      };
      yocto-queue = {
        "0.1.0" = {
          fetchInfo = {
            narHash = "sha256-DpbkBR6X0fZcRRdqavXuN5z2r2EfhSO5pbc2PuZwDFY=";
            type = "tarball";
            url = "https://registry.npmjs.org/yocto-queue/-/yocto-queue-0.1.0.tgz";
          };
          ident = "yocto-queue";
          ltype = "file";
          treeInfo = { };
          version = "0.1.0";
        };
      };
      zod = {
        "3.21.4" = {
          fetchInfo = {
            narHash = "sha256-xyP+/+1G4HB94Z6Hmcb/5MRRr9FmUzWRprObG5AJD6U=";
            type = "tarball";
            url = "https://registry.npmjs.org/zod/-/zod-3.21.4.tgz";
          };
          ident = "zod";
          ltype = "file";
          treeInfo = { };
          version = "3.21.4";
        };
      };
    };
  };
}
