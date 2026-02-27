import type {
  NavItemsConfig as DocsNavItems,
  DocsPath,
} from "#lib/models/docs.ts";
import { extractCustomMedia } from "#lib/models/custom-media.server.ts";

export const version = process.env["SITE_VER"] || "unstable";
export const customMedia = await extractCustomMedia();
export const searchResultLimit = 5;
export const codeMinLineNumberLines = 4;
export const codeLightTheme = "catppuccin-latte";
export const codeDarkTheme = "catppuccin-macchiato";
export const maxTocDepth = 3;
export const docsDir = "src/docs";
export const docsBase: DocsPath = `/docs/${version}`;
export const docsNav: DocsNavItems = [
  {
    label: "Getting Started",
    children: [
      "",
      "getting-started/creating-your-first-clan",
      "getting-started/add-machines",
      "getting-started/add-users",
      "getting-started/add-services",
      "getting-started/prepare-physical-machines",
      "getting-started/prepare-virtual-machines",
      "getting-started/configure-disk",
      "getting-started/deployment-phase",
      "getting-started/update-machines",
      "getting-started/whats-next",
    ],
  },
  {
    label: "Guides",
    children: [
      {
        label: "Inventory",
        children: [
          "guides/inventory/inventory",
          "guides/inventory/autoincludes",
        ],
      },
      {
        label: "Services",
        children: [
          "guides/services/introduction-to-services",
          "guides/services/community",
          "guides/services/exports",
          "guides/internal-ssl-services",
        ],
      },
      {
        label: "Vars",
        children: [
          "guides/vars/vars-overview",
          "guides/vars/vars-backend",
          "guides/vars/vars-concepts",
          "guides/vars/vars-advanced-examples",
          "guides/vars/vars-troubleshooting",
          {
            label: "Sops Backend",
            children: [
              "guides/vars/sops/age-plugins",
              "guides/vars/sops/secrets",
            ],
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
      "guides/macos",
      {
        label: "Templates",
        children: ["concepts/templates", "guides/disko-templates/community"],
      },
      {
        label: "Migrations",
        children: [
          "guides/migrations/convert-existing-NixOS-configuration",
          "guides/migrations/migrate-admin-service",
          "guides/migrations/migrate-inventory-services",
          "guides/migrations/migration-facts-vars",
          "guides/migrations/disk-id",
        ],
      },
      "guides/disk-encryption",
      "guides/secure-boot",
      {
        label: "Contributing",
        children: [
          "guides/contributing/CONTRIBUTING",
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
        children: [
          "reference/options/clan",
          "reference/options/clan_inventory",
          "reference/options/clan_service",
        ],
      },
      {
        label: "clan.core (Machine Options)",
        children: [
          "reference/clan.core",
          "reference/clan.core/backups",
          "reference/clan.core/deployment",
          "reference/clan.core/networking",
          "reference/clan.core/postgresql",
          "reference/clan.core/settings",
          "reference/clan.core/sops",
          "reference/clan.core/state",
          "reference/clan.core/vars",
        ],
      },
      {
        label: "CLI",
        children: [
          "reference/cli",
          "reference/cli/backups",
          "reference/cli/flakes",
          "reference/cli/flash",
          "reference/cli/init",
          "reference/cli/machines",
          "reference/cli/select",
          "reference/cli/secrets",
          "reference/cli/show",
          "reference/cli/ssh",
          "reference/cli/state",
          "reference/cli/templates",
          "reference/cli/vars",
          "reference/cli/vms",
        ],
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
        children: [
          "services/official/admin",
          "services/official/borgbackup",
          "services/official/certificates",
          "services/official/coredns",
          "services/official/data-mesher",
          "services/official/dm-dns",
          "services/official/dyndns",
          "services/official/emergency-access",
          "services/official/garage",
          "services/official/hello-world",
          "services/official/internet",
          "services/official/importer",
          "services/official/kde",
          "services/official/localbackup",
          "services/official/matrix-synapse",
          "services/official/mycelium",
          "services/official/monitoring",
          "services/official/ncps",
          "services/official/packages",
          "services/official/pki",
          "services/official/sshd",
          "services/official/syncthing",
          "services/official/trusted-nix-caches",
          "services/official/tor",
          "services/official/users",
          "services/official/wifi",
          "services/official/wireguard",
          "services/official/yggdrasil",
          "services/official/zerotier",
        ],
      },
      "services/community",
    ],
  },
  {
    label: "Test",
    path: "test",
  },
];
