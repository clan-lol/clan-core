import type { Meta, StoryObj } from "@kachurun/storybook-solid";
import { Loader, LoaderProps } from "@/src/components/Loader/Loader";

const LoaderExamples = (props: LoaderProps) => (
  <div class="grid grid-cols-8">
    <Loader {...props} size="default" />
    <Loader {...props} size="l" />
    <Loader {...props} size="xl" />
  </div>
);

const meta: Meta<LoaderProps> = {
  title: "Components/Loader",
  component: LoaderExamples,
};

export default meta;

type Story = StoryObj<LoaderProps>;

export const Primary: Story = {
  args: {
    hierarchy: "primary",
  },
};

export const Secondary: Story = {
  args: {
    hierarchy: "secondary",
  },
};
