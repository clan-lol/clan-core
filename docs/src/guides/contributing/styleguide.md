# Styleguide

## Framework features

### Admonitions

Basic Syntax

```md
:::admonition[Title]{type=info collapsible open}
Collapsiple Info
:::
```

Types:

:::admonition{type=info}
Important information
:::

:::admonition{type=important}
Important information
:::

:::admonition{type=tip}
Important information
:::

:::admonition{type=example}
Important information
:::

Collapsible

:::admonition{type=info collapsible open}
Collapsed info default open
:::

:::admonition{type=info collapsible}
Collapsed info default closed
:::

Custom title

:::admonition[Custom Title]{type=info}
Important information
:::

### Code Examples

```nix
let
  is = nix: nix;
in
{
  this = is "valid";
}
```

Highlight Code in a Snippet

```nix {2,4-6}
{
  this line is highlighted
  this line is NOT highlighted
  this line is highlighted
  this line is highlighted
  this line is highlighted
  this line is NOT highlighted
}
```

## Writing Principles

A consistent style greatly increases the usability of all documentation and communication.

Use this page as a reference and style guide for our internal and external documentation, blog posts, and all other Clan communication.

### Knowledge Expectations

**Assume competence, not familiarity.**

Write for someone who knows a great deal — up to but not including this project.

**What readers know:**

- Basic computer operation
- Command line familiarity
- General interest in systems configuration

**What readers don't know:**

- Clan-specific concepts
- NixOS ecosystem details or grammar
- Deployment workflows

If specific knowledge is required, mention it at the start of the page.

#### Show, Don't Tell

The fastest path to understanding is a working example.
People learn by doing, not by reading about doing.

**Recommended structure:**

- Start with the minimal working code or command
- Briefly explain what it does
- Cover edge cases or variations
- Link to further information instead of including it

#### Grammar and Style

**Sentence structure:**

- Use simple, direct sentences
- Break complex ideas into multiple short sentences
- Avoid nested clauses

**Bad:**

> The following command, which utilizes nixos-facter to generate a comprehensive hardware report, will write the results back into the respective machine folder located on your setup device.

What the user does is hidden in the middle.
`nixos-facter` is a leaked implementation detail.
Users care about *hardware scanning*, not *the tool that does it*.

**Good:**

> This command generates a hardware report and saves it to your machine folder.

#### Content Organization

Lead with value. State what the reader will accomplish before explaining how.

**Bad:**

> To create a new machine that you can later use as a webserver, first navigate to your Clan directory, then execute the clan machines create command with the --name flag followed by your desired machine name.

**Good:**

Create a new webserver machine in your Clan:

```bash
clan machines create --name webserver
```

Use **progressive disclosure**. Introduce concepts only when needed.

**Recommended structure:**

1. State the goal (one sentence)
2. Show the simplest working example
3. Explain concepts if needed
4. Provide advanced options separately or link to the reference

#### Code Examples

**Keep examples focused:**

- Show one concept at a time
- Use realistic but simple scenarios
- Avoid dependencies on other examples

**Minimal comments**

Let the code speak for itself.
Paste code examples directly and without further alteration.

**Bad:**

```nix
# This sets the target host IP address for deployment
clan.networking.targetHost = "192.168.1.10"; # Change this to your machine's IP
# This enables SSH access
services.openssh.enable = true; # Required for Clan deployment
```

**Good:**

```nix
{
  clan.networking.targetHost = "192.168.XXX.XXX";
  services.openssh.enable = true;
}
```

#### Hide Nix Where Possible

Nix knowledge is a barrier, not a feature.

- Prefer `clan` CLI commands
- Show configuration as *what you want*, not *how Nix works*
- Explain only what Nix does in the context of Clan

**Bad:**

> Before adding a machine, you need to understand the NixOS module system and attribute set merging.

**Good:**

Add a machine:

```bash
clan machines create webserver
```

This creates `machines/webserver/default.nix`, where you can configure it via NixOS.

#### Teach Nix Through Examples, Not Theory

*(After respecting the prior point)*

Users learn the NixOS module system by seeing patterns first.

- Start with a working example
- Explanation follows the code
- Link deeper concepts instead of inlining them
- Link to `nix.dev` for optional learning

#### General Rules

- Abbreviate keys like `ssh-ed25519 AAAAC3NzaC…`
- Abbreviate IP addresses like `192.168.XXX.XXX`
- Variables are capitalized and start with `$`, e.g. `$YOUR-CLAN-NAME`
- Variables should be directly usable during copy-paste
- Do **not** describe missing code parts (`#elided`, `#omitted`)
- **Machines vs Devices**:
    - machine = Clan identity
    - device = hardware

#### Capitalization

