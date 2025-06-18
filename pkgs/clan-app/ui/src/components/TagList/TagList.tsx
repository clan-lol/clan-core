import { Component, For } from "solid-js";
import { Typography } from "@/src/components/Typography";
import "./TagList.css";

interface TagListProps {
  values: string[];
}

export const TagList: Component<TagListProps> = (props) => {
  return (
    <div class="tag-list">
      <For each={props.values}>
        {(tag) => (
          <Typography hierarchy="label" size="s" inverted={true} class="tag">
            {tag}
          </Typography>
        )}
      </For>
    </div>
  );
};
