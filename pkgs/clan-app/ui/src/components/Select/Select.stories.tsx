import { TagProps } from "@/src/components/Tag/Tag";
import { Meta, StoryContext, StoryObj } from "@kachurun/storybook-solid";

import { Select, SelectProps } from "./Select";
import { Fieldset } from "../Form/Fieldset";

// const meta: Meta<SelectProps> = {
//   title: "Components/Select",
//   component: Select,
// };
const meta = {
  title: "Components/Form/Select",
  component: Select,
  decorators: [
    (Story: StoryObj, context: StoryContext<SelectProps>) => {
      return (
        <div class={`w-[600px]`}>
          <Fieldset>
            <Story />
          </Fieldset>
        </div>
      );
    },
  ],
} satisfies Meta<SelectProps>;

export default meta;

type Story = StoryObj<TagProps>;

export const Default: Story = {
  args: {
    required: true,
    label: {
      label: "Select your pet",
      description: "Choose your favorite pet from the list",
    },
    options: [
      { value: "dog", label: "Doggy" },
      { value: "cat", label: "Catty" },
      { value: "fish", label: "Fishy" },
      { value: "bird", label: "Birdy" },
      { value: "hamster", label: "Hammy" },
      { value: "snake", label: "Snakey" },
      { value: "turtle", label: "Turtly" },
    ],
    placeholder: "Select your pet",
  },
};

// <Field name="language">
//     {(field, input) => (
//         <Select
//         required
//         label={{
//             label: "Language",
//             description: "Select your preferred language",
//         }}
//         options={[
//             { value: "en", label: "English" },
//             { value: "fr", label: "Français" },
//         ]}
//         placeholder="Language"
//         onChange={(opt) => {
//             setValue(formStore, "language", opt?.value || "");
//         }}
//         name={field.name}
//         validationState={field.error ? "invalid" : "valid"}
//         />
//     )}
// </Field>
