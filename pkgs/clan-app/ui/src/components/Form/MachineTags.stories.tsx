import type { Meta, StoryObj } from "@kachurun/storybook-solid";
import { MachineTags, MachineTagsProps } from "./MachineTags";
import { createForm, setValue } from "@modular-forms/solid";
import { Button } from "../Button/Button";

const meta = {
  title: "Components/MachineTags",
  component: MachineTags,
} satisfies Meta<MachineTagsProps>;

export default meta;

export type Story = StoryObj<typeof meta>;

export const Default: Story = {
  render: () => {
    const [formStore, { Field, Form }] = createForm<{ tags: string[] }>({
      initialValues: { tags: ["nixos"] },
    });
    const handleSubmit = (values: { tags: string[] }) => {
      console.log("submitting", values);
    };

    const readonly = ["nixos"];
    const options = ["foo"];

    return (
      <Form onSubmit={handleSubmit}>
        <Field name="tags" type="string[]">
          {(field, props) => (
            <MachineTags
              onChange={(newVal) => {
                // Workaround for now, until we manage to use native events
                setValue(formStore, field.name, newVal);
              }}
              name="Tags"
              defaultOptions={options}
              readonlyOptions={readonly}
              readOnly={false}
              defaultValue={field.value}
            />
          )}
        </Field>
        <Button type="submit" hierarchy="primary">
          Submit
        </Button>
      </Form>
    );
  },
};
