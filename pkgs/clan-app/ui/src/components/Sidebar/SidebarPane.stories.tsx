import type { Meta, StoryObj } from "@kachurun/storybook-solid";
import {
  SidebarPane,
  SidebarPaneProps,
} from "@/src/components/Sidebar/SidebarPane";
import { SidebarSection } from "./SidebarSection";
import { Divider } from "@/src/components/Divider/Divider";
import { TextInput } from "@/src/components/Form/TextInput";
import { TextArea } from "@/src/components/Form/TextArea";
import { Checkbox } from "@/src/components/Form/Checkbox";
import { SidebarSectionForm } from "@/src/components/Sidebar/SidebarSectionForm";
import * as v from "valibot";
import { splitProps } from "solid-js";
import { Typography } from "@/src/components/Typography/Typography";
import { MachineTags } from "@/src/components/Form/MachineTags";
import { setValue } from "@modular-forms/solid";
import { StoryContext } from "@kachurun/storybook-solid-vite";

type Story = StoryObj<SidebarPaneProps>;

const profiles = {
  ron: {
    firstName: "Ron",
    lastName: "Burgundy",
    bio: "It's actually an optical illusion, it's the pattern on the pants.",
    shareProfile: true,
    tags: ["all", "home Server", "backup", "random"],
  },
};

const meta: Meta<SidebarPaneProps> = {
  title: "Components/SidebarPane",
  component: SidebarPane,
  decorators: [
    (
        Story: StoryObj<SidebarPaneProps>,
        context: StoryContext<SidebarPaneProps>,
      ) =>
      () => <Story {...context.args} />,
  ],
};

export default meta;

export const Default: Story = {
  args: {
    title: "Neptune",
    onClose: () => {
      console.log("closing");
    },
  },
  // We have to provide children within a custom render function to ensure we aren't creating any reactivity outside the
  // solid-js scope.
  render: (args: SidebarPaneProps) => (
    <SidebarPane
      {...args}
      children={
        <>
          <SidebarSectionForm
            title="General"
            schema={v.object({
              firstName: v.pipe(
                v.string(),
                v.nonEmpty("Please enter a first name."),
              ),
              lastName: v.pipe(
                v.string(),
                v.nonEmpty("Please enter a last name."),
              ),
              bio: v.string(),
              shareProfile: v.optional(v.boolean()),
            })}
            initialValues={profiles.ron}
            onSubmit={async () => {
              console.log("saving general");
            }}
          >
            {({ editing, Field }) => (
              <div class="flex flex-col gap-3">
                <Field name="firstName">
                  {(field, input) => (
                    <TextInput
                      {...field}
                      size="s"
                      inverted
                      label="First Name"
                      value={field.value}
                      required
                      readOnly={!editing}
                      orientation="horizontal"
                      input={input}
                    />
                  )}
                </Field>
                <Divider />
                <Field name="lastName">
                  {(field, input) => (
                    <TextInput
                      {...field}
                      size="s"
                      inverted
                      label="Last Name"
                      value={field.value}
                      required
                      readOnly={!editing}
                      orientation="horizontal"
                      input={input}
                    />
                  )}
                </Field>
                <Divider />
                <Field name="bio">
                  {(field, input) => (
                    <TextArea
                      {...field}
                      value={field.value}
                      size="s"
                      label="Bio"
                      inverted
                      readOnly={!editing}
                      orientation="horizontal"
                      input={{ ...input, rows: 4 }}
                    />
                  )}
                </Field>
                <Field name="shareProfile" type="boolean">
                  {(field, input) => {
                    return (
                      <Checkbox
                        {...splitProps(field, ["value"])[1]}
                        defaultChecked={field.value}
                        size="s"
                        label="Share"
                        inverted
                        readOnly={!editing}
                        orientation="horizontal"
                        input={input}
                      />
                    );
                  }}
                </Field>
              </div>
            )}
          </SidebarSectionForm>
          <SidebarSectionForm
            title="Tags"
            schema={v.object({
              tags: v.pipe(v.array(v.string()), v.nonEmpty()),
            })}
            initialValues={profiles.ron}
            onSubmit={async (values) => {
              console.log("saving tags", values);
            }}
          >
            {({ editing, Field, formStore }) => (
              <Field name="tags" type="string[]">
                {(field, props) => (
                  <MachineTags
                    {...splitProps(field, ["value"])[1]}
                    size="s"
                    onChange={(newVal) => {
                      // Workaround for now, until we manage to use native events
                      setValue(formStore, field.name, newVal);
                    }}
                    inverted
                    required
                    readOnly={!editing}
                    orientation="horizontal"
                    defaultValue={field.value}
                  />
                )}
              </Field>
            )}
          </SidebarSectionForm>
          <SidebarSection title="Simple">
            <Typography tag="h2" hierarchy="title" size="m" inverted>
              Static Content
            </Typography>
            <Typography hierarchy="label" size="s" inverted>
              This is a non-form section with static content
            </Typography>
          </SidebarSection>
        </>
      }
    />
  ),
};
