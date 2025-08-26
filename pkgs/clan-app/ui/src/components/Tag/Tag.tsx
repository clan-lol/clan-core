import "./Tag.css";

import cx from "classnames";
import { Typography } from "@/src/components/Typography/Typography";
import { createSignal, JSX } from "solid-js";

interface IconActionProps {
  inverted: boolean;
  handleActionClick: () => void;
}

export interface TagProps extends JSX.HTMLAttributes<HTMLSpanElement> {
  children?: JSX.Element;
  icon?: (state: IconActionProps) => JSX.Element;
  inverted?: boolean;
  interactive?: boolean;
  class?: string;
}

export const Tag = (props: TagProps) => {
  const inverted = () => props.inverted || false;

  const [isActive, setIsActive] = createSignal(false);

  const handleActionClick = () => {
    setIsActive(true);
    setTimeout(() => setIsActive(false), 150);
  };

  return (
    <span
      class={cx("tag", {
        inverted: inverted(),
        active: isActive(),
        "has-icon": props.icon,
        "is-interactive": props.interactive,
        class: props.class,
      })}
    >
      <Typography hierarchy="label" size="xs" inverted={inverted()}>
        {props.children}
      </Typography>
      {props.icon?.({
        inverted: inverted(),
        handleActionClick,
      })}
    </span>
  );
};
