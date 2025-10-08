import type { RawNavLink } from "./routes/docs";

export const blog = {
  base: "/blog",
};
export const docs = {
  base: "/docs",
  navLinks: [
    {
      label: "Getting Started",
      items: ["getting-started/add-machines"],
    },
    {
      label: "Reference",
      items: [
        {
          label: "Overview",
          slug: "reference/overview",
        },
        {
          label: "Options",
          autogenerate: { directory: "reference/options" },
        },
      ],
    },
  ] as RawNavLink[],
};

export const markdown = {
  minLineNumberLines: 4,
};
