{
  floco = {
    pdefs = {
      "@clan/colors" = {
        "1.0.0" = {
          depInfo = {
            "@material/material-color-utilities" = {
              descriptor = "^0.2.6";
              pin = "0.2.7";
            };
            "@types/node" = {
              descriptor = "^20.3.2";
              pin = "20.8.2";
            };
            typescript = {
              descriptor = "^5.1.5";
              pin = "5.2.2";
            };
          };
          fetchInfo = "path:..";
          ident = "@clan/colors";
          lifecycle = {
            build = true;
          };
          ltype = "dir";
          treeInfo = {
            "node_modules/@material/material-color-utilities" = {
              dev = true;
              key = "@material/material-color-utilities/0.2.7";
            };
            "node_modules/@types/node" = {
              dev = true;
              key = "@types/node/20.8.2";
            };
            "node_modules/typescript" = {
              dev = true;
              key = "typescript/5.2.2";
            };
          };
          version = "1.0.0";
        };
      };
      "@material/material-color-utilities" = {
        "0.2.7" = {
          fetchInfo = {
            narHash = "sha256-hRYXqtkoXHoB30v1hstWz7dO7dNeBb6EJqZG66hHi94=";
            type = "tarball";
            url = "https://registry.npmjs.org/@material/material-color-utilities/-/material-color-utilities-0.2.7.tgz";
          };
          ident = "@material/material-color-utilities";
          ltype = "file";
          treeInfo = { };
          version = "0.2.7";
        };
      };
      "@types/node" = {
        "20.8.2" = {
          fetchInfo = {
            narHash = "sha256-o4hyob1kLnm0OE8Rngm0d6XJxobpMlYSoquusktmLPk=";
            type = "tarball";
            url = "https://registry.npmjs.org/@types/node/-/node-20.8.2.tgz";
          };
          ident = "@types/node";
          ltype = "file";
          treeInfo = { };
          version = "20.8.2";
        };
      };
      typescript = {
        "5.2.2" = {
          binInfo = {
            binPairs = {
              tsc = "bin/tsc";
              tsserver = "bin/tsserver";
            };
          };
          fetchInfo = {
            narHash = "sha256-io9rXH9RLRLB0484ZdvcqblLQquLFUBGxDuwSixWxus=";
            type = "tarball";
            url = "https://registry.npmjs.org/typescript/-/typescript-5.2.2.tgz";
          };
          ident = "typescript";
          ltype = "file";
          treeInfo = { };
          version = "5.2.2";
        };
      };
    };
  };
}
