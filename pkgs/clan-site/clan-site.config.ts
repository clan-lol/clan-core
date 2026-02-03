import process from "node:process";

export default {
  ver: process.env["SITE_VER"] || "unstable",
  docs: {
    searchResultLimit: 5,
    minLineNumberLines: 4,
    maxTocExtractionDepth: 3,
    codeLightTheme: "catppuccin-latte",
    codeDarkTheme: "catppuccin-macchiato",
    nav: [
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
    ],
  },
};
