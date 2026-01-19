import cx from "classnames";
import styles from "./ListClans.module.css";
import { Typography } from "@/components/Typography/Typography";
import { Component, For } from "solid-js";
import { NavSection } from "@/components/NavSection/NavSection";
import { useClansContext, useUIContext } from "@/models";
import TitledModal from "../components/TitledModal";

const ListClans: Component = () => {
  const [, { closeModal }] = useUIContext();
  const [clans, { activateClan }] = useClansContext();

  return (
    <TitledModal title="Select Clan">
      <div class={cx(styles.container)}>
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
                  onClick={async () => {
                    await activateClan(clan);
                    closeModal();
                  }}
                />
              </li>
            )}
          </For>
        </ul>
      </div>
    </TitledModal>
  );
};
export default ListClans;
