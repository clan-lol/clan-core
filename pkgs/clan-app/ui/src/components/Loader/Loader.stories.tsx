import type { Meta, StoryObj } from "storybook-solidjs-vite";
import { Loader, LoaderProps } from "@/src/components/Loader/Loader";

const LoaderExamples = (props: LoaderProps) => (
  <div class="grid grid-cols-8">
    <Loader {...props} size="default" />
    <Loader {...props} size="l" />
    <Loader {...props} size="xl" />
  </div>
);

const meta: Meta<typeof LoaderExamples> = {
  title: "Components/Loader",
  component: LoaderExamples,
};

export default meta;

type Story = StoryObj<typeof meta>;

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
