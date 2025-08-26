import "./TagGroup.css";
import cx from "classnames";
import { For } from "solid-js";
import { Tag } from "@/src/components/Tag/Tag";

export interface TagGroupProps {
  class?: string;
  labels: string[];
  inverted?: boolean;
}

export const TagGroup = (props: TagGroupProps) => {
  const inverted = () => props.inverted || false;

  return (
    <div class={cx("tag-group", props.class, { inverted: inverted() })}>
      <For each={props.labels}>
        {(label) => <Tag inverted={inverted()}>{label}</Tag>}
      </For>
    </div>
  );
};
