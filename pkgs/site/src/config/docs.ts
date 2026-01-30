import type { NavItemInput } from "$lib/models/docs/index.ts";

export const navItems: NavItemInput[] = [
  {
    label: "Getting Started",
    items: ["/getting-started/add-machines"],
  },
  {
    label: "Reference",
    items: [
      {
        label: "Overview",
        slug: "/reference",
      },
      {
        label: "Options",
        autogenerate: { directory: "/reference/options" },
      },
    ],
  },
  {
    label: "Test",
    link: "/test",
  },
];

export const minLineNumberLines = 4;
export const maxTocExtractionDepth = 3;
export const codeLightTheme = "catppuccin-latte";
export const codeDarkTheme = "catppuccin-macchiato";
