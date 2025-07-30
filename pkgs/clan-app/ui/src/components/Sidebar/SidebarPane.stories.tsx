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

type Story = StoryObj<SidebarPaneProps>;

const schema = v.object({
  firstName: v.pipe(v.string(), v.nonEmpty("Please enter a first name.")),
  lastName: v.pipe(v.string(), v.nonEmpty("Please enter a last name.")),
  bio: v.string(),
  shareProfile: v.optional(v.boolean()),
  tags: v.pipe(v.optional(v.array(v.string()))),
});

const clanURI = "/home/brian/clans/my-clan";

const profiles = {
  ron: {
    firstName: "Ron",
    lastName: "Burgundy",
    bio: "It's actually an optical illusion, it's the pattern on the pants.",
    shareProfile: true,
    tags: ["All", "Home Server", "Backup", "Random"],
  },
};

const meta: Meta<SidebarPaneProps> = {
  title: "Components/SidebarPane",
  component: SidebarPane,
};

export default meta;

export const Default: Story = {
  args: {
    title: "Neptune",
    onClose: () => {
      console.log("closing");
    },
    children: (
      <>
        <SidebarSectionForm
          title="General"
          schema={schema}
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
        {/* todo fix tags component */}
        {/*<SidebarSectionForm*/}
        {/*  title="Tags"*/}
        {/*  schema={schema}*/}
        {/*  initialValues={profiles.ron}*/}
        {/*  onSubmit={async () => {*/}
        {/*    console.log("saving general");*/}
        {/*  }}*/}
        {/*>*/}
        {/*  {({ editing, Field }) => (*/}
        {/*    <Field name="tags">*/}
        {/*      {(field, input) => (*/}
        {/*        <Combobox*/}
        {/*          {...field}*/}
        {/*          value={field.value}*/}
        {/*          options={field.value || []}*/}
        {/*          size="s"*/}
        {/*          inverted*/}
        {/*          required*/}
        {/*          readOnly={!editing}*/}
        {/*          orientation="horizontal"*/}
        {/*          multiple*/}
        {/*        />*/}
        {/*      )}*/}
        {/*    </Field>*/}
        {/*  )}*/}
        {/*</SidebarSectionForm>*/}
        <SidebarSection title="Simple" class="flex flex-col">
          <Typography tag="h2" hierarchy="title" size="m" inverted>
            Static Content
          </Typography>
          <Typography hierarchy="label" size="s" inverted>
            This is a non-form section with static content
          </Typography>
        </SidebarSection>
      </>
    ),
  },
};
