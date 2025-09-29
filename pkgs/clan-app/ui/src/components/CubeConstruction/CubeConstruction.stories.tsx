import { CubeConstruction } from "./CubeConstruction";
import { Meta, StoryObj } from "@kachurun/storybook-solid";

const meta: Meta = {
  title: "Components/CubeConstruction",
  component: CubeConstruction,
  globals: {
    // 👇 Override background value for this story
    backgrounds: { value: "dark" },
  },
};

export default meta;

type Story = StoryObj;

export const Default: Story = {
  args: {},
};
