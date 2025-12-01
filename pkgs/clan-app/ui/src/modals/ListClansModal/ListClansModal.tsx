import { Modal } from "../../components/Modal/Modal";
import cx from "classnames";
import styles from "./ListClansModal.module.css";
import { Typography } from "@/src/components/Typography/Typography";
import { For, Show } from "solid-js";
import { activeClanURI, clanURIs, setActiveClanURI } from "@/src/stores/clan";
import { useClanListQuery } from "@/src/hooks/queries";
import { Alert } from "@/src/components/Alert/Alert";
import { NavSection } from "@/src/components/NavSection/NavSection";
import { useClanContext } from "@/src/contexts/ClanContext";

export interface ListClansModalProps {
  onClose?: () => void;
}

export const ListClansModal = (props: ListClansModalProps) => {
  const { clans } = useClanContext()!;

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
          <For each={Array.from(clans() || [])}>
            {(clan) => (
              <li>
                <NavSection
                  label={clan.data.name}
                  description={clan.data.description}
                  onClick={() => {
                    if (clan.isActive) {
                      location.reload();
                    } else {
                      clan.activate();
                    }
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
