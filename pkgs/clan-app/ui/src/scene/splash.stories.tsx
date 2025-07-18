import { Meta, StoryObj } from "@kachurun/storybook-solid";
import { Splash } from "./splash";

const meta: Meta = {
  title: "scene/splash",
  component: Splash,
};

export default meta;

type Story = StoryObj;

export const Default: Story = {
  args: {},
};
