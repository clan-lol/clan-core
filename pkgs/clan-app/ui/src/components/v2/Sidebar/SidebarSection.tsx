import { createSignal, JSX } from "solid-js";
import "./SidebarSection.css";
import { Typography } from "@/src/components/v2/Typography/Typography";
import { Button as KButton } from "@kobalte/core/button";
import Icon from "../Icon/Icon";

export interface SidebarSectionProps {
  title: string;
  onSave: () => Promise<void>;
  children: (editing: boolean) => JSX.Element;
}

export const SidebarSection = (props: SidebarSectionProps) => {
  const [editing, setEditing] = createSignal(false);

  const save = async () => {
    // todo how do we surface errors?
    await props.onSave();
    setEditing(false);
  };

  return (
    <div class="sidebar-section">
      <div class="header">
        <Typography
          hierarchy="label"
          size="xs"
          family="mono"
          weight="light"
          transform="uppercase"
          color="tertiary"
          inverted={true}
        >
          {props.title}
        </Typography>
        <div class="controls">
          {editing() && (
            <KButton>
              <Icon
                icon="Checkmark"
                color="tertiary"
                size="0.75rem"
                inverted={true}
                onClick={save}
              />
            </KButton>
          )}
          <KButton onClick={() => setEditing(!editing())}>
            <Icon
              icon={editing() ? "Close" : "Edit"}
              color="tertiary"
              size="0.75rem"
              inverted={true}
            />
          </KButton>
        </div>
      </div>
      <div class="content">{props.children(editing())}</div>
    </div>
  );
};
