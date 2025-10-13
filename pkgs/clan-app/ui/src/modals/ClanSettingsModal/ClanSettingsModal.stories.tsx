import { fn } from "storybook/test";
import type { Meta, StoryObj } from "@kachurun/storybook-solid";
import { ClanSettingsModal, ClanSettingsModalProps } from "./ClanSettingsModal";

const meta: Meta<ClanSettingsModalProps> = {
  title: "Modals/ClanSettings",
  component: ClanSettingsModal,
};

export default meta;

type Story = StoryObj<ClanSettingsModalProps>;

const props: ClanSettingsModalProps = {
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
};

export const Default: Story = {
  args: props,
};
