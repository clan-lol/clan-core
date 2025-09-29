import styles from "./Tag.module.css";

import cx from "classnames";
import { Typography } from "@/src/components/Typography/Typography";
import { createSignal, JSX, mergeProps, Show } from "solid-js";

interface IconActionProps {
  inverted: boolean;
  handleActionClick: () => void;
}

export interface TagProps extends JSX.HTMLAttributes<HTMLSpanElement> {
  children?: JSX.Element;
  icon?: (state: IconActionProps) => JSX.Element;
  inverted?: boolean;
  interactive?: boolean;
}

export const Tag = (props: TagProps) => {
  const local = mergeProps({ inverted: false }, props);

  const [isActive, setIsActive] = createSignal(false);

  const handleActionClick = () => {
    setIsActive(true);
    setTimeout(() => setIsActive(false), 150);
  };

  const icon = () =>
    props.icon?.({
      inverted: local.inverted,
      handleActionClick,
    });

  return (
    <span
      class={cx(styles.tag, {
        [styles.inverted]: local.inverted,
        [styles.active]: isActive(),
        [styles.hasAction]: icon(),
        [styles.interactive]: props.interactive,
      })}
    >
      <Typography hierarchy="label" size="xs" inverted={local.inverted}>
        {props.children}
      </Typography>
      <Show when={icon()}>
        <span class={styles.action}>{icon()}</span>
      </Show>
    </span>
  );
};
