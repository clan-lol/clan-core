# Clan App

A powerful application that allows users to create and manage their own Clans.

## Getting Started

Enter the `pkgs/clan-app` directory and allow [direnv] to load the `clan-app` devshell with `direnv allow`:

```console
❯ direnv allow
direnv: loading ~/Development/lol/clan/git/clan/clan-core/pkgs/ui/.envrc
direnv: loading ~/Development/lol/clan/git/clan/clan-core/.envrc
direnv: using flake
direnv: nix-direnv: Renewed cache
switch to another dev-shell using: select-shell
direnv: using flake .#ui --builders
path '/home/brian/Development/lol/clan/git/clan/clan-core/pkgs/ui' does not contain a 'flake.nix', searching up
direnv: ([/nix/store/rjnigckx9rmga58562hxw9kr5hynavcd-direnv-2.36.0/bin/direnv export zsh]) is taking a while to execute. Use CTRL-C to give up.
path '/home/brian/Development/lol/clan/git/clan/clan-core/pkgs/ui' does not contain a 'flake.nix', searching up
direnv: nix-direnv: Renewed cache
switch to another dev-shell using: select-shell
/home/brian/.config/direnv/lib/hm-nix-direnv.sh:3858: /home/brian/Development/lol/clan/git/clan/clan-core/pkgs/ui/clan-app/.local.env: No such file or directory
direnv: export +AR +AS +CC +CLAN_CORE_PATH +CONFIG_SHELL +CXX +DETERMINISTIC_BUILD +GETTEXTDATADIRS +GETTEXTDATADIRS_FOR_BUILD +GETTEXTDATADIRS_FOR_TARGET +GIT_ROOT +GSETTINGS_SCHEMAS_PATH +HOST_PATH +IN_NIX_SHELL +LD +NIX_BINTOOLS +NIX_BINTOOLS_WRAPPER_TARGET_HOST_x86_64_unknown_linux_gnu +NIX_BUILD_CORES +NIX_CC +NIX_CC_WRAPPER_TARGET_HOST_x86_64_unknown_linux_gnu +NIX_CFLAGS_COMPILE +NIX_ENFORCE_NO_NATIVE +NIX_HARDENING_ENABLE +NIX_LDFLAGS +NIX_STORE +NM +NODE_PATH +OBJCOPY +OBJDUMP +PC_CONFIG_FILES +PKG_ROOT_CLAN_APP +PKG_ROOT_UI +PKG_ROOT_WEBVIEW_UI +PRJ_ROOT +PYTHONHASHSEED +PYTHONNOUSERSITE +PYTHONPATH +RANLIB +READELF +SIZE +SOURCE_DATE_EPOCH +STRINGS +STRIP +WEBVIEW_LIB_DIR +_PYTHON_HOST_PLATFORM +_PYTHON_SYSCONFIGDATA_NAME +__structuredAttrs +buildInputs +buildPhase +builder +cmakeFlags +configureFlags +depsBuildBuild +depsBuildBuildPropagated +depsBuildTarget +depsBuildTargetPropagated +depsHostHost +depsHostHostPropagated +depsTargetTarget +depsTargetTargetPropagated +doCheck +doInstallCheck +dontAddDisableDepTrack +mesonFlags +name +nativeBuildInputs +out +outputs +patches +phases +preferLocalBuild +propagatedBuildInputs +propagatedNativeBuildInputs +shell +shellHook +stdenv +strictDeps +system ~GDK_PIXBUF_MODULE_FILE ~GI_TYPELIB_PATH ~PATH ~XDG_DATA_DIRS
```

Once that has loaded, you can run the local dev environment by running `process-compose`.

This will start a [process-compose] instance containing two processes:

* `clan-app-ui` which is a background process running a [vite] server for `./ui` in a hot-reload fashion
* `clan-app` which is a [foreground process](https://f1bonacc1.github.io/process-compose/launcher/?h=foreground#foreground-processes),
that is started on demand and provides the [webview] wrapper for the UI.

Wait for the `clan-app-ui` process to enter the `Running` state, then navigate to the `clan-app` process and press `F7`.
This will start the [webview] window and bring `clan-app`'s terminal into the foreground, allowing for interaction with
the debugger if required.

If you need to restart, simply enter `ctrl+c` and you will be dropped back into the `process-compose` terminal.
From there you can start `clan-app` again with `F7`.

> **Note**
> If you are interacting with a breakpoint, do not continue/exit with `ctrl+c` as this will introduce a quirk
> the next time you start `clan-app` where you will be unable to see the input you are typing in a debugging session.
>
> Instead, exit the debugger with `q+Enter`.

Follow the instructions below to set up your development environment and start the application:


## Start clan-app without process-compose


1. **Navigate to the Webview UI Directory**

   Go to the `clan-core/pkgs/clan-app/ui` directory and start the web server by executing:

   ```bash
   npm install
   vite
   ```

2. **Start the Clan App**

   In the `clan-core/pkgs/clan-app` directory, execute the following command:

   ```bash
   ./bin/clan-app --debug --content-uri http://localhost:3000
   ```

This will start the application in debug mode and link it to the web server running at `http://localhost:3000`.

### Debugging Style and Layout

```bash
# Enable the GTK debugger
gsettings set org.gtk.Settings.Debug enable-inspector-keybinding true

# Start the application with the debugger attached
GTK_DEBUG=interactive ./bin/clan-app --debug
```

Appending `--debug` flag enables debug logging printed into the console.

### Profiling

To activate profiling you can run

```bash
CLAN_CLI_PERF=1 ./bin/clan-app
```

### Library Components

> Note:
>
> we recognized bugs when starting some cli-commands through the integrated vs-code terminal.
> If encountering issues make sure to run commands in a regular os-shell.

lib-Adw has a demo application showing all widgets. You can run it by executing

```bash
adwaita-1-demo
```

GTK4 has a demo application showing all widgets. You can run it by executing

```bash
gtk4-widget-factory
```

To find available icons execute

```bash
gtk4-icon-browser
```

### Links

Here are some important documentation links related to the Clan App:

- [GTK4 PyGobject Reference](http://lazka.github.io/pgi-docs/index.html#Gtk-4.0): This link provides the PyGObject reference documentation for GTK4, the toolkit used for building the user interface of the clan app. It includes information about GTK4 widgets, signals, and other features.

- [Adw Widget Gallery](https://gnome.pages.gitlab.gnome.org/libadwaita/doc/main/widget-gallery.html): This link showcases a widget gallery for Adw, allowing you to see the available widgets and their visual appearance. It can be helpful for designing the user interface of the clan app.

- [GNOME Human Interface Guidelines](https://developer.gnome.org/hig/): This link provides the GNOME Human Interface Guidelines, which offer design and usability recommendations for creating GNOME applications. It covers topics such as layout, navigation, and interaction patterns.

## Error handling

> Error dialogs should be avoided where possible, since they are disruptive.
>
> For simple non-critical errors, toasts can be a good alternative.


[direnv]: https://direnv.net/
[process-compose]: https://f1bonacc1.github.io/process-compose/
[vite]: https://vite.dev/
[webview]: https://github.com/webview/webview
