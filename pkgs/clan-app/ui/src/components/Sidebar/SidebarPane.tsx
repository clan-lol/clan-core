import { createSignal, JSX, onMount, Show } from "solid-js";
import "./SidebarPane.css";
import { Typography } from "@/src/components/Typography/Typography";
import Icon from "../Icon/Icon";
import { Button as KButton } from "@kobalte/core/button";
import cx from "classnames";

export interface SidebarPaneProps {
  class?: string;
  title: string;
  onClose: () => void;
  subHeader?: () => JSX.Element;
  children: JSX.Element;
}

export const SidebarPane = (props: SidebarPaneProps) => {
  const [closing, setClosing] = createSignal(false);
  const [open, setOpened] = createSignal(true);

  const onClose = () => {
    setClosing(true);
    setTimeout(() => props.onClose(), 550);
  };
  onMount(() => {
    setTimeout(() => {
      setOpened(true);
    }, 250);
  });

  return (
    <div
      class={cx("sidebar-pane", props.class, {
        closing: closing(),
        open: open(),
      })}
    >
      <div class="header">
        <Typography hierarchy="body" size="s" weight="bold" inverted={true}>
          {props.title}
        </Typography>
        <KButton onClick={onClose}>
          <Icon icon="Close" color="primary" size="0.75rem" inverted={true} />
        </KButton>
      </div>
      <Show when={props.subHeader}>
        <div class="sub-header">{props.subHeader!()}</div>
      </Show>
      <div class="body">{props.children}</div>
    </div>
  );
};
