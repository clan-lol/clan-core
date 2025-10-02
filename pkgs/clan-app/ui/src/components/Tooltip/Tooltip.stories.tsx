import { Meta, StoryObj } from "@kachurun/storybook-solid";
import { Tooltip, TooltipProps } from "@/src/components/Tooltip/Tooltip";
import { Typography } from "@/src/components/Typography/Typography";

const meta: Meta<TooltipProps> = {
  title: "Components/Tooltip",
  component: Tooltip,
  decorators: [
    (Story: StoryObj<TooltipProps>) => (
      <div class="p-16">
        <Story />
      </div>
    ),
  ],
  render: (args: TooltipProps) => (
    <div class="p-16">
      <Tooltip
        {...args}
        children={
          <Typography
            hierarchy="body"
            size="xs"
            inverted={true}
            weight="medium"
          >
            Your Clan is being created
          </Typography>
        }
      />
    </div>
  ),
};

export default meta;

type Story = StoryObj<TooltipProps>;

export const Default: Story = {
  args: {
    placement: "top",
    inverted: false,
  },
};

export const AnimateBounce: Story = {
  args: {
    ...Default.args,
    animation: "bounce",
  },
};
