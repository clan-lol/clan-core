import { Component } from "solid-js";
import { Dynamic } from "solid-js/web";
import { Dialog } from "@kobalte/core/dialog";
import { mapObjectKeys } from "@/src/util";
import { useUIContext } from "@/src/models";
import styles from "./Modal.module.css";

const modals: Record<string, Component> = mapObjectKeys(
  import.meta.glob(
    [
      "./*/index.tsx",
      "./*.tsx",
      "!./index.tsx",
      "!./*.*.tsx",
      "!./frames/**",
      "!./components/**",
    ],
    {
      eager: true,
      import: "default",
    },
  ),
  ([path]) => {
    const result = /^.\/(?:([^/]+)\/index\.tsx|([^/]+)\.tsx)$/.exec(path);
    const name = result && (result[1] || result[2]);
    if (!name) {
      throw new Error("Failed to extract the modal name from import.meta.glob");
    }
    return name;
  },
);

const Modal: Component = () => {
  const [ui] = useUIContext();
  const modal = () => ui.modal && modals[ui.modal.type];
  return (
    <Dialog open={!!ui.modal} modal={true}>
      <Dialog.Portal>
        <Dialog.Overlay class={styles.backdrop}>
          <Dynamic component={modal()!} />
        </Dialog.Overlay>
      </Dialog.Portal>
    </Dialog>
  );
};
export default Modal;
