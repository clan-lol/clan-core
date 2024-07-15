/* @refresh reload */
import { render } from "solid-js/web";

import "./index.css";
import App from "./App";
import { QueryClient, QueryClientProvider } from "@tanstack/solid-query";

const client = new QueryClient();

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
}

render(
  () => (
    <QueryClientProvider client={client}>
      <App />
    </QueryClientProvider>
  ),
  // eslint-disable-next-line @typescript-eslint/no-non-null-assertion
  root!
);
