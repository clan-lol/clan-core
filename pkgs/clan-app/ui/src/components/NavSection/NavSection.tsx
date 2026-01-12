import cx from "classnames";
import styles from "./NavSection.module.css";
import { Button } from "@kobalte/core/button";
import Icon from "../Icon/Icon";
import { Typography } from "../Typography/Typography";
import { Show } from "solid-js";

interface NavSectionProps {
  label: string;
  description?: string;
  onClick: () => void;
}

export const NavSection = (props: NavSectionProps) => {
  return (
    <Button class={cx(styles.navSection)} onClick={props.onClick}>
      <div class={cx(styles.meta)}>
        <Typography hierarchy="label" size="default" weight="bold">
          {props.label}
        </Typography>
        <Show when={props.description}>
          <Typography
            hierarchy="body"
            size="s"
            weight="normal"
            color="secondary"
          >
            {props.description}
          </Typography>
        </Show>
      </div>
      <Icon icon="CaretRight" />
    </Button>
  );
};
