import { Meta, StoryObj } from "@kachurun/storybook-solid";
import { Toolbar, ToolbarProps } from "@/src/components/Toolbar/Toolbar";
import { Divider } from "@/src/components/Divider/Divider";
import { ToolbarButton } from "./ToolbarButton";
import { Tooltip } from "../Tooltip/Tooltip";
import { Typography } from "../Typography/Typography";

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
        <ToolbarButton name="select" icon="Cursor" />
        <ToolbarButton name="new-machine" icon="NewMachine" />
        <Divider orientation="vertical" />
        <ToolbarButton name="modules" icon="Modules" selected={true} />
        <ToolbarButton name="ai" icon="AI" />
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
        <Tooltip
          trigger={<ToolbarButton name="select" icon="Cursor" />}
          placement="top"
        >
          <div class="mb-1 p-1 text-fg-inv-1">
            <Typography hierarchy="label" size="s" color="inherit">
              Select an object
            </Typography>
          </div>
        </Tooltip>
        <Divider orientation="vertical" />
        <Tooltip
          trigger={<ToolbarButton name="new-machine" icon="NewMachine" />}
          placement="top"
        >
          <div class="mb-1 p-1 text-fg-inv-1">
            <Typography hierarchy="label" size="s" color="inherit">
              Create a new machine
            </Typography>
          </div>
        </Tooltip>
        <Tooltip
          trigger={
            <ToolbarButton name="modules" icon="Modules" selected={true} />
          }
          placement="top"
        >
          <div class="mb-1 p-1 text-fg-inv-1">
            <Typography hierarchy="label" size="s" color="inherit">
              Manage Services
            </Typography>
          </div>
        </Tooltip>
        <Tooltip
          trigger={<ToolbarButton name="ai" icon="AI" />}
          placement="top"
        >
          <div class="mb-1 p-1 text-fg-inv-1">
            <Typography hierarchy="label" size="s" color="inherit">
              Chat with AI
            </Typography>
          </div>
        </Tooltip>
      </>
    ),
  },
};
