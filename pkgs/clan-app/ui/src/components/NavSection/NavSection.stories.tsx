import type { Meta, StoryObj } from "@kachurun/storybook-solid";
import {
  NavSection,
  NavSectionProps,
} from "@/src/components/NavSection/NavSection";

const meta: Meta<NavSectionProps> = {
  title: "Components/NavSection",
  component: NavSection,
  decorators: [
    (Story: StoryObj) => (
      <div class="w-96">
        <Story />
      </div>
    ),
  ],
};

export default meta;

type Story = StoryObj<NavSectionProps>;

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
