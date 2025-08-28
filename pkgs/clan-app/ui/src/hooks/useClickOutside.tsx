import { onCleanup } from "solid-js";

export function useClickOutside(
  el: () => HTMLElement | undefined,
  handler: (e: MouseEvent) => void,
) {
  const listener = (e: MouseEvent) => {
    const element = el();
    if (element && !element.contains(e.target as Node)) {
      handler(e);
    }
  };
  document.addEventListener("mousedown", listener);
  onCleanup(() => document.removeEventListener("mousedown", listener));
}
