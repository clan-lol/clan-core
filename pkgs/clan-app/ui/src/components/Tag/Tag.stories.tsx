import { Tag, TagProps } from "@/src/components/Tag/Tag";
import { Meta, type StoryContext, StoryObj } from "@kachurun/storybook-solid";
import { expect, fn } from "storybook/test";

const meta: Meta<TagProps> = {
  title: "Components/Tag",
  component: Tag,
};

export default meta;

type Story = StoryObj<TagProps>;

export const Default: Story = {
  args: {
    label: "Label",
  },
};

export const WithAction: Story = {
  args: {
    ...Default.args,
    action: {
      icon: "Close",
      onClick: fn(),
    },
  },
  play: async ({ canvas, step, userEvent, args }: StoryContext) => {
    await userEvent.click(canvas.getByRole("button"));
    await expect(args.action.onClick).toHaveBeenCalled();
  },
};

export const Inverted: Story = {
  args: {
    label: "Label",
    inverted: true,
  },
};

export const InvertedWithAction: Story = {
  args: {
    ...WithAction.args,
    inverted: true,
  },
  play: WithAction.play,
};
