import { Meta, StoryObj } from "@kachurun/storybook-solid";

import { Search, SearchProps, Module } from "./Search";

const meta = {
  title: "Components/Search",
  component: Search,
} satisfies Meta<SearchProps>;

export default meta;

type Story = StoryObj<SearchProps>;

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
      name: `Module ${i + 1}`,
      description: `${greek[i % greek.length]}#${i + 1}`,
      input: "lolcat",
    });
  }

  return modules;
}

export const Default: Story = {
  args: {
    // Test with lots of modules
    options: generateModules(1000),
  },
  render: (args: SearchProps) => {
    return (
      <div class="absolute bottom-1/3 w-3/4 px-3">
        <Search
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
