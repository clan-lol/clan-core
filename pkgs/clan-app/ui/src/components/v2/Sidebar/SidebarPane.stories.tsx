import type { Meta, StoryObj } from "@kachurun/storybook-solid";
import {
  SidebarPane,
  SidebarPaneProps,
} from "@/src/components/v2/Sidebar/SidebarPane";
import { SidebarSection } from "./SidebarSection";
import { Divider } from "@/src/components/v2/Divider/Divider";
import { TextInput } from "@/src/components/v2/Form/TextInput";
import { TextArea } from "@/src/components/v2/Form/TextArea";
import { Checkbox } from "@/src/components/v2/Form/Checkbox";
import { Combobox } from "../Form/Combobox";

const meta: Meta<SidebarPaneProps> = {
  title: "Components/Sidebar/Pane",
  component: SidebarPane,
};

export default meta;

type Story = StoryObj<SidebarPaneProps>;

export const Default: Story = {
  args: {
    title: "Neptune",
    onClose: () => {
      console.log("closing");
    },
    children: (
      <>
        <SidebarSection
          title="General"
          onSave={async () => {
            console.log("saving general");
          }}
        >
          {(editing) => (
            <form class="flex flex-col gap-3">
              <TextInput
                label="First Name"
                size="s"
                inverted={true}
                required={true}
                readOnly={!editing}
                orientation="horizontal"
                input={{ value: "Ron" }}
              />
              <Divider />
              <TextInput
                label="Last Name"
                size="s"
                inverted={true}
                required={true}
                readOnly={!editing}
                orientation="horizontal"
                input={{ value: "Burgundy" }}
              />
              <Divider />
              <TextArea
                label="Bio"
                size="s"
                inverted={true}
                readOnly={!editing}
                orientation="horizontal"
                input={{
                  value:
                    "It's actually an optical illusion, it's the pattern on the pants.",
                  rows: 4,
                }}
              />
              <Divider />
              <Checkbox
                size="s"
                label="Share Profile"
                required={true}
                inverted={true}
                readOnly={!editing}
                checked={true}
                orientation="horizontal"
              />
            </form>
          )}
        </SidebarSection>
        <SidebarSection
          title="Tags"
          onSave={async () => {
            console.log("saving general");
          }}
        >
          {(editing) => (
            <form class="flex flex-col gap-3">
              <Combobox
                size="s"
                inverted={true}
                required={true}
                readOnly={!editing}
                orientation="horizontal"
                multiple={true}
                options={["All", "Home Server", "Backup", "Random"]}
                defaultValue={["All", "Home Server", "Backup", "Random"]}
              />
            </form>
          )}
        </SidebarSection>
        <SidebarSection
          title="Advanced Settings"
          onSave={async () => {
            console.log("saving general");
          }}
        >
          {(editing) => <></>}
        </SidebarSection>
      </>
    ),
  },
};
