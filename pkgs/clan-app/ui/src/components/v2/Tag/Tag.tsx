import "./Tag.css";

import cx from "classnames";
import { Typography } from "@/src/components/v2/Typography/Typography";
import { createSignal, Show } from "solid-js";
import Icon, { IconVariant } from "../Icon/Icon";

export interface TagAction {
  icon: IconVariant;
  onClick: () => void;
}

export interface TagProps {
  label: string;
  action?: TagAction;
  inverted?: boolean;
}

export const Tag = (props: TagProps) => {
  const inverted = () => props.inverted || false;

  const [isActive, setIsActive] = createSignal(false);

  const handleActionClick = () => {
    setIsActive(true);
    props.action?.onClick();
    setTimeout(() => setIsActive(false), 150);
  };

  return (
    <span
      class={cx("tag", {
        inverted: inverted(),
        active: isActive(),
        "has-action": props.action,
      })}
      aria-label={props.label}
      aria-readonly={!props.action}
    >
      <Typography hierarchy="label" size="xs" inverted={inverted()}>
        {props.label}
      </Typography>
      <Show when={props.action}>
        <Icon
          role="button"
          icon={props.action!.icon}
          size="0.5rem"
          inverted={inverted()}
          onClick={handleActionClick}
        />
      </Show>
    </span>
  );
};
