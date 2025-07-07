import { createSignal, JSX } from "solid-js";
import { Dialog as KDialog } from "@kobalte/core/dialog";
import "./Modal.css";
import { Typography } from "../Typography/Typography";
import Icon from "../Icon/Icon";

export interface ModalContext {
  close(): void;
}

export interface ModalProps {
  id?: string;
  title: string;
  onClose: () => void;
  children: (ctx: ModalContext) => JSX.Element;
}

export const Modal = (props: ModalProps) => {
  const [open, setOpen] = createSignal(true);

  return (
    <KDialog id={props.id} open={open()} modal={true}>
      <KDialog.Portal>
        <KDialog.Content class="modal-content">
          <div class="header">
            <Typography class="title" hierarchy="label" family="mono" size="xs">
              {props.title}
            </Typography>
            <KDialog.CloseButton onClick={() => setOpen(false)}>
              <Icon icon="Close" size="0.75rem" />
            </KDialog.CloseButton>
          </div>
          <div class="body">
            {props.children({ close: () => setOpen(false) })}
          </div>
        </KDialog.Content>
      </KDialog.Portal>
    </KDialog>
  );
};
