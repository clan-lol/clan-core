import { createSignal, JSX, onMount } from "solid-js";
import "./SidebarPane.css";
import { Typography } from "@/src/components/Typography/Typography";
import Icon from "../Icon/Icon";
import { Button as KButton } from "@kobalte/core/button";
import cx from "classnames";

export interface SidebarPaneProps {
  title: string;
  onClose: () => void;
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
    <div class={cx("sidebar-pane", { closing: closing(), open: open() })}>
      <div class="header">
        <Typography hierarchy="body" size="s" weight="bold" inverted={true}>
          {props.title}
        </Typography>
        <KButton onClick={onClose}>
          <Icon icon="Close" color="primary" size="0.75rem" inverted={true} />
        </KButton>
      </div>
      <div class="body">{props.children}</div>
    </div>
  );
};
