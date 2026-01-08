import { Meta, StoryObj } from "storybook-solidjs-vite";
import Splash from ".";

const meta: Meta = {
  title: "scene/splash",
  component: Splash,
};

export default meta;

type Story = StoryObj;

export const Default: Story = {
  args: {},
};
