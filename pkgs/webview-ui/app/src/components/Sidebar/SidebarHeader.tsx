import { createSignal, Show } from "solid-js";
import { Typography } from "@/src/components/Typography";
import { SidebarFlyout } from "./SidebarFlyout";
import "./css/sidebar.css";
import Icon from "../icon";

interface SidebarProps {
  clanName: string;
  showFlyout?: () => boolean;
}

const ClanProfile = (props: SidebarProps) => {
  return (
    <div
      class={`sidebar__profile ${props.showFlyout?.() ? "sidebar__profile--flyout" : ""}`}
    >
      <Typography
        class="sidebar__profile__character"
        tag="span"
        hierarchy="title"
        size="m"
        weight="bold"
        color="primary"
        inverted={true}
      >
        {props.clanName.slice(0, 1).toUpperCase()}
      </Typography>
    </div>
  );
};

const ClanTitle = (props: SidebarProps) => {
  return (
    <Typography
      tag="h3"
      hierarchy="body"
      size="default"
      weight="medium"
      color="primary"
      inverted={true}
    >
      {props.clanName}
    </Typography>
  );
};

export const SidebarHeader = (props: SidebarProps) => {
  const [showFlyout, toggleFlyout] = createSignal(false);

  function handleClick() {
    toggleFlyout(!showFlyout());
  }

  return (
    <header class="sidebar__header">
      <div onClick={handleClick} class="sidebar__header__inner">
        {/* <ClanProfile clanName={props.clanName} showFlyout={showFlyout} /> */}
        <div class="w-full text-white pl-1">
          <ClanTitle clanName={props.clanName} />
        </div>
        <Show
          when={showFlyout}
          fallback={<Icon size={12} class="text-white" icon="CaretDown" />}
        >
          <Icon size={12} class="text-white" icon="CaretDown" />
        </Show>
      </div>
      {showFlyout() && <SidebarFlyout />}
    </header>
  );
};
