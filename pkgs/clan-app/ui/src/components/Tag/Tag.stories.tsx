import { Tag, TagProps } from "@/src/components/Tag/Tag";
import { Meta, type StoryContext, StoryObj } from "@kachurun/storybook-solid";
import { fn } from "storybook/test";
import Icon from "../Icon/Icon";

const meta: Meta<TagProps> = {
  title: "Components/Tag",
  component: Tag,
};

export default meta;

type Story = StoryObj<TagProps>;

export const Default: Story = {
  args: {
    children: "Label",
  },
};

const IconAction = ({
  inverted,
  handleActionClick,
}: {
  inverted: boolean;
  handleActionClick: () => void;
}) => (
  <Icon
    role="button"
    icon={"Close"}
    size="0.5rem"
    onClick={() => {
      console.log("icon clicked");
      handleActionClick();
      fn();
    }}
    inverted={inverted}
  />
);
export const WithAction: Story = {
  args: {
    ...Default.args,
    icon: IconAction,
    interactive: true,
  },
  play: async ({ canvas, step, userEvent, args }: StoryContext) => {
    await userEvent.click(canvas.getByRole("button"));
    // await expect(args.icon.onClick).toHaveBeenCalled();
  },
};

export const Inverted: Story = {
  args: {
    children: "Label",
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
