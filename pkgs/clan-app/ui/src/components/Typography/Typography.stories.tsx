import type { Meta, StoryObj } from "@kachurun/storybook-solid";

import { Family, Hierarchy, Typography, Weight } from "./Typography";
import { Component, For, Show } from "solid-js";
import { AllColors } from "@/src/components/colors";

interface TypographyExamplesProps {
  weights: Weight[];
  sizes: ("default" | "s" | "xs" | "xxs" | "m" | "l")[];
  hierarchy: Hierarchy;
  colors?: boolean;
  family?: Family;
  inverted?: boolean;
}

const TypographyExamples: Component<TypographyExamplesProps> = (props) => (
  <table
    class="w-full min-w-max table-auto text-left"
    classList={{
      "text-white bg-inv-1": props.inverted,
    }}
  >
    <tbody>
      <For each={props.sizes}>
        {(size) => (
          <tr
            class="border-b fg-semantic-info-1 border-def-3 even:bg-def-2"
            classList={{
              "border-inv-3 even:bg-inv-2": props.inverted,
              "border-def-3 even:bg-def-2": !props.inverted,
            }}
          >
            <For each={props.weights}>
              {/* we set a foreground color to test color=inherit */}
              {(weight) => (
                <td class="px-6 py-2">
                  <Show when={!props.colors}>
                    <Typography
                      hierarchy={props.hierarchy}
                      size={size}
                      weight={weight}
                      family={props.family}
                    >
                      {props.hierarchy} / {size} / {weight}
                    </Typography>
                  </Show>
                  <Show when={props.colors}>
                    <For each={AllColors}>
                      {(color) => (
                        <>
                          <Typography
                            hierarchy={props.hierarchy}
                            size={size}
                            weight={weight}
                            color={color}
                            family={props.family}
                            inverted={props.inverted}
                          >
                            {props.hierarchy} / {size} / {weight} / {color}
                          </Typography>
                          <br />
                        </>
                      )}
                    </For>
                  </Show>
                </td>
              )}
            </For>
          </tr>
        )}
      </For>
    </tbody>
  </table>
);

const meta: Meta<TypographyExamplesProps> = {
  title: "Components/Typography",
  component: TypographyExamples,
};

export default meta;

type Story = StoryObj<TypographyExamplesProps>;

export const BodyCondensed: Story = {
  args: {
    hierarchy: "body",
    sizes: ["default", "s", "xs", "xxs"],
    weights: ["normal", "medium", "bold"],
  },
};

export const Body: Story = {
  args: {
    ...BodyCondensed.args,
    family: "regular",
  },
};

export const LabelCondensed: Story = {
  args: {
    hierarchy: "label",
    sizes: ["default", "s", "xs"],
    weights: ["normal", "medium", "bold"],
  },
};

export const LabelMono: Story = {
  args: {
    ...LabelCondensed.args,
    family: "mono",
  },
};

export const Title: Story = {
  args: {
    hierarchy: "title",
    sizes: ["default", "m", "l"],
    weights: ["normal", "medium", "bold"],
  },
};

export const Headline: Story = {
  args: {
    hierarchy: "headline",
    sizes: ["default", "m", "l"],
    weights: ["normal", "medium", "bold"],
  },
};

export const Teaser: Story = {
  args: {
    hierarchy: "teaser",
    sizes: ["default"],
    weights: ["bold"],
  },
};

export const Colors: Story = {
  args: {
    ...BodyCondensed.args,
    colors: true,
  },
};

export const ColorsInverted: Story = {
  args: {
    ...Colors.args,
    inverted: true,
  },
};
