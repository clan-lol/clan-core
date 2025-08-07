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
export const Async: Story = {
  args: {
    required: true,
    label: {
      label: "Select your pet",
      description: "Choose your favorite pet from the list",
    },
    getOptions: async () => {
      return new Promise((resolve) => {
        setTimeout(() => {
          resolve([
            { value: "dog", label: "Doggy" },
            { value: "cat", label: "Catty" },
            { value: "fish", label: "Fishy" },
            { value: "bird", label: "Birdy" },
            { value: "hamster", label: "Hammy" },
            { value: "snake", label: "Snakey" },
            { value: "turtle", label: "Turtly" },
          ]);
        }, 3000);
      });
    },
    placeholder: "Select your pet",
  },
};
