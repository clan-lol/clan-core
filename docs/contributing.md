# Website Template

Welcome to our website template repository! This template is designed to help you and your team build high-quality websites efficiently. We've carefully chosen the technologies to make development smooth and enjoyable. Here's what you can expect from this template:

**Frontend**: Our frontend is powered by [React NextJS](https://nextjs.org/), a popular and versatile framework for building web applications.

**Backend**: For the backend, we use Python along with the [FastAPI framework](https://fastapi.tiangolo.com/). To ensure seamless communication between the frontend and backend, we generate an `openapi.json` file from the Python code, which defines the REST API. This file is then used with [Orval](https://orval.dev/) to generate TypeScript bindings for the REST API. We're committed to code correctness, so we use [mypy](https://mypy-lang.org/) to ensure that our Python code is statically typed correctly. For backend testing, we rely on [pytest](https://docs.pytest.org/en/7.4.x/).

**Continuous Integration (CI)**: We've set up a CI bot that rigorously checks your code using the quality assurance (QA) tools mentioned above. If any errors are detected, it will block pull requests until they're resolved.

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
     You can do this by executing following command:

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

6. **Build the Backend**:

   - Go to the `pkgs/clan-cli` directory and execute:
     ```bash
     direnv allow
     ```
   - Wait for the backend to build.

7. **Start the Backend Server**:

   - To start the backend server, execute:
     ```bash
     clan webui --reload --no-open --log-level debug
     ```
   - The server will automatically restart if any Python files change.

8. **Build the Frontend**:

   - In a different shell, navigate to the `pkgs/ui` directory and execute:
     ```bash
     direnv allow
     ```
   - Wait for the frontend to build.

   NOTE: If you have the error "@clan/colors.json" you executed `npm install`, please do not do that. `direnv reload` will handle dependency management. Please delete node_modules with `rm -rf node_modules`.

9. **Start the Frontend**:
   - To start the frontend, execute:
     ```bash
     npm run dev
     ```
   - Access the website by going to [http://localhost:3000](http://localhost:3000).

# Setting Up Your Git Workflow

Let's set up your Git workflow to collaborate effectively:

1. **Register Your Gitea Account Locally**:

   - Execute the following command to add your Gitea account locally:
     ```bash
     tea login add
     ```
   - Fill out the prompt as follows:
     - URL of Gitea instance: `https://gitea.gchq.icu`
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

   - Visit https://gitea.gchq.icu and go to the project page. Check under "Pull Requests" for any issues with your pull request.

5. **Push Your Changes**:
   - If there are issues, fix them and redo step 2. Afterward, execute:
     ```bash
     git push origin HEAD:YourUsername-main
     ```
   - This will directly push to your open pull request.

# Debugging

When working on the backend of your project, debugging is an essential part of the development process. Here are some methods for debugging and testing the backend of your application:

## Test Backend Locally in Devshell with Breakpoints

To test the backend locally in a development environment and set breakpoints for debugging, follow these steps:

1. Run the following command to execute your tests and allow for debugging with breakpoints:
   ```bash
   pytest -n0 -s --maxfail=1
   ```
   You can place `breakpoint()` in your Python code where you want to trigger a breakpoint for debugging.

## Test Backend Locally in a Nix Sandbox

To run your backend tests in a Nix sandbox, you have two options depending on whether your test functions have been marked as impure or not:

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

### Running schemathesis fuzzer on GET requests

```bash
nix run .#runSchemaTests
```

If you want to test more request types edit the file `checks/impure/flake-module.nix`

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

These debugging and testing methods will help you identify and fix issues in your backend code efficiently, ensuring the reliability and robustness of your application.

For more information on testing read [property and contract based testing](testing.md)

# Using this Template

To make the most of this template:

1. Set up a new Gitea account named `ui-asset-bot`. Generate an access token with all access permissions and set it under `settings/actions/secrets` as a secret called `BOT_ACCESS_TOKEN`.

   - Also, edit the file `.gitea/workflows/ui_assets.yaml` and change the `BOT_EMAIL` variable to match the email you set for that account. Gitea matches commits to accounts by their email address, so this step is essential.

2. Create a second Gitea account named `merge-bot`. Edit the file `pkgs/merge-after-ci/default.nix` if the name should be different. Under "Branches," set the main branch to be protected and add `merge-bot` to the whitelisted users for pushing. Set the unprotected file pattern to `**/ui-assets.nix`.

   - Enable the status check for "build / test (pull_request)."

3. Add both `merge-bot` and `ui-asset-bot` as collaborators.
   - Set the option to "Delete pull request branch after merge by default."
   - Also, set the default merge style to "Rebase then create merge commit."

With this template, you're well-equipped to build and collaborate on high-quality websites efficiently. Happy coding!.
