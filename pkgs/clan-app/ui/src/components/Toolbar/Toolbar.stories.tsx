import { Meta, StoryObj } from "@kachurun/storybook-solid";
import { Toolbar, ToolbarProps } from "@/src/components/Toolbar/Toolbar";
import { Divider } from "@/src/components/Divider/Divider";
import { ToolbarButton } from "./ToolbarButton";

const meta: Meta<ToolbarProps> = {
  title: "Components/Toolbar",
  component: Toolbar,
};

export default meta;

type Story = StoryObj<ToolbarProps>;

export const Default: Story = {
  args: {
    children: (
      <>
        <ToolbarButton
          name="select"
          icon="Cursor"
          description="Select my thing"
        />
        <ToolbarButton
          name="new-machine"
          icon="NewMachine"
          description="Select this thing"
        />
        <Divider orientation="vertical" />
        <ToolbarButton
          name="modules"
          icon="Modules"
          selected={true}
          description="Add service"
        />
        <ToolbarButton name="ai" icon="AI" description="Call your AI Manager" />
      </>
    ),
  },
};

export const WithTooltip: Story = {
  // @ts-expect-error: args in storybook is not typed correctly. This is a storybook issue.
  render: (args) => (
    <div class="flex h-[80vh]">
      <div class="mt-auto">
        <Toolbar {...args} />
      </div>
    </div>
  ),
  args: {
    children: (
      <>
        <ToolbarButton name="select" icon="Cursor" description="Select" />

        <ToolbarButton
          name="new-machine"
          icon="NewMachine"
          description="Select"
        />

        <ToolbarButton
          name="modules"
          icon="Modules"
          selected={true}
          description="Select"
        />

        <ToolbarButton name="ai" icon="AI" description="Select" />
      </>
    ),
  },
};
