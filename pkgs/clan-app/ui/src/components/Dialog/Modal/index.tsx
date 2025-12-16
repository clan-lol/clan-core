import { Component, JSX, Show } from "solid-js";
import { Dialog } from "@kobalte/core/dialog";
import styles from "./Modal.module.css";
import { Typography } from "../../Typography/Typography";
import Icon from "../../Icon/Icon";
import { useUIContext } from "@/src/models";
import { Dynamic } from "solid-js/web";
import { mapObjectKeys } from "@/src/util";

const modals: Record<
  string,
  {
    default: Component;
    config?: ModalConfig;
  }
> = mapObjectKeys(
  import.meta.glob(["./*/index.tsx", "./*.tsx", "!./index.tsx", "!./*.*.tsx"], {
    eager: true,
  }),
  ([path]) => {
    const result = /^.\/(?:([^/]+)\/index\.tsx|([^/]+)\.tsx)$/.exec(path);
    const name = result && (result[1] || result[2]);
    if (!name) {
      throw new Error("Failed to extract the modal name from import.meta.glob");
    }
    return name;
  },
);

export type ModalConfig = {
  title: string;
};

// If some content 
const ModalComponent: Component = () => {
  const [ui, { closeModal }] = useUIContext();
  const modal = () => ui.modal && modals[ui.modal.type];
  return (
    <Dialog open={!!ui.modal} modal={true}>
      <Dialog.Portal>
        <Dialog.Overlay class={styles.backdrop}>
          <Dialog.Content class={styles.container}>
            <div class={styles.titlebar}>
              <Typography
                hierarchy="label"
                family="mono"
                size="xs"
                in="Modal-title"
              >
                {modal()?.config?.title}
              </Typography>
              <Dialog.CloseButton on:click={() => closeModal()}>
                <Icon icon="Close" size="0.75rem" />
              </Dialog.CloseButton>
            </div>
            <div class={styles.content}>
              <Show when={ui.modal}>
                {/* TODO: fix the z-index issue for <Select /> */}
                <Dynamic component={modal()?.default} />
              </Show>
            </div>
          </Dialog.Content>
        </Dialog.Overlay>
      </Dialog.Portal>
    </Dialog>
  );
};
export default ModalComponent;

export const ModalHeading: Component<{ text: string; tail?: JSX.Element }> = (
  props,
) => {
  return (
    <div class={styles.headingbar}>
      <div class={styles.headingbarInner}>
        <Typography
          hierarchy="label"
          family="mono"
          size="default"
          weight="medium"
        >
          {props.text}
        </Typography>
        <Show when={props.tail}>{props.tail}</Show>
      </div>
    </div>
  );
};
