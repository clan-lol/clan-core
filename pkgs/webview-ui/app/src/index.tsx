/* @refresh reload */
import { render } from "solid-js/web";

import "./index.css";
import App from "./App";
import { getFakeResponse } from "../mock";
const root = document.getElementById("app");

window.clan = window.clan || {};

if (import.meta.env.DEV && !(root instanceof HTMLElement)) {
  throw new Error(
    "Root element not found. Did you forget to add it to your index.html? Or maybe the id attribute got misspelled?"
  );
}

if (import.meta.env.DEV) {
  console.log("Development mode");
  // Load the debugger in development mode
  await import("solid-devtools");
  window.webkit = window.webkit || {
    messageHandlers: {
      gtk: {
        postMessage: (postMessage) => {
          const { method, data } = postMessage;
          console.debug("Python API call", { method, data });
          setTimeout(() => {
            const mock = getFakeResponse(method, data);
            console.log("Returning mock-data: ", { mock });

            window.clan[method](JSON.stringify(mock));
          }, 200);
        },
      },
    },
  };
}
// eslint-disable-next-line @typescript-eslint/no-non-null-assertion
render(() => <App />, root!);
