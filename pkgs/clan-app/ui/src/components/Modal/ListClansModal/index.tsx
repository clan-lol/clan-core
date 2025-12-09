import { Modal } from "../Modal";
import cx from "classnames";
import styles from "./ListClansModal.module.css";
import { Typography } from "@/src/components/Typography/Typography";
import { Component, For } from "solid-js";
import { NavSection } from "@/src/components/NavSection/NavSection";
import { useClansContext } from "@/src/models";

const ListClansModal: Component<{
  onClose?: () => void;
}> = (props) => {
  const [clans, { activateClan }] = useClansContext();

  return (
    <Modal
      title="Select Clan"
      open
      onClose={props.onClose}
      class={cx(styles.modal)}
    >
      <div class={cx(styles.content)}>
        <div class={cx(styles.header)}>
          <Typography
            hierarchy="label"
            family="mono"
            size="xs"
            color="tertiary"
            transform="uppercase"
          >
            Your Clans
          </Typography>
        </div>
        <ul class={cx(styles.clans)}>
          <For each={clans.all}>
            {(clan) => (
              <li>
                <NavSection
                  label={clan.data.name}
                  description={clan.data.description}
                  onClick={() => {
                    activateClan(clan);
                  }}
                />
              </li>
            )}
          </For>
        </ul>
      </div>
    </Modal>
  );
};
export default ListClansModal;