- Clan
- GB / RAM / HDD
- bootable USB drive
- Wi-Fi / DHCP / DNS
- macOS / NixOS / Nix / Linux
- Flakes
- WireGuard
- ZeroTier
- git
- direnv
- Setup Device / Target Devices

#### Imperative Mood, Voice, and Person

Use imperative mood for instructions. Address the reader as "you", not "the user". Use active voice; in other words, make the subject do the action.

**Don't:**

> The user should run the following command.
> The configuration will need to be updated.
> The key is generated by the system.

**Do:**

> Run the command.
> Update the configuration.
> The system generates the key.

#### Tense

Use present tense for descriptions. Future tense makes documentation feel tentative.

**Don't:**

> This will create a new machine folder.
> Running this command will install the package.

**Do:**

> This creates a new machine folder.
> Running this command installs the package.

#### Avoid Nominalizations

A nominalization is a verb turned into a noun, often by adding *-tion*, *-ment*, or *-ance* (e.g. "explanation", "selection"). The fix: find the hidden verb and use it directly.

**Don't:**

> Make a selection from the list.
> Provide an explanation of the error.

**Do:**

> Select from the list.
> Explain the error.

#### Filler Words and Weak Phrases

Cut words and phrases that add length without meaning.

Delete on sight:

- "simply", "just", "easily", "basically", "obviously"
- "in order to" → use "to"
- "allows you to" → use the verb directly
- "it's worth noting that" → just say the thing

**Don't:**

> Simply run `clan machines create`.
> In order to deploy, you first need to run the command, which allows you to push the config.
> It's worth noting that this requires root access.

**Do:**

> Run `clan machines create`.
> To deploy, run:
> This requires root access.

Every word must earn its place.

#### Writing Procedures

One instruction per sentence. Don't pack multiple actions into one sentence.

**Don't:**

> Navigate to your Clan directory and run the command, then check the output.

**Do:**

1. Navigate to your Clan directory.
2. Run the command.
3. Check the output.

Don't bury the negative. Key limitations should be prominent, not a footnote after a positive description.

**Don't:**

> This service supports multiple roles, integrates with the vars system, and works great for most setups (note that multiple instances are not supported).

**Do:**

> This service does not support multiple instances.

#### Consistent Terminology

Pick a term and stick to it. Don't swap synonyms to avoid repetition. In technical documetnation, repetition is clarity.

**Don't:**

> Create a machine... configure the host... deploy the node.

**Do:**

> Create a machine... configure the machine... deploy the machine.

#### Links

Use descriptive link text. Never use "click here" or "this link."

**Don't:**

> For more information, see [this page](url).
> Click [here](url) to read the reference.

**Do:**

> See [inventory reference](url) for details.
> Read the [NixOS module system guide](url).

Only link when the destination is directly relevant, not for generic background context (sometimes known as "Wikipedia-style links"). Readers feel obligated to click links, fearing they'll miss something important. Don't send them to a generic article about a technology when they're looking for how *your* system uses it.

**Don't:**

> Our software uses [SQLite](https://sqlite.org/) for storage.
> *(Reader clicks expecting schema details — finds a generic product page instead.)*

(Note that in the above example, the SQLite link is the SQLite home page, which is likely not pertinent.)

**Do:**

> See [database schema](url) for the full table structure.

#### UI Language

Match UI element names exactly: wording, casing, and spacing (even if a label seems oddly worded).

**Don't:**

> Click the generator button.
> Select the save option.

**Do:**

> Click **Generate a Key**.
> Click **Save Changes**.

Someone will go looking for a button labeled "generator." They will not find it. They will be frustrated.

Consistency between documentation and interface builds confidence. Words are part of the interface.

:::admonition{type=tip}
This can be tricky as UI changes; we don't yet have a policy in place for how to handle this. We welcome comments and suggestions.
:::

Tip:

#### Clean System Discipline

Your machine has things new users don't: cached credentials, installed tools, environment variables, existing configuration. When writing or updating documentation:

**Don't:**

> Write steps from memory on your development machine, assuming what works there will work everywhere.

**Do:**

> - Start on a clean system — a fresh VM or new user account
> - Take notes in real time as you work through the steps
> - Document every warning, prompt, or unexpected output the system shows

Also think in combinations: WSL vs native Linux, with and without existing keys. You don't need to test every matrix square — but you need to know which ones diverge.

#### Never Type Code — Always Copy-Paste

Always copy commands and code from a terminal where you just ran them successfully. Never retype from memory.

**Don't:**

> Retype a command from memory into the documentation.

**Do:**

> Paste commands directly from the shell or IDE.

Replace sensitive values with placeholders: `<YOUR-KEY>`, `<YOUR-HOST>`, `<YOUR-TOKEN>`.

Typed-from-memory commands introduce subtle errors. Even the most experienced software developers have occasional typos.

