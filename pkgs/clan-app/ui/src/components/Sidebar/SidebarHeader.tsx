import styles from "./SidebarHeader.module.css";
import Icon from "@/src/components/Icon/Icon";
import { DropdownMenu } from "@kobalte/core/dropdown-menu";
import { Typography } from "../Typography/Typography";
import { createSignal, For, Show, Suspense } from "solid-js";
import { Button } from "../Button/Button";
import { ClanSettingsModal } from "@/src/modals/ClanSettingsModal/ClanSettingsModal";
import { useClanContext } from "@/src/contexts/ClanContext";

export const SidebarHeader = () => {
  const [open, setOpen] = createSignal(false);
  const [showSettings, setShowSettings] = createSignal(false);
  const { clans } = useClanContext()!;

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
                {clans()?.active?.data.name.charAt(0).toUpperCase()}
              </Typography>
            </div>
            <Typography
              hierarchy="label"
              size="s"
              weight="bold"
              inverted={!open()}
            >
              {clans()?.active?.data.name}
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
                  onClick={() => clans()?.active?.deactivate()}
                >
                  Add
                </Button>
              </DropdownMenu.GroupLabel>
              <div class={styles.dropdownGroupItems}>
                <For each={Array.from(clans()!)}>
                  {(clan) => (
                    <Suspense fallback={"Loading..."}>
                      <DropdownMenu.Item
                        class={styles.dropdownItem}
                        onSelect={() => {
                          clan.activate();
                        }}
                      >
                        <Typography hierarchy="label" size="xs" weight="medium">
                          {clan.data.name}
                        </Typography>
                      </DropdownMenu.Item>
                    </Suspense>
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
