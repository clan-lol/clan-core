import { Meta, StoryObj } from "storybook-solidjs-vite";
import { Tooltip } from "@/src/components/Tooltip/Tooltip";
import { Typography } from "@/src/components/Typography/Typography";

const meta: Meta<typeof Tooltip> = {
  title: "Components/Tooltip",
  component: Tooltip,
  decorators: [
    (Story) => (
      <div class="p-16">
        <Story />
      </div>
    ),
  ],
  render: (args) => (
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

type Story = StoryObj<typeof meta>;

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
