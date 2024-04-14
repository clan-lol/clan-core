# Contributing

**Continuous Integration (CI)**: Each pull request gets automatically tested by gitea. If any errors are detected, it will block pull requests until they're resolved.

**Dependency Management**: We use the [Nix package manager](https://nixos.org/) to manage dependencies and ensure reproducibility, making your development process more robust.

## Supported Operating Systems

- Linux
- macOS

# Getting Started with the Development Environment

Let's get your development environment up and running:

1. **Install Nix Package Manager**:

   - You can install the Nix package manager by either [downloading the Nix installer](https://github.com/DeterminateSystems/nix-installer/releases) or running this command:
     ```bash
     curl --proto '=https' --tlsv1.2 -sSf -L https://install.determinate.systems/nix | sh -s -- install
     ```

2. **Install direnv**:

   - Download the direnv package from [here](https://direnv.net/docs/installation.html) or run the following command:
     ```bash
     curl -sfL https://direnv.net/install.sh | bash
     ```

3. **Add direnv to your shell**:

   - Direnv needs to [hook into your shell](https://direnv.net/docs/hook.html) to work.
     You can do this by executing following command. The example below will setup direnv for `zsh` and `bash`

   ```bash
   echo 'eval "$(direnv hook zsh)"' >> ~/.zshrc && echo 'eval "$(direnv hook bash)"' >> ~/.bashrc && eval "$SHELL"
   ```

4. **Clone the Repository and Navigate**:

   - Clone this repository and navigate to it.

5. **Allow .envrc**:

   - When you enter the directory, you'll receive an error message like this:
     ```bash
     direnv: error .envrc is blocked. Run `direnv allow` to approve its content
     ```
   - Execute `direnv allow` to automatically execute the shell script `.envrc` when entering the directory.

# Setting Up Your Git Workflow

Let's set up your Git workflow to collaborate effectively:

1. **Register Your Gitea Account Locally**:

   - Execute the following command to add your Gitea account locally:
     ```bash
     tea login add
     ```
   - Fill out the prompt as follows:
     - URL of Gitea instance: `https://git.clan.lol`
     - Name of new Login [gitea.gchq.icu]: `gitea.gchq.icu:7171`
     - Do you have an access token? No
     - Username: YourUsername
     - Password: YourPassword
     - Set Optional settings: No

2. **Git Workflow**:

   1. Add your changes to Git using `git add <file1> <file2>`.
   2. Run `nix fmt` to lint your files.
   3. Commit your changes with a descriptive message: `git commit -a -m "My descriptive commit message"`.
   4. Make sure your branch has the latest changes from upstream by executing:
      ```bash
      git fetch && git rebase origin/main --autostash
      ```
   5. Use `git status` to check for merge conflicts.
   6. If conflicts exist, resolve them. Here's a tutorial for resolving conflicts in [VSCode](https://code.visualstudio.com/docs/sourcecontrol/overview#_merge-conflicts).
   7. After resolving conflicts, execute `git merge --continue` and repeat step 5 until there are no conflicts.

3. **Create a Pull Request**:

   - To automatically open a pull request that gets merged if all tests pass, execute:
     ```bash
     merge-after-ci
     ```

4. **Review Your Pull Request**:

   - Visit https://git.clan.lol and go to the project page. Check under "Pull Requests" for any issues with your pull request.

5. **Push Your Changes**:
   - If there are issues, fix them and redo step 2. Afterward, execute:
     ```bash
     git push origin HEAD:YourUsername-main
     ```
   - This will directly push to your open pull request.

# Debugging

Here are some methods for debugging and testing the clan-cli:

## Test Locally in Devshell with Breakpoints

To test the cli locally in a development environment and set breakpoints for debugging, follow these steps:

1. Run the following command to execute your tests and allow for debugging with breakpoints:
   ```bash
   cd ./pkgs/clan-cli
   pytest -n0 -s --maxfail=1 ./tests/test_nameofthetest.py
   ```
   You can place `breakpoint()` in your Python code where you want to trigger a breakpoint for debugging.

## Test Locally in a Nix Sandbox

To run tests in a Nix sandbox, you have two options depending on whether your test functions have been marked as impure or not:

### Running Tests Marked as Impure

If your test functions need to execute `nix build` and have been marked as impure because you can't execute `nix build` inside a Nix sandbox, use the following command:

```bash
nix run .#impure-checks
```

This command will run the impure test functions.

### Running Pure Tests

For test functions that have not been marked as impure and don't require executing `nix build`, you can use the following command:

```bash
nix build .#checks.x86_64-linux.clan-pytest --rebuild
```

This command will run all pure test functions.

### Inspecting the Nix Sandbox

If you need to inspect the Nix sandbox while running tests, follow these steps:

1. Insert an endless sleep into your test code where you want to pause the execution. For example:

   ```python
   import time
   time.sleep(3600)  # Sleep for one hour
   ```

2. Use `cntr` and `psgrep` to attach to the Nix sandbox. This allows you to interactively debug your code while it's paused. For example:

   ```bash
   cntr exec -w your_sandbox_name
   psgrep -a -x your_python_process_name
   ```


# Standards

Every new module name should be in kebab-case.
Every fact definition, where possible should be in kebab-case.
