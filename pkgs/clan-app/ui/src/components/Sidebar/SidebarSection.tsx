import { JSX, Show } from "solid-js";
import styles from "./SidebarSection.module.css";
import { Typography } from "@/src/components/Typography/Typography";

interface SidebarSectionProps {
  title: string;
  controls?: JSX.Element;
  children: JSX.Element;
}

export const SidebarSection = (props: SidebarSectionProps) => {
  return (
    <div class={styles.sidebarSection}>
      <div class={styles.header}>
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
        <Show when={props.controls}>
          <div class={styles.controls}>{props.controls}</div>
        </Show>
      </div>
      <div class={styles.content}>{props.children}</div>
    </div>
  );
};
