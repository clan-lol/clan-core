import type { Meta, StoryObj } from "storybook-solidjs-vite";
import { Button, ButtonProps } from "./Button";
import { Component } from "solid-js";
import { expect, fn, within } from "storybook/test";

const getCursorStyle = (el: Element) => window.getComputedStyle(el).cursor;

const ButtonExamples: Component<ButtonProps> = (props) => (
  <>
    <div class="grid w-fit grid-cols-6 gap-8">
      <div>
        <Button data-testid="default" {...props}>
          Label
        </Button>
      </div>
      <div>
        <Button data-testid="small" size="s" {...props}>
          Label
        </Button>
      </div>
      <div>
        <Button data-testid="xsmall" size="xs" {...props}>
          Label
        </Button>
      </div>
      <div>
        <Button data-testid="default-disabled" {...props} disabled={true}>
          Disabled
        </Button>
      </div>
      <div>
        <Button
          data-testid="small-disabled"
          {...props}
          disabled={true}
          size="s"
        >
          Disabled
        </Button>
      </div>

      <div>
        <Button
          data-testid="xsmall-disabled"
          {...props}
          disabled={true}
          size="xs"
        >
          Disabled
        </Button>
      </div>

      <div>
        <Button data-testid="default-start-icon" {...props} icon="Flash">
          Label
        </Button>
      </div>
      <div>
        <Button data-testid="small-start-icon" {...props} icon="Flash" size="s">
          Label
        </Button>
      </div>
      <div>
        <Button
          data-testid="xsmall-start-icon"
          {...props}
          icon="Flash"
          size="xs"
        >
          Label
        </Button>
      </div>
      <div>
        <Button
          data-testid="default-disabled-start-icon"
          {...props}
          icon="Flash"
          disabled={true}
        >
          Disabled
        </Button>
      </div>
      <div>
        <Button
          data-testid="small-disabled-start-icon"
          {...props}
          icon="Flash"
          size="s"
          disabled={true}
        >
          Disabled
        </Button>
      </div>

      <div>
        <Button
          data-testid="xsmall-disabled-start-icon"
          {...props}
          icon="Flash"
          size="xs"
          disabled={true}
        >
          Disabled
        </Button>
      </div>

      <div>
        <Button data-testid="default-end-icon" {...props} endIcon="Flash">
          Label
        </Button>
      </div>
      <div>
        <Button
          data-testid="small-end-icon"
          {...props}
          endIcon="Flash"
          size="s"
        >
          Label
        </Button>
      </div>
      <div>
        <Button
          data-testid="xsmall-end-icon"
          {...props}
          endIcon="Flash"
          size="xs"
        >
          Label
        </Button>
      </div>
      <div>
        <Button
          data-testid="default-disabled-end-icon"
          {...props}
          endIcon="Flash"
          disabled={true}
        >
          Disabled
        </Button>
      </div>
      <div>
        <Button
          data-testid="small-disabled-end-icon"
          {...props}
          endIcon="Flash"
          size="s"
          disabled={true}
        >
          Disabled
        </Button>
      </div>
      <div>
        <Button
          data-testid="xsmall-disabled-end-icon"
          {...props}
          endIcon="Flash"
          size="xs"
          disabled={true}
        >
          Disabled
        </Button>
      </div>

      <div>
        <Button data-testid="default-icon" {...props} icon="Flash" />
      </div>
      <div>
        <Button data-testid="small-icon" {...props} icon="Flash" size="s" />
      </div>
      <div>
        <Button data-testid="xsmall-icon" {...props} icon="Flash" size="xs" />
      </div>
      <div>
        <Button
          data-testid="default-disabled-icon"
          {...props}
          icon="Flash"
          disabled={true}
        />
      </div>
      <div>
        <Button
          data-testid="small-disabled-icon"
          {...props}
          icon="Flash"
          disabled={true}
          size="s"
        />
      </div>
      <div>
        <Button
          data-testid="xsmall-disabled-icon"
          {...props}
          icon="Flash"
          disabled={true}
          size="xs"
        />
      </div>
    </div>
  </>
);

const meta: Meta<typeof ButtonExamples> = {
  title: "Components/Button",
  component: ButtonExamples,
};

export default meta;

type Story = StoryObj<ButtonProps>;

export const Primary: Story = {
  args: {
    hierarchy: "primary",
    onClick: fn(),
  },

  play: async ({ canvasElement, step, userEvent, args }) => {
    const canvas = within(canvasElement);
    const buttons = await canvas.findAllByRole("button");

    for (const button of buttons) {
      const testID = button.getAttribute("data-testid");

      // skip disabled buttons
      if (button.hasAttribute("disabled")) {
        continue;
      }

      await step(`Click on ${testID}`, async () => {
        // move the mouse over the button
        await userEvent.hover(button);

        // the pointer should be normal
        await expect(getCursorStyle(button)).toEqual("pointer");

        // click the button
        await userEvent.click(button);

        // the click handler should have been called
        await expect(args.onClick).toHaveBeenCalled();
      });
    }
  },
};

export const Secondary: Story = {
  args: {
    ...Primary.args,
    hierarchy: "secondary",
  },
  play: Primary.play,
};

export const GhostPrimary: Story = {
  args: {
    ...Primary.args,
    hierarchy: "primary",
    ghost: true,
  },
  play: Primary.play,
  decorators: [
    (Story) => (
      <div class="p-10 bg-def-3">
        <Story />
      </div>
    ),
  ],
};

export const GhostSecondary: Story = {
  args: {
    ...Primary.args,
    hierarchy: "secondary",
    ghost: true,
  },
  play: Primary.play,
};
