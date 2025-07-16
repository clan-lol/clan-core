import type { Meta, StoryContext, StoryObj } from "@kachurun/storybook-solid";
import { Component, For } from "solid-js";
import { Logo, LogoProps, LogoVariant } from "./Logo";
import cx from "classnames";

const variants: LogoVariant[] = ["Clan", "Darknet"];

const LogoExamples: Component<LogoProps> = (props) => (
  <div class="grid grid-cols-6 items-center gap-4">
    <For each={variants}>{(item) => <Logo {...props} variant={item} />}</For>
  </div>
);

const meta: Meta<LogoProps> = {
  title: "Components/Logo",
  component: LogoExamples,
  decorators: [
    (Story: StoryObj, context: StoryContext<LogoProps>) => (
      <div class={cx(context.args.inverted || false ? "bg-inv-acc-3" : "")}>
        <Story />
      </div>
    ),
  ],
};

export default meta;

type Story = StoryObj<LogoProps>;

export const Default: Story = {};

export const Primary: Story = {
  args: {
    color: "primary",
  },
};

export const Secondary: Story = {
  args: {
    color: "secondary",
  },
};

export const Tertiary: Story = {
  args: {
    color: "tertiary",
  },
};

export const Quaternary: Story = {
  args: {
    color: "quaternary",
  },
};

export const PrimaryInverted: Story = {
  args: {
    ...Primary.args,
    inverted: true,
  },
};

export const SecondaryInverted: Story = {
  args: {
    ...Secondary.args,
    inverted: true,
  },
};

export const TertiaryInverted: Story = {
  args: {
    ...Tertiary.args,
    inverted: true,
  },
};

export const QuaternaryInverted: Story = {
  args: {
    ...Quaternary.args,
    inverted: true,
  },
};

export const Inverted: Story = {
  args: {
    inverted: true,
  },
};
