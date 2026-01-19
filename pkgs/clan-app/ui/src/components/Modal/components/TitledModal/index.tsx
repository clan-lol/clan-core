import { FlowComponent } from "solid-js";
import { Dialog } from "@kobalte/core/dialog";
import styles from "./TitledModal.module.css";
import { Typography } from "@/components/Typography/Typography";
import Icon from "@/components/Icon";
import { useUIContext } from "@/models";

const TitledModal: FlowComponent<{ title: string }> = (props) => {
  const [, { closeModal }] = useUIContext();
  return (
    <Dialog.Content class={styles.container}>
      <div class={styles.titlebar}>
        <Typography hierarchy="label" family="mono" size="xs" in="Modal-title">
          {props.title}
        </Typography>
        <Dialog.CloseButton on:click={() => closeModal()}>
          <Icon name="close" size="0.75rem" />
        </Dialog.CloseButton>
      </div>
      {props.children}
    </Dialog.Content>
  );
};
export default TitledModal;
