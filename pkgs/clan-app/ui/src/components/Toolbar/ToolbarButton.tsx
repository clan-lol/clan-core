import styles from "./Toolbar.module.css";
import cx from "classnames";
import { Button } from "@kobalte/core/button";
import Icon, { IconVariant } from "@/src/components/Icon/Icon";
import type { JSX } from "solid-js";

export interface ToolbarButtonProps
  extends JSX.ButtonHTMLAttributes<HTMLButtonElement> {
  icon: IconVariant;
  selected?: boolean;
}

export const ToolbarButton = (props: ToolbarButtonProps) => {
  return (
    <Button
      class={cx(styles.toolbar_button, {
        [styles["selected"]]: props.selected,
      })}
      {...props}
    >
      <Icon icon={props.icon} inverted={!props.selected} />
    </Button>
  );
};
