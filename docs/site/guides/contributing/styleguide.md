## Style Guide for Documentation and Blog Posts

A consistent style greatly increases the usability of all documentation and communication.  
Please use this page as a reference and style guide for our internal and external documentation, blog posts, and all other Clan communication.

### Writing Principles

#### Knowledge Expectations

**What readers know:**

- Basic computer operation
- Command line familiarity
- General interest in systems configuration

**What readers don't know:**

- Clan-specific concepts
- NixOS ecosystem details or grammar
- Deployment workflows

If specific knowledge is required, mention it at the start of the page.

---

#### Show, Don't Tell

The fastest path to understanding is a working example.  
People learn by doing, not by reading about doing.

**Recommended structure:**

- Start with the minimal working code or command
- Briefly explain what it does
- Cover edge cases or variations
- Link to further information instead of including it

---

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

---

#### Content Organization

Lead with value. State what the reader will accomplish before explaining how.

**Bad:**

> To create a new machine that you can later use as a webserver, first navigate to your Clan directory, then execute the clan machines create command with the --name flag followed by your desired machine name.

**Good:**

Create a new webserver machine in your Clan:

~~~nix
clan machines create --name webserver
~~~

Use **progressive disclosure**. Introduce concepts only when needed.

**Recommended structure:**

1. State the goal (one sentence)
2. Show the simplest working example
3. Explain concepts if needed
4. Provide advanced options separately or link to the reference

---

#### Code Examples

**Keep examples focused:**

- Show one concept at a time
- Use realistic but simple scenarios
- Avoid dependencies on other examples

**Minimal comments**

Let the code speak for itself.  
Paste code examples directly and without further alteration.

**Bad:**

~~~nix
# This sets the target host IP address for deployment
clan.networking.targetHost = "192.168.1.10"; # Change this to your machine's IP
# This enables SSH access
services.openssh.enable = true; # Required for Clan deployment
~~~

**Good:**

~~~nix
{
  clan.networking.targetHost = "192.168.XXX.XXX";
  services.openssh.enable = true;
}
~~~

---

#### Hide Nix Where Possible

Nix knowledge is a barrier, not a feature.

- Prefer `clan` CLI commands
- Show configuration as *what you want*, not *how Nix works*
- Explain only what Nix does in the context of Clan

**Bad:**

> Before adding a machine, you need to understand the NixOS module system and attribute set merging.

**Good:**

Add a machine:

~~~bash
clan machines create webserver
~~~

This creates `machines/webserver/default.nix`, where you can configure it via NixOS.

---

#### Teach Nix Through Examples, Not Theory

*(After respecting the prior point)*

Users learn the NixOS module system by seeing patterns first.

- Start with a working example
- Explanation follows the code
- Link deeper concepts instead of inlining them
- Link to `nix.dev` for optional learning

---

### Style Guidelines

#### General Rules

- Abbreviate keys like `ssh-ed25519 AAAAC3NzaC…`
- Abbreviate IP addresses like `192.168.XXX.XXX`
- Variables are capitalized and start with `$`, e.g. `$YOUR-CLAN-NAME`
- Variables should be directly usable during copy-paste
- Do **not** describe missing code parts (`#elided`, `#omitted`)
- Use `##` for headlines and `###` for subchapters


- **Machines vs Devices**:
    - machine = Clan identity
    - device = hardware

---

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
- Setup Machine / Target Machines
- devices / systems

---

#### Code in Text

Inline code is marked like ```this```.

---

#### Code Snippets

```text
multi
line
code
```

---

#### Highlight Code in a Snippet

Use ```hl_lines``` to highlight specific lines. 

Example: hl_lines="2 4-6" 

~~~nix {hl_lines="2 4-6"}
{
  this line is highlighted
  this line is NOT highlighted
  this line is highlighted
  this line is highlighted
  this line is highlighted
  this line is NOT highlighted
}
~~~

---

#### Under Construction Flags

!!! warning "HeadlineText"
    Use ```!!! warning HeadlineText```
    
    Text after 4 spaces

---

#### Fold-out Info Areas

??? info "HeadlineText"
    Use ```??? info "HeadlineText"```
    
    Text after 4 spaces
