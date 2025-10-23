import { Meta, StoryObj } from "@kachurun/storybook-solid";
import { Toolbar, ToolbarProps } from "@/src/components/Toolbar/Toolbar";
import { ToolbarButton } from "./ToolbarButton";

const meta: Meta<ToolbarProps> = {
  title: "Components/Toolbar",
  component: Toolbar,
};

export default meta;

type Story = StoryObj<ToolbarProps>;

export const Default: Story = {
  // We have to specify children inside a render function to avoid issues with reactivity outside a solid-js context.
  // @ts-expect-error: args in storybook is not typed correctly. This is a storybook issue.
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
