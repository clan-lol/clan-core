import type { NavItemsConfig as DocsNavItems } from "#lib/models/docs.ts";
import {
  getCustomMedia,
  getGeneratedDocsDir,
  getVersion,
} from "#lib/util.server.ts";
import pathutil from "node:path";

export const version = await getVersion();
export const customMedia = await getCustomMedia();
export const searchResultLimit = 20;
export const codeMinLineNumberLines = 4;
export const codeLightTheme = "catppuccin-latte";
export const codeDarkTheme = "catppuccin-macchiato";
export const maxTocDepth = 3;
export const copyButtonMessageDelay = 3000;
export const docsSrcDirs = [
  pathutil.resolve(import.meta.dirname, "../../docs/src"),
  getGeneratedDocsDir(),
] as const;
export const docsCodeEmbedsDir = pathutil.resolve(
  import.meta.dirname,
  "../../docs/embeds",
);
export const docsBase = "/docs" as const;
export const docsNav: DocsNavItems = [
  { label: "Home", path: "" },
  {
    label: "Getting Started",
    children: [
      { label: "Install Nix and direnv", path: "getting-started/install-nix" },
      { label: "Quick Start", path: "getting-started/quick-start" },
      {
        label: "Install on Physical Machine",
        path: "getting-started/getting-started-physical",
      },
      {
        label: "Install in VirtualBox",
        path: "getting-started/getting-started-virtualbox",
      },
      {
        label: "Install on AWS",
        path: "getting-started/getting-started-aws",
      },
      {
        label: "Install on Google Cloud",
        path: "getting-started/getting-started-google",
      },
      {
        label: "Install on Hetzner",
        path: "getting-started/getting-started-hetzner",
      },
      { label: "Create an SSH Key", path: "getting-started/create-an-ssh-key" },
      "getting-started/whats-next",
    ],
  },
  {
    label: "Guides",
    children: [
      {
        label: "Inventory",
        children: [
          "guides/inventory/intro-to-inventory",
          "guides/inventory/autoincludes",
        ],
      },
      {
        label: "Services",
        children: [
          "guides/services/intro-to-services-revised",
          "guides/services/community",
          "guides/services/exports",
          "guides/internal-ssl-services",
        ],
      },
      {
        label: "Vars",
        children: [
          "guides/vars/intro-to-vars",
          {
            label: "Backend",
            children: [
              "guides/vars/vars-backend",
              {
                label: "Sops Backend",
                children: [
                  "guides/vars/sops/age-plugins",
                  "guides/vars/sops/secrets",
                ],
              },
              {
                label: "Age Backend",
                children: ["guides/vars/age/age-backend"],
              },
            ],
          },
          { label: "Concepts", path: "guides/vars/vars-concepts" },
          {
            label: "Advanced Examples",
            path: "guides/vars/vars-advanced-examples",
          },
          {
            label: "Troubleshooting",
            path: "guides/vars/vars-troubleshooting",
          },
        ],
      },
      {
        label: "Backups",
        children: [
          "guides/backups/backup-intro",
          "guides/backups/minimal-example",
          "guides/backups/digging-deeper",
          "guides/backups/advanced-example",
        ],
      },
      {
        label: "Networking",
        children: [
          "guides/networking/networking",
          "guides/networking/mesh-vpn",
        ],
      },
      "guides/nixpkgs-flake-input",
      "guides/flake-parts",
      "guides/nixos-rebuild",
      { label: "MacOS", path: "guides/macos" },
      {
        label: "Templates",
        children: ["concepts/templates", "guides/disko-templates/community"],
      },
      {
        label: "Migrations",
        children: [
          "guides/migrations/convert-existing-NixOS-configuration",
          "guides/migrations/how-to-rename-a-machine",
          "guides/migrations/migrate-admin-service",
          "guides/migrations/migrate-inventory-services",
          "guides/migrations/migration-facts-vars",
          "guides/migrations/disk-id",
        ],
      },
      "guides/build-host",
      "guides/ssh-agent-forwarding",
      "guides/private-inputs",
      "guides/disk-encryption",
      "guides/secure-boot",
      {
        label: "Contributing",
        children: [
          // TODO: implement symlink follow
          "guides/contributing/CONTRIBUTING",
          "guides/contributing/writing-documentation",
          "guides/contributing/debugging",
          "guides/contributing/testing",
          "guides/contributing/styleguide",
        ],
      },
    ],
  },
  {
    label: "Reference",
    children: [
      {
        label: "Overview",
        path: "reference",
      },
      {
        label: "Options",
        pathPrefix: "reference/options",
      },
      {
        label: "clan.core (Machine Options)",
        pathPrefix: "reference/clan.core",
      },
      {
        label: "CLI",
        pathPrefix: "reference/cli",
      },
      "reference/clanLib",
      {
        label: "Decisions",
        children: [
          "decisions/Architecture-decisions",
          "decisions/01-Clan-Modules",
          "decisions/02-clan-as-library",
          "decisions/03-adr-numbering-process",
          "decisions/04-fetching-nix-from-python",
          "decisions/05-deployment-parameters",
          "decisions/template",
        ],
      },
      "reference/glossary",
      {
        label: "Releases",
        children: ["releases/25-11"],
      },
    ],
  },
  {
    label: "Services",
    children: [
      "services/definition",
      {
        label: "Official",
        pathPrefix: "services/official",
      },
      "services/community",
    ],
  },
];
