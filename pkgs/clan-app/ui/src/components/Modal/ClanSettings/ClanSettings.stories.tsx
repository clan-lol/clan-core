import { fn } from "storybook/test";
import type { Meta, StoryObj } from "storybook-solidjs-vite";
import { ClanSettingsModal } from ".";

const meta: Meta<typeof ClanSettingsModal> = {
  title: "Modals/ClanSettings",
  component: ClanSettingsModal,
};

export default meta;

type Story = StoryObj<typeof meta>;

export const Default: Story = {
  args: {
    onClose: fn(),
    model: {
      uri: "/home/foo/my-clan",
      details: {
        name: "Sol",
        description: null,
        icon: null,
      },
      fieldsSchema: {
        name: {
          readonly: true,
          reason: null,
          readonly_members: [],
        },
        description: {
          readonly: false,
          reason: null,
          readonly_members: [],
        },
        icon: {
          readonly: false,
          reason: null,
          readonly_members: [],
        },
      },
    },
  },
};
