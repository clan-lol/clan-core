import { Meta, StoryObj } from "@kachurun/storybook-solid";
import { CubeScene } from "./cubes";

const meta: Meta = {
  title: "scene/cubes",
  component: CubeScene,
};

export default meta;

type Story = StoryObj;

export const Default: Story = {
  args: {},
};
