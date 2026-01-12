import type { Preview } from "storybook-solidjs-vite";

import "../src/index.css";
import "./preview.css";

export const preview: Preview = {
  tags: ["autodocs"],
  parameters: {
    docs: { toc: true },

    // automatically create action args for all props that start with "on"
    actions: { argTypesRegex: "^on.*" },

    controls: {
      matchers: {
        color: /(background|color)$/i,
        date: /Date$/,
      },
    },

    a11y: {
      // 'todo' - show a11y violations in the test UI only
      // 'error' - fail CI on a11y violations
      // 'off' - skip a11y checks entirely
      test: "todo",
    },
  },
};

export default preview;
