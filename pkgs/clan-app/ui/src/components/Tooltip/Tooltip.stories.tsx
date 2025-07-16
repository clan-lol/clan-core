import { Meta, StoryObj } from "@kachurun/storybook-solid";
import { Tooltip, TooltipProps } from "@/src/components/Tooltip/Tooltip";
import { Typography } from "@/src/components/Typography/Typography";
import { Button } from "@/src/components/Button/Button";

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
};

export default meta;

type Story = StoryObj<TooltipProps>;

export const Default: Story = {
  args: {
    placement: "top",
    inverted: false,
    trigger: <Button hierarchy="primary">Trigger</Button>,
    children: (
      <Typography hierarchy="body" size="xs" inverted={true} weight="medium">
        Your Clan is being created
      </Typography>
    ),
  },
};

export const AnimateBounce: Story = {
  args: {
    ...Default.args,
    animation: "bounce",
  },
};
