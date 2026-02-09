const version = process.env["SITE_VER"] || "unstable";
export default {
  version,
  searchResultLimit: 5,
  codeMinLineNumberLines: 4,
  codeLightTheme: "catppuccin-latte",
  codeDarkTheme: "catppuccin-macchiato",
  maxTocExtractionDepth: 3,
  docsDir: "src/docs",
  docsBase: `/docs/${version}` satisfies DocsPath,
  docsNav: [
    {
      label: "Getting Started",
      items: [
        "/",
        "/getting-started/creating-your-first-clan",
        "/getting-started/add-machines",
        "/getting-started/add-users",
        "/getting-started/add-services",
        "/getting-started/prepare-physical-machines",
        "/getting-started/prepare-virtual-machines",
        "/getting-started/configure-disk",
        "/getting-started/deployment-phase",
        "/getting-started/update-machines",
        "/getting-started/whats-next",
      ],
    },
    {
      label: "Gudies",
      items: ["/guides/inventory/inventory"],
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
          auto: "/reference/options",
        },
      ],
    },
    {
      label: "Services",
      items: ["/services/definition"],
    },
    {
      label: "Test",
      path: "/test",
    },
  ] satisfies readonly DocsNavItem[],
};

export type Path = `/${string}`;
export type DocsPath = `/docs/${string}`;

export type DocsNavItem =
  | Path
  | {
      readonly label: string;
      readonly items: readonly DocsNavItem[];
      readonly collapsed?: boolean;
      readonly badge?: Badge;
    }
  | {
      readonly label: string;
      readonly auto: Path;
      readonly collapsed?: boolean;
      readonly badge?: Badge;
    }
  | {
      readonly label?: string;
      readonly slug: Path;
      readonly badge?: Badge;
    }
  | {
      readonly label: string;
      readonly path: Path;
      readonly badge?: Badge;
    }
  | {
      readonly label: string;
      readonly url: string;
      readonly badge?: Badge;
    };

export type Badge =
  | string
  | {
      readonly text: string;
      readonly variant: "caution" | "normal";
    };
