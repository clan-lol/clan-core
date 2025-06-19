import type { Meta, StoryObj, StoryContext } from "@kachurun/storybook-solid";
import { Component, For } from "solid-js";
import Icon, { IconProps, IconVariant } from "./Icon";
import cx from "classnames";

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
  decorators: [
    (Story: StoryObj, context: StoryContext<IconProps>) => (
      <div class={cx(context.args.inverted || false ? "bg-inv-acc-3" : "")}>
        <Story />
      </div>
    ),
  ],
};

export default meta;

type Story = StoryObj<IconProps>;

export const Default: Story = {};

export const Primary: Story = {
  args: {
    color: "primary",
  },
};

export const Secondary: Story = {
  args: {
    color: "secondary",
  },
};

export const Tertiary: Story = {
  args: {
    color: "tertiary",
  },
};

export const Quaternary: Story = {
  args: {
    color: "quaternary",
  },
};

export const PrimaryInverted: Story = {
  args: {
    ...Primary.args,
    inverted: true,
  },
};

export const SecondaryInverted: Story = {
  args: {
    ...Secondary.args,
    inverted: true,
  },
};

export const TertiaryInverted: Story = {
  args: {
    ...Tertiary.args,
    inverted: true,
  },
};

export const QuaternaryInverted: Story = {
  args: {
    ...Quaternary.args,
    inverted: true,
  },
};

export const Inverted: Story = {
  args: {
    inverted: true,
  },
};

export const Large: Story = {
  args: {
    width: "2rem",
    height: "2rem",
  },
};
