import cx from "classnames";
import styles from "./ListClans.module.css";
import { Typography } from "@/src/components/Typography/Typography";
import { batch, Component, For } from "solid-js";
import { NavSection } from "@/src/components/NavSection/NavSection";
import { useClansContext, useUIContext } from "@/src/models";

const ListClans: Component = () => {
  const [, { closeModal }] = useUIContext();
  const [clans, { activateClan }] = useClansContext();

  return (
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
                  batch(() => {
                    activateClan(clan);
                    closeModal();
                  });
                }}
              />
            </li>
          )}
        </For>
      </ul>
    </div>
  );
};
export default ListClans;

export const title = "Select Clan";
