import type { Meta, StoryObj } from "@kachurun/storybook-solid";
import { Component, For } from "solid-js";
import Icon, { IconProps, IconVariant } from "./Icon";

const iconVariants: IconVariant[] = [
  "ClanIcon",
  "Checkmark",
  "Paperclip",
  "Expand",
  "Plus",
  "Trash",
  "Folder",
  "CaretRight",
  "CaretLeft",
  "CaretUp",
  "CaretDown",
  "Close",
  "Flash",
  "EyeClose",
  "EyeOpen",
  "Settings",
  "Grid",
  "List",
  "Edit",
  "Load",
  "ArrowRight",
  "ArrowLeft",
  "ArrowTop",
  "ArrowBottom",
  "Info",
  "Update",
  "Reload",
  "Search",
  "Report",
  "Cursor",
  "More",
  "Filter",
  "Download",
  "Attention",
  "User",
  "WarningFilled",
  "Modules",
  "NewMachine",
  "AI",
  "Heart",
  "SearchFilled",
  "Offline",
  "Switch",
  "Tag",
  "Machine",
];

const IconExamples: Component<IconProps> = (props) => (
  <div class="inline-flex flex-wrap gap-2">
    <For each={iconVariants}>{(item) => <Icon {...props} icon={item} />}</For>
  </div>
);

const meta: Meta<IconProps> = {
  title: "Components/Icon",
  component: IconExamples,
};

export default meta;

type Story = StoryObj<IconProps>;

export const Default: Story = {};

export const Large: Story = {
  args: {
    width: "2rem",
    height: "2rem",
  },
};
