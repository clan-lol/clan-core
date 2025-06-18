import type { Preview } from "@kachurun/storybook-solid";

import "@/src/components/v2/index.css";
import "../src/index.css";
import "./preview.css";

export const preview: Preview = {
  tags: ["autodocs"],
  parameters: {
    docs: { toc: true },
    backgrounds: {
      values: [
        { name: "Dark", value: "#333" },
        { name: "Light", value: "#ffffff" },
      ],
      default: "Light",
    },
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
