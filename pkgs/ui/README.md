# Clan UI

## Getting started

Enter the `pkgs/ui` directory and allow [direnv] to load the `ui` devshell with `direnv allow`:

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

* `webview-ui` which is a background process running a [vite] server for `./webview-ui` in a hot-reload fashion
* `clan-app` which is a [foreground process](https://f1bonacc1.github.io/process-compose/launcher/?h=foreground#foreground-processes),
that is started on demand and provides the [webview] wrapper for the UI.

Wait for the `webview-ui` process to enter the `Running` state, then navigate to the `clan-app` process and press `F7`. 
This will start the [webview] window and bring `clan-app`'s terminal into the foreground, allowing for interaction with
the debugger if required. 

If you need to restart, simply enter `ctrl+c` and you will be dropped back into the `process-compose` terminal. 
From there you can start `clan-app` again with `F7`.

> **Note**
> If you are interacting with a breakpoint, do not continue/exit with `ctrl+c` as this will introduce a quirk
> the next time you start `clan-app` where you will be unable to see the input you are typing in a debugging session. 
>
> Instead, exit the debugger with `q+Enter`. 

[direnv]: https://direnv.net/
[process-compose]: https://f1bonacc1.github.io/process-compose/
[vite]: https://vite.dev/ 
[webview]: https://github.com/webview/webview