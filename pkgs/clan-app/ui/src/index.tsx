/* @refresh reload */
import { ErrorBoundary, render } from "solid-js/web";

import "./index.css";
import { QueryClientProvider } from "@tanstack/solid-query";
import { ApiClientProvider } from "./hooks/ApiClient";
import { callApi } from "./hooks/api";
import { DefaultQueryClient } from "@/src/hooks/queries";
import { Toaster } from "solid-toast";
import Entrypoint from "./Entrypoint";

const root = document.getElementById("app")!;

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
    <ErrorBoundary
      fallback={(error, reset) => {
        console.error(error);
        return (
          <div>
            <p>{error.message}</p>
            <button onClick={reset}>Try Again</button>
          </div>
        );
      }}
    >
      <ApiClientProvider client={{ fetch: callApi }}>
        {/* Temporary solution */}
        <Toaster toastOptions={{}} />
        <QueryClientProvider client={DefaultQueryClient}>
          <Entrypoint />
        </QueryClientProvider>
      </ApiClientProvider>
    </ErrorBoundary>
  ),
  root,
);
