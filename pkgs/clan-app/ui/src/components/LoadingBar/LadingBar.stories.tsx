import type { Meta, StoryObj } from "storybook-solidjs-vite";
import { LoadingBar } from "./LoadingBar";

const meta: Meta<typeof LoadingBar> = {
  title: "Components/LoadingBar",
  component: LoadingBar,
  decorators: [
    (Story) => {
      return (
        <div class={"flex w-fit items-center justify-center bg-slate-500 p-10"}>
          <Story />
        </div>
      );
    },
  ],
};

export default meta;

type Story = StoryObj<typeof meta>;

export const Default: Story = {};
