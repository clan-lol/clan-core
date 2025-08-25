import { fn } from "storybook/test";
import type { Meta, StoryObj } from "@kachurun/storybook-solid";
import { ClanSettingsModal, ClanSettingsModalProps } from "./ClanSettingsModal";

const meta: Meta<ClanSettingsModalProps> = {
  title: "Modals/ClanSettings",
  component: ClanSettingsModal,
};

export default meta;

type Story = StoryObj<ClanSettingsModalProps>;

export const Default: Story = {
  args: {
    onClose: fn(),
    model: {
      uri: "/home/foo/my-clan",
      name: "Sol",
      description: null,
      icon: null,
      fieldsSchema: {
        name: {
          readonly: true,
          reason: null,
        },
        description: {
          readonly: false,
          reason: null,
        },
        icon: {
          readonly: false,
          reason: null,
        },
      },
    },
  },
};
