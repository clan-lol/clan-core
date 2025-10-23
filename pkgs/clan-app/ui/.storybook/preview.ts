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
  },
};

export default preview;
