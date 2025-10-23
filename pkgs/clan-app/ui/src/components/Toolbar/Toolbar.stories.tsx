import { Meta, StoryObj } from "storybook-solidjs-vite";
import { Toolbar } from "@/src/components/Toolbar/Toolbar";
import { ToolbarButton } from "./ToolbarButton";

const meta: Meta<typeof Toolbar> = {
  title: "Components/Toolbar",
  component: Toolbar,
};

export default meta;

type Story = StoryObj<typeof meta>;

export const Default: Story = {
  // We have to specify children inside a render function to avoid issues with reactivity outside a solid-js context.
  render: (args) => (
    <div class="flex h-[80vh]">
      <div class="mt-auto">
        <Toolbar
          {...args}
          children={
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
          }
        />
      </div>
    </div>
  ),
};
