/* @refresh reload */
import { render } from "solid-js/web";

import "./index.css";
import { QueryClient, QueryClientProvider } from "@tanstack/solid-query";
import { Routes } from "@/src/routes";
import { Router } from "@solidjs/router";
import { Layout } from "@/src/routes/Layout";
import { SolidQueryDevtools } from "@tanstack/solid-query-devtools";

export const client = new QueryClient();

const root = document.getElementById("app");

if (import.meta.env.DEV && !(root instanceof HTMLElement)) {
  throw new Error(
    "Root element not found. Did you forget to add it to your index.html? Or maybe the id attribute got misspelled?",
  );
}

render(
  () => (
    <QueryClientProvider client={client}>
      {import.meta.env.DEV && <SolidQueryDevtools />}
      <Router root={Layout}>{Routes}</Router>
    </QueryClientProvider>
  ),
  root!,
);
