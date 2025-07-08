import { JSX } from "solid-js";
import "./SidebarPane.css";
import { Typography } from "@/src/components/v2/Typography/Typography";
import Icon from "../Icon/Icon";
import { Button as KButton } from "@kobalte/core/button";

export interface SidebarPaneProps {
  title: string;
  onClose: () => void;
  children: JSX.Element;
}

export const SidebarPane = (props: SidebarPaneProps) => {
  return (
    <div class="sidebar-pane">
      <div class="header">
        <Typography hierarchy="body" size="s" weight="bold" inverted={true}>
          {props.title}
        </Typography>
        <KButton onClick={props.onClose}>
          <Icon icon="Close" color="primary" size="0.75rem" inverted={true} />
        </KButton>
      </div>
      <div class="body">{props.children}</div>
    </div>
  );
};
