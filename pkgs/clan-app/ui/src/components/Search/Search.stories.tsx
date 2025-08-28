import { Meta, StoryObj } from "@kachurun/storybook-solid";

import { Search, SearchProps } from "./Search";
import Icon from "../Icon/Icon";
import { Combobox } from "@kobalte/core/combobox";
import { Typography } from "../Typography/Typography";
import {
  ItemRenderOptions,
  SearchMultiple,
  SearchMultipleProps,
} from "./MultipleSearch";
import { Show } from "solid-js";

const meta = {
  title: "Components/Search",
  component: Search,
} satisfies Meta<SearchProps<unknown>>;

export default meta;

type Story = StoryObj<SearchProps<unknown>>;

// To test the virtualizer, we can generate a list of modules
function generateModules(count: number): Module[] {
  const greek = [
    "alpha",
    "beta",
    "gamma",
    "delta",
    "epsilon",
    "zeta",
    "eta",
    "theta",
    "iota",
    "kappa",
    "lambda",
    "mu",
    "nu",
    "xi",
    "omicron",
    "pi",
    "rho",
    "sigma",
    "tau",
    "upsilon",
    "phi",
    "chi",
    "psi",
    "omega",
  ];

  const modules: Module[] = [];

  for (let i = 0; i < count; i++) {
    modules.push({
      value: `lolcat/module-${i + 1}`,
      label: `Module ${i + 1}`,
      description: `${greek[i % greek.length]}#${i + 1} this is a very long description to test text wrapping in the search component`,
      input: "lolcat-flake-part-from-nixpkgs-via-nix-via-clan-flake",
    });
  }

  return modules;
}

export interface Module {
  value: string;
  label: string;
  input: string;
  description: string;
}

export const Default: Story = {
  args: {
    height: "14.5rem",
    // Test with lots of modules
    options: generateModules(1000),
    renderItem: (item: Module) => {
      return (
        <div class="flex items-center justify-between gap-2 rounded-md px-2 py-1 pr-4">
          <div class="flex size-8 shrink-0 items-center justify-center rounded-md bg-white">
            <Icon icon="Code" />
          </div>
          <div class="flex w-full flex-col">
            <Combobox.ItemLabel class="flex">
              <Typography hierarchy="body" size="s" weight="medium" inverted>
                {item.label}
              </Typography>
            </Combobox.ItemLabel>
            <Typography
              hierarchy="body"
              size="xxs"
              weight="normal"
              color="quaternary"
              inverted
              class="flex justify-between"
            >
              <span class="inline-block max-w-72 truncate align-middle">
                {item.description}
              </span>
              <span class="inline-block max-w-20 truncate align-middle">
                by {item.input}
              </span>
            </Typography>
          </div>
        </div>
      );
    },
  },
  render: (args: SearchProps<Module>) => {
    return (
      <div class="fixed bottom-10 left-1/2 mb-2 w-[30rem] -translate-x-1/2">
        <Search<Module>
          {...args}
          onChange={(module) => {
            // Go to the module configuration
            console.log("Selected module:", module);
          }}
        />
      </div>
    );
  },
};

export const Loading: Story = {
  args: {
    height: "14.5rem",
    // Test with lots of modules
    loading: true,
    options: [],
    renderItem: () => <span></span>,
  },
  render: (args: SearchProps<Module>) => {
    return (
      <div class="absolute bottom-1/3 w-3/4 px-3">
        <Search<Module>
          {...args}
          onChange={(module) => {
            // Go to the module configuration
          }}
        />
      </div>
    );
  },
};

type MachineOrTag =
  | {
      value: string;
      label: string;
      type: "machine";
      disabled?: boolean;
    }
  | {
      members: string[];
      value: string;
      label: string;
      disabled?: boolean;
      type: "tag";
    };

const machinesAndTags: MachineOrTag[] = [
  { value: "machine-1", label: "Machine 1", type: "machine" },
  { value: "machine-2", label: "Machine 2", type: "machine" },
  {
    value: "all",
    label: "All",
    type: "tag",
    members: ["machine-1", "machine-2", "machine-3", "machine-4", "machine-5"],
  },
  {
    value: "tag-1",
    label: "Tag 1",
    type: "tag",
    members: ["machine-1", "machine-2"],
  },
  { value: "machine-3", label: "Machine 3", type: "machine" },
  { value: "machine-4", label: "Machine 4", type: "machine" },
  { value: "machine-5", label: "Machine 5", type: "machine" },
  {
    value: "tag-2",
    label: "Tag 2",
    type: "tag",
    members: ["machine-3", "machine-4", "machine-5"],
  },
];
export const Multiple: Story = {
  args: {
    // Test with lots of modules
    options: machinesAndTags,
    placeholder: "Search for Machine or Tags",
    renderItem: (item: MachineOrTag, opts: ItemRenderOptions) => {
      console.log("Rendering item:", item, "opts", opts);
      return (
        <div class="flex w-full items-center gap-2 px-3 py-2">
          <Combobox.ItemIndicator>
            <Show when={opts.selected} fallback={<Icon icon="Code" />}>
              <Icon icon="Checkmark" color="primary" inverted />
            </Show>
          </Combobox.ItemIndicator>
          <Combobox.ItemLabel class="flex items-center gap-2">
            <Typography
              hierarchy="body"
              size="s"
              weight="medium"
              inverted
              color={opts.disabled ? "quaternary" : "primary"}
            >
              {item.label}
            </Typography>
            <Show when={item.type === "tag" && item}>
              {(tag) => (
                <Typography
                  hierarchy="body"
                  size="xs"
                  weight="medium"
                  inverted
                  color="secondary"
                  tag="div"
                >
                  {tag().members.length}
                </Typography>
              )}
            </Show>
          </Combobox.ItemLabel>
          <Icon
            class="ml-auto"
            icon={item.type === "machine" ? "Machine" : "Tag"}
            color="quaternary"
            inverted
          />
        </div>
      );
    },
  },
  render: (args: SearchMultipleProps<MachineOrTag>) => {
    return (
      <div class="absolute bottom-1/3 w-3/4 px-3">
        <SearchMultiple<MachineOrTag>
          {...args}
          divider
          height="20rem"
          virtualizerOptions={{
            estimateSize: () => 38,
          }}
          onChange={(selection) => {
            // Go to the module configuration
            console.log("Currently Selected:", selection);
          }}
        />
      </div>
    );
  },
};
