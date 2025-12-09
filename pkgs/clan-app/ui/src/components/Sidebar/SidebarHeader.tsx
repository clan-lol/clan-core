import styles from "./SidebarHeader.module.css";
import Icon from "@/src/components/Icon/Icon";
import { DropdownMenu } from "@kobalte/core/dropdown-menu";
import { Typography } from "../Typography/Typography";
import { Component, createSignal, For, Show } from "solid-js";
import { Button } from "../Button/Button";
import { ClanSettingsModal } from "@/src/components/Modal/ClanSettingsModal";
import { useClanContext, useClansContext } from "@/src/models";

const SidebarHeader: Component = () => {
  const [open, setOpen] = createSignal(false);
  const [showSettings, setShowSettings] = createSignal(false);
  const [clan] = useClanContext();
  const [clans, { activateClan, deactivateClan }] = useClansContext();

  return (
    <div class={styles.sidebarHeader}>
      <Show when={showSettings()}>
        <ClanSettingsModal
          onClose={() => {
            // TODO: refresh clan data
            setShowSettings(false);
          }}
        />
      </Show>
      <DropdownMenu open={open()} onOpenChange={setOpen} sameWidth={true}>
        <DropdownMenu.Trigger class={styles.dropDownTrigger}>
          <div class={styles.clanLabel}>
            <div class={styles.clanIcon}>
              <Typography
                hierarchy="label"
                size="s"
                weight="bold"
                inverted={true}
              >
                {clan().data.name.charAt(0).toUpperCase()}
              </Typography>
            </div>
            <Typography
              hierarchy="label"
              size="s"
              weight="bold"
              inverted={!open()}
            >
              {clan().data.name}
            </Typography>
          </div>
          <DropdownMenu.Icon>
            <Icon icon={"CaretDown"} inverted={!open()} size="0.75rem" />
          </DropdownMenu.Icon>
        </DropdownMenu.Trigger>
        <DropdownMenu.Portal>
          <DropdownMenu.Content class={styles.dropDownContent}>
            <DropdownMenu.Item
              class={styles.dropdownItem}
              onSelect={() => setShowSettings(true)}
            >
              <Icon
                icon="Settings"
                size="0.75rem"
                inverted={true}
                color="tertiary"
              />
              <Typography hierarchy="label" size="xs" weight="medium">
                Settings
              </Typography>
            </DropdownMenu.Item>
            <DropdownMenu.Group class={styles.dropdownGroup}>
              <DropdownMenu.GroupLabel class={styles.dropdownGroupLabel}>
                <Typography
                  hierarchy="label"
                  family="mono"
                  size="xs"
                  color="tertiary"
                  transform="uppercase"
                >
                  Your Clans
                </Typography>
                <Button
                  hierarchy="secondary"
                  ghost
                  size="xs"
                  icon="Plus"
                  onClick={() => deactivateClan()}
                >
                  Add
                </Button>
              </DropdownMenu.GroupLabel>
              <div class={styles.dropdownGroupItems}>
                <For each={clans.all}>
                  {(clan) => (
                    <DropdownMenu.Item
                      class={styles.dropdownItem}
                      onSelect={async () => {
                        await activateClan(clan);
                      }}
                    >
                      <Typography hierarchy="label" size="xs" weight="medium">
                        {clan.data.name}
                      </Typography>
                    </DropdownMenu.Item>
                  )}
                </For>
              </div>
            </DropdownMenu.Group>
          </DropdownMenu.Content>
        </DropdownMenu.Portal>
      </DropdownMenu>
    </div>
  );
};
export default SidebarHeader;
