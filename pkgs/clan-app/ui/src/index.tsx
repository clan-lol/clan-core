/* @refresh reload */
import { render } from "solid-js/web";

import "./index.css";
import { QueryClientProvider } from "@tanstack/solid-query";
import { Routes } from "@/src/routes";
import { Router } from "@solidjs/router";
import { Layout } from "@/src/routes/Layout";
import { SolidQueryDevtools } from "@tanstack/solid-query-devtools";
import { ApiClientProvider } from "./hooks/ApiClient";
import { callApi } from "./hooks/api";
import { DefaultQueryClient } from "@/src/hooks/queries";

const root = document.getElementById("app");

if (import.meta.env.DEV && !(root instanceof HTMLElement)) {
  throw new Error(
    "Root element not found. Did you forget to add it to your index.html? Or maybe the id attribute got misspelled?",
  );
}
if (import.meta.env.DEV) {
  console.log("Development mode");
}

render(
  () => (
    <ApiClientProvider client={{ fetch: callApi }}>
      <QueryClientProvider client={DefaultQueryClient}>
        {import.meta.env.DEV && <SolidQueryDevtools initialIsOpen={true} />}
        <Router root={Layout}>{Routes}</Router>
      </QueryClientProvider>
    </ApiClientProvider>
  ),
  root!,
);
