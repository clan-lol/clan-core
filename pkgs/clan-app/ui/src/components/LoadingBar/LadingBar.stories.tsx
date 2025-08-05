import type { Meta, StoryContext, StoryObj } from "@kachurun/storybook-solid";
import { LoadingBar } from "./LoadingBar";

const meta: Meta = {
  title: "Components/LoadingBar",
  component: LoadingBar,
  decorators: [
    (Story: StoryObj, context: StoryContext<unknown>) => {
      return (
        <div class={"flex w-fit items-center justify-center bg-slate-500 p-10"}>
          <Story />
        </div>
      );
    },
  ],
};

export default meta;

type Story = StoryObj;

export const Default: Story = {};
