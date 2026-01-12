import { createSignal, JSX, Show } from "solid-js";
import styles from "./SidebarPane.module.css";
import { Typography } from "@/src/components/Typography/Typography";
import Icon from "../Icon/Icon";
import { Button as KButton } from "@kobalte/core/button";
import cx from "classnames";

interface SidebarPaneProps {
  title: string;
  onClose: () => void;
  subHeader?: JSX.Element;
  children: JSX.Element;
}

export const SidebarPane = (props: SidebarPaneProps) => {
  const [closing, setClosing] = createSignal(false);

  // FIXME: use animationend event instead of setTimeout
  const onClose = () => {
    setClosing(true);
    setTimeout(() => props.onClose(), 550);
  };

  return (
    <div
      class={cx(styles.sidebarPane, {
        [styles.closing]: closing(),
      })}
    >
      <div class={styles.header}>
        <Typography hierarchy="body" size="s" weight="bold" inverted={true}>
          {props.title}
        </Typography>
        <KButton onClick={onClose}>
          <Icon icon="Close" color="primary" size="0.75rem" inverted={true} />
        </KButton>
      </div>
      <Show when={props.subHeader}>
        <div class={styles.subHeader}>{props.subHeader}</div>
      </Show>
      <div class={styles.body}>{props.children}</div>
    </div>
  );
};
