import type { Meta, StoryObj } from "@kachurun/storybook-solid";
import { Button, ButtonProps } from "./Button";
import { Component } from "solid-js";
import { expect, fn, waitFor } from "storybook/test";
import { StoryContext } from "@kachurun/storybook-solid-vite";

const getCursorStyle = (el: Element) => window.getComputedStyle(el).cursor;

const ButtonExamples: Component<ButtonProps> = (props) => (
  <>
    <div class="grid w-fit grid-cols-4 gap-8">
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
        <Button data-testid="default-start-icon" {...props} startIcon="Flash">
          Label
        </Button>
      </div>
      <div>
        <Button
          data-testid="small-start-icon"
          {...props}
          startIcon="Flash"
          size="s"
        >
          Label
        </Button>
      </div>
      <div>
        <Button
          data-testid="default-disabled-start-icon"
          {...props}
          startIcon="Flash"
          disabled={true}
        >
          Disabled
        </Button>
      </div>
      <div>
        <Button
          data-testid="small-disabled-start-icon"
          {...props}
          startIcon="Flash"
          size="s"
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
        <Button data-testid="default-icon" {...props} icon="Flash" />
      </div>
      <div>
        <Button data-testid="small-icon" {...props} icon="Flash" size="s" />
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
    </div>
  </>
);

const meta: Meta<ButtonProps> = {
  title: "Components/Button",
  component: ButtonExamples,
};

export default meta;

type Story = StoryObj<ButtonProps>;

export const Primary: Story = {
  args: {
    hierarchy: "primary",
    onAction: fn(async () => {
      // wait 500 ms to simulate an action
      await new Promise((resolve) => setTimeout(resolve, 1000));
      // randomly fail to check that the loading state still returns to normal
      if (Math.random() > 0.5) {
        throw new Error("Action failure");
      }
    }),
  },
  parameters: {
    test: {
      // increase test timeout to allow for the loading action
      mockTimers: true,
    },
  },

  play: async ({ canvas, step, userEvent, args }: StoryContext) => {
    const buttons = await canvas.findAllByRole("button");

    for (const button of buttons) {
      const testID = button.getAttribute("data-testid");

      // skip disabled buttons
      if (button.hasAttribute("disabled")) {
        continue;
      }

      await step(`Click on ${testID}`, async () => {
        // check for the loader
        const loaders = button.getElementsByClassName("loader");
        await expect(loaders.length).toEqual(1);

        // assert its width is 0 before we click
        const [loader] = loaders;
        await expect(loader.clientWidth).toEqual(0);

        // move the mouse over the button
        await userEvent.hover(button);

        // the pointer should be normal
        await expect(getCursorStyle(button)).toEqual("pointer");

        // click the button
        await userEvent.click(button);

        // check the button has changed
        await waitFor(async () => {
          // the action handler should have been called
          await expect(args.onAction).toHaveBeenCalled();
          // the button should have a loading class
          await expect(button).toHaveClass("loading");
          // the loader should be visible
          await expect(loader.clientWidth).toBeGreaterThan(0);
          // the pointer should have changed to wait
          await expect(getCursorStyle(button)).toEqual("wait");
        });

        // wait for the action handler to finish
        await waitFor(
          async () => {
            // the loading class should be removed
            await expect(button).not.toHaveClass("loading");
            // the loader should be hidden
            await expect(loader.clientWidth).toEqual(0);
            // the pointer should be normal
            await expect(getCursorStyle(button)).toEqual("pointer");
          },
          { timeout: 1500 },
        );
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
    (Story: StoryObj) => (
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
