import { JSX } from "solid-js";
import "./SidebarSection.css";
import { Typography } from "@/src/components/Typography/Typography";
import cx from "classnames";

export interface SidebarSectionProps {
  title: string;
  class?: string;
  children: JSX.Element;
}

export const SidebarSection = (props: SidebarSectionProps) => {
  return (
    <div class={cx("sidebar-section", props.class)}>
      <div class="header">
        <Typography
          hierarchy="label"
          size="xs"
          family="mono"
          transform="uppercase"
          color="tertiary"
          inverted={true}
        >
          {props.title}
        </Typography>
      </div>
      <div class="content">{props.children}</div>
    </div>
  );
};
