## Developing GTK4 Applications


## Demos
Adw has a demo application showing all widgets. You can run it by executing:
```bash
adwaita-1-demo
```
GTK4 has a demo application showing all widgets. You can run it by executing:
```bash
gtk4-widget-factory
```

To find available icons execute:
```bash
gtk4-icon-browser
```



## Links
- [Adw PyGobject Reference](http://lazka.github.io/pgi-docs/index.html#Adw-1)
- [GTK4 PyGobject Reference](http://lazka.github.io/pgi-docs/index.html#Gtk-4.0)
- [Adw Widget Gallery](https://gnome.pages.gitlab.gnome.org/libadwaita/doc/main/widget-gallery.html)
- [Python + GTK3 Tutorial](https://python-gtk-3-tutorial.readthedocs.io/en/latest/textview.html)



## Debugging Style and Layout

You can append `--debug` flag to enable debug logging printed into the console.

```bash
# Enable the GTK debugger
gsettings set org.gtk.Settings.Debug enable-inspector-keybinding true

# Start the application with the debugger attached
GTK_DEBUG=interactive ./bin/clan-vm-manager --debug
```

## Profiling
To activate profiling execute:
```
PERF=1 ./bin/clan-vm-manager
```