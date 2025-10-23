import { CubeConstruction } from "./CubeConstruction";
import { Meta, StoryObj } from "storybook-solidjs-vite";

const meta: Meta<typeof CubeConstruction> = {
  title: "Components/CubeConstruction",
  component: CubeConstruction,
  globals: {
    // 👇 Override background value for this story
    backgrounds: { value: "dark" },
  },
};

export default meta;

type Story = StoryObj<typeof meta>;

export const Default: Story = {
  args: {},
};
