import { render } from "solid-js/web";

import "./index.css";
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

render(() => <Entrypoint />, root);
