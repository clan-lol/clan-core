import styles from "./TagGroup.module.css";
import cx from "classnames";
import { For, mergeProps } from "solid-js";
import { Tag } from "@/src/components/Tag/Tag";

export interface TagGroupProps {
  labels: string[];
  inverted?: boolean;
}

export const TagGroup = (props: TagGroupProps) => {
  const local = mergeProps({ inverted: false } as const, props);

  return (
    <div class={cx(styles.tagGroup, { inverted: local.inverted })}>
      <For each={props.labels}>
        {(label) => <Tag inverted={local.inverted}>{label}</Tag>}
      </For>
    </div>
  );
};
