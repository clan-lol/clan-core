import styles from "./Toolbar.module.css";
import cx from "classnames";
import { Button } from "@kobalte/core/button";
import Icon, { IconVariant } from "@/src/components/Icon/Icon";
import type { JSX } from "solid-js";
import { Tooltip } from "../Tooltip/Tooltip";

interface ToolbarButtonProps
  extends JSX.ButtonHTMLAttributes<HTMLButtonElement> {
  icon: IconVariant;
  description: JSX.Element;
  selected?: boolean;
}

export const ToolbarButton = (props: ToolbarButtonProps) => {
  return (
    <Tooltip description={props.description} gutter={10} placement="top">
      <Button
        class={cx(styles.toolbar_button, {
          [styles["selected"]]: props.selected,
        })}
        {...props}
      >
        <Icon icon={props.icon} inverted={!props.selected} />
      </Button>
    </Tooltip>
  );
};
