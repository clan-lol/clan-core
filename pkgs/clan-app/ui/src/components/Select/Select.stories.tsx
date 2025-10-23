import { Meta, StoryObj } from "storybook-solidjs-vite";

import { Select } from "./Select";
import { Fieldset } from "../Form/Fieldset";

const meta: Meta<typeof Select> = {
  title: "Components/Form/Select",
  component: Select,
  decorators: [
    (Story) => {
      return (
        <div class={`w-[600px]`}>
          <Fieldset>
            <Story />
          </Fieldset>
        </div>
      );
    },
  ],
};

export default meta;

type Story = StoryObj<typeof meta>;

export const Default: Story = {
  args: {
    required: true,
    label: {
      label: "Select your pet",
      description: "Choose your favorite pet from the list",
    },
    options: [
      {
        value: "dog",
        label: "DoggyDoggyDoggyDoggyDoggyDoggy DoggyDoggyDoggyDoggyDoggy",
      },
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
