import type { Meta, StoryObj } from "storybook-solidjs-vite";
import { NavSection } from "@/src/components/NavSection/NavSection";

const meta: Meta<typeof NavSection> = {
  title: "Components/NavSection",
  component: NavSection,
  decorators: [
    (Story) => (
      <div class="w-96">
        <Story />
      </div>
    ),
  ],
};

export default meta;

type Story = StoryObj<typeof NavSection>;

export const Default: Story = {
  args: {
    label: "My Clan",
  },
};

export const WithDescription: Story = {
  args: {
    ...Default.args,
    description:
      "This is my Clan. There are many Clans like it, but this one is mine",
  },
};
