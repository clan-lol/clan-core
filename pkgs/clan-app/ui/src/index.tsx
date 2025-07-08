/* @refresh reload */
import { render } from "solid-js/web";

import "./index.css";
import { QueryClient } from "@tanstack/solid-query";

export const client = new QueryClient();

const root = document.getElementById("app");

if (import.meta.env.DEV && !(root instanceof HTMLElement)) {
  throw new Error(
    "Root element not found. Did you forget to add it to your index.html? Or maybe the id attribute got misspelled?",
  );
}
if (import.meta.env.DEV) {
  console.log("Development mode");
  // Load the debugger in development mode
  await import("solid-devtools");
}

render(() => <h1>Hello World</h1>, root!);
