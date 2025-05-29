import type { Meta, StoryObj } from "@kachurun/storybook-solid";
import { Title as BlockTitle, Subtitle, Description, Primary, Stories } from '@storybook/blocks';

import {
  AllowedSizes,
  Hierarchy,
  Typography,
  TypographyProps,
  Weight,
} from "./Typography";
import { Component, For } from "solid-js";

interface TypographyExamplesProps<H extends Hierarchy> {
  weights: Weight[]
  sizes: AllowedSizes<H>
  hierarchy: Hierarchy;
}

const TypographyExamples: Component<TypographyExamplesProps> = (props) => (
  <table class="w-full text-left table-auto min-w-max">
    <tbody>
      <For each={props.sizes}>
        {(size) => (
          <tr>
            <For each={props.weights}>
              {(weight) => (
                <td class="p-2 border-b">
                  <Typography
                    hierarchy={props.hierarchy}
                    size={size}
                    weight={weight}
                  >
                    {props.hierarchy} / {size} / {weight}
                  </Typography>
                </td>
              )}
            </For>
          </tr>
        )}
      </For>
    </tbody>
  </table>
);

const meta: Meta<TypographyExamplesProps<never>> = {
  title: "Components/Typography",
  component: TypographyExamples,
  parameters: {
    docs: {
      // custom page template to remove controls and primary story example
      // gives a much nicer overview
      page: () => (
        <>
          <BlockTitle />
          <Subtitle />
          <Description />
          <Stories />
        </>
      ),

    }
  },
  decorators: [
    (Story) => (
      <div className="bg-white">
        <Story />
      </div>
    ),
  ],
};

export default meta;

type Story = StoryObj<TypographyProps>;

export const Body: Story = {
  args: {
    hierarchy: "body",
    sizes: ["default", "s", "xs", "xxs"],
    weights: ["normal", "medium", "bold"]
  },
};

export const Label: Story = {
  args: {
    hierarchy: "label",
    sizes: ["default", "s", "xs"],
    weights: ["normal", "medium", "bold"]
  },
};

export const Title: Story = {
  args: {
    hierarchy: "title",
    sizes: ["default", "s", "xs"],
    weights: ["normal", "medium", "bold"]
  },
}

export const Headline: Story = {
  args: {
    hierarchy: "headline",
    sizes: ["default", "s", "xs"],
    weights: ["normal", "medium", "bold"]
  },
}