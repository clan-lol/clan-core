import { Component, JSX, Show } from "solid-js";
import { Dialog as KDialog } from "@kobalte/core/dialog";
import styles from "./Modal.module.css";
import { Typography } from "../Typography/Typography";
import Icon from "../Icon/Icon";
import cx from "classnames";
import { Dynamic } from "solid-js/web";

export interface ModalContext {
  close(): void;
}

export interface ModalProps {
  id?: string;
  title: string;
  onClose: () => void;
  children: (ctx: ModalContext) => JSX.Element;
  mount?: Node;
  class?: string;
  metaHeader?: Component;
  disablePadding?: boolean;
  open: boolean;
}

export const Modal = (props: ModalProps) => {
  return (
    <Show when={props.open}>
      <KDialog id={props.id} open={props.open} modal={true}>
        <KDialog.Portal mount={props.mount}>
          <div class={styles.backdrop} />
          <div class={styles.contentWrapper}>
            <KDialog.Content class={cx(styles.modal_content, props.class)}>
              <div class={styles.modal_header}>
                <Typography
                  class={styles.modal_title}
                  hierarchy="label"
                  family="mono"
                  size="xs"
                >
                  {props.title}
                </Typography>
                <KDialog.CloseButton
                  onClick={() => {
                    props.onClose();
                  }}
                >
                  <Icon icon="Close" size="0.75rem" />
                </KDialog.CloseButton>
              </div>
              <Show when={props.metaHeader}>
                {(metaHeader) => (
                  <>
                    <div class="flex h-9 items-center px-6 py-2 bg-def-1">
                      <Dynamic component={metaHeader()} />
                    </div>
                    <div class={styles.header_divider} />
                  </>
                )}
              </Show>
              <div
                class={styles.modal_body}
                data-no-padding={props.disablePadding}
              >
                {props.children({
                  close: () => {
                    props.onClose();
                  },
                })}
              </div>
            </KDialog.Content>
          </div>
        </KDialog.Portal>
      </KDialog>
    </Show>
  );
};
