import {
  Component,
  JSX,
  Show,
  createContext,
  createSignal,
  useContext,
  ParentComponent,
} from "solid-js";
import { Dialog as KDialog } from "@kobalte/core/dialog";
import styles from "./Modal.module.css";
import { Typography } from "../Typography/Typography";
import Icon from "../Icon/Icon";
import cx from "classnames";
import { Dynamic } from "solid-js/web";

export interface ModalContextType {
  portalRef: HTMLDivElement;
}

const ModalContext = createContext<unknown>();

export const useModalContext = () => {
  const context = useContext(ModalContext);
  if (!context) {
    return null;
  }
  return context as ModalContextType;
};

const defaultContentWrapper: ParentComponent = (props): JSX.Element => (
  <>{props.children}</>
);

export interface ModalProps {
  id?: string;
  title: string;
  onClose?: () => void;
  children: JSX.Element;
  mount?: Node;
  class?: string;
  metaHeader?: Component;
  wrapContent?: ParentComponent;
  disablePadding?: boolean;
  open: boolean;
}

export const Modal = (props: ModalProps) => {
  const [portalRef, setPortalRef] = createSignal<HTMLDivElement>();

  // allows wrapping the dialog content in a component
  // useful with forms where the submit button is in the header
  const contentWrapper: Component = props.wrapContent || defaultContentWrapper;

  return (
    <Show when={props.open}>
      <KDialog id={props.id} open={props.open} modal={true}>
        <KDialog.Portal mount={props.mount}>
          <div class={styles.backdrop} />
          <div class={styles.contentWrapper}>
            <KDialog.Content
              class={cx(styles.modal_content, props.class)}
              onEscapeKeyDown={props.onClose}
            >
              {contentWrapper({
                children: (
                  <>
                    <div class={styles.modal_header}>
                      <Typography
                        hierarchy="label"
                        family="mono"
                        size="xs"
                        in="Modal-title"
                      >
                        {props.title}
                      </Typography>
                      <Show when={props.onClose}>
                        <KDialog.CloseButton onClick={props.onClose}>
                          <Icon icon="Close" size="0.75rem" />
                        </KDialog.CloseButton>
                      </Show>
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
                      ref={setPortalRef}
                    >
                      <ModalContext.Provider
                        value={{ portalRef: portalRef()! }}
                      >
                        {props.children}
                      </ModalContext.Provider>
                    </div>
                  </>
                ),
              })}
            </KDialog.Content>
          </div>
        </KDialog.Portal>
      </KDialog>
    </Show>
  );
};
