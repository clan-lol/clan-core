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
        <ToolbarButton name="select" icon="Cursor" />
        <ToolbarButton name="new-machine" icon="NewMachine" />
        <Divider orientation="vertical" />
        <ToolbarButton name="modules" icon="Modules" selected={true} />
        <ToolbarButton name="ai" icon="AI" />
      </>
    ),
  },
};
