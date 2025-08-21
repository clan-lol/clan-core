import "./SidebarHeader.css";
import Icon from "@/src/components/Icon/Icon";
import { DropdownMenu } from "@kobalte/core/dropdown-menu";
import { useNavigate } from "@solidjs/router";
import { Typography } from "../Typography/Typography";
import { createSignal, For, Suspense, useContext } from "solid-js";
import {
  navigateToClan,
  navigateToOnboarding,
  useClanURI,
} from "@/src/hooks/clan";
import { setActiveClanURI } from "@/src/stores/clan";
import { Button } from "../Button/Button";
import { ClanContext } from "@/src/routes/Clan/Clan";

export const SidebarHeader = () => {
  const navigate = useNavigate();

  const [open, setOpen] = createSignal(false);

  // get information about the current active clan
  const ctx = useContext(ClanContext);

  if (!ctx) {
    throw new Error("SidebarContext not found");
  }

  const clanURI = useClanURI();

  const clanChar = () =>
    ctx?.activeClanQuery?.data?.name.charAt(0).toUpperCase();
  const clanName = () => ctx?.activeClanQuery?.data?.name;

  const clans = () => ctx.otherClanQueries.filter((clan) => !clan.isError);

  return (
    <div class="sidebar-header">
      <Suspense fallback={"Loading..."}>
        <DropdownMenu open={open()} onOpenChange={setOpen} sameWidth={true}>
          <DropdownMenu.Trigger class="dropdown-trigger">
            <div class="clan-label">
              <div class="clan-icon">
                <Typography
                  hierarchy="label"
                  size="s"
                  weight="bold"
                  inverted={true}
                >
                  {clanChar()}
                </Typography>
              </div>
              <Typography
                hierarchy="label"
                size="s"
                weight="bold"
                inverted={!open()}
              >
                {clanName()}
              </Typography>
            </div>
            <DropdownMenu.Icon>
              <Icon icon={"CaretDown"} inverted={!open()} size="0.75rem" />
            </DropdownMenu.Icon>
          </DropdownMenu.Trigger>
          <DropdownMenu.Portal>
            <DropdownMenu.Content class="sidebar-dropdown-content">
              <DropdownMenu.Item
                class="dropdown-item"
                onSelect={() => navigateToClan(navigate, clanURI)}
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
              <DropdownMenu.Group class="dropdown-group">
                <DropdownMenu.GroupLabel class="dropdown-group-label">
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
                    startIcon="Plus"
                    onClick={() => navigateToOnboarding(navigate, true)}
                  >
                    Add
                  </Button>
                </DropdownMenu.GroupLabel>
                <div class="dropdown-group-items">
                  <For each={clans()}>
                    {(clan) => (
                      <Suspense fallback={"Loading..."}>
                        <DropdownMenu.Item
                          class="dropdown-item"
                          onSelect={() => {
                            setActiveClanURI(clan.data!.uri);
                          }}
                        >
                          <Typography
                            hierarchy="label"
                            size="xs"
                            weight="medium"
                          >
                            {clan.data?.name}
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
      </Suspense>
    </div>
  );
};
