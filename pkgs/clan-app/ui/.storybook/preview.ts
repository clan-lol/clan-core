import type { Preview } from "@kachurun/storybook-solid";

export const preview: Preview = {
  tags: ["autodocs"],
  parameters: {
    docs: { toc: true },
    backgrounds: {
      values: [
        { name: "Dark", value: "#333" },
        { name: "Light", value: "#F7F9F2" },
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
