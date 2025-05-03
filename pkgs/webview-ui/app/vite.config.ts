import { defineConfig } from "vite";
import solidPlugin from "vite-plugin-solid";
import solidSvg from "vite-plugin-solid-svg";
import devtools from "solid-devtools/vite";
import path from "node:path";
import { exec } from "child_process";

// watch also clan-cli to catch api changes
const clanCliDir = path.resolve(__dirname, "../../clan-cli");

function regenPythonApiOnFileChange() {
  return {
    name: "run-python-script-on-change",
    handleHotUpdate({}) {
      exec("reload-python-api.sh", (err, stdout, stderr) => {
        if (err) {
          console.error(`reload-python-api.sh error:\n${stderr}`);
        }
      });
    },
    configureServer(server: import("vite").ViteDevServer) {
      server.watcher.add([clanCliDir]);
    },
  };
}

export default defineConfig({
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "./"), // Adjust the path as needed
    },
  },
  plugins: [
    /*
    Uncomment the following line to enable solid-devtools.
    For more info see https://github.com/thetarnav/solid-devtools/tree/main/packages/extension#readme
    */
    devtools(),
    solidPlugin(),
    solidSvg(),
    regenPythonApiOnFileChange(),
  ],
  server: {
    port: 3000,
  },
  build: {
    target: "safari11",
    //  assetsDi
    manifest: true,
  },
});
