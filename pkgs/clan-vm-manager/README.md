## Developing GTK3 Applications

Here we will document on how to develop GTK3 application UI in python. First we want to setup
an example code base to look into. In this case gnome-music.

## Setup gnome-music as code reference

gnome-music does not use glade

Clone gnome-music and check out the tag v40.0
[gnome-music](https://github.com/GNOME/gnome-music/tree/40.0)

```bash
git clone git@github.com:GNOME/gnome-music.git && cd gnome-music && git checkout 40.0
```

Checkout nixpkgs version `468cb5980b56d348979488a74a9b5de638400160` for the correct gnome-music devshell then execute:

```bash

nix develop /home/username/Projects/nixpkgs#gnome.gnome-music
```

Look into the file `gnome-music.in` which bootstraps the application.

## Setup gnu-cash as reference

Gnucash uses glade with complex UI
Setup gnucash

```bash
git clone git@github.com:Gnucash/gnucash.git
git checkout ed4921271c863c7f6e0c800e206b25ac6e9ba4da

cd nixpkgs
git checkout 015739d7bffa7da4e923978040a2f7cba6af3270
nix develop /home/username/Projects/nixpkgs#gnucash
mkdir build && cd build
cmake ..
cd ..
make
```

- The use the GTK Builder instead of templates.

## Look into virt-manager it uses python + spice-gtk

Look into `virtManager/details/viewers.py` to see how spice-gtk is being used

```bash
git clone https://github.com/virt-manager/virt-manager

```

### Glade

Make sure to check the 'composit' box in glade in the GtkApplicationWindow to be able to
import the glade file through GTK template

## Links

- Another python glade project [syncthing-gtk](https://github.com/kozec/syncthing-gtk)

- Other python glade project [linuxcnc](https://github.com/podarok/linuxcnc/tree/master)

- Install [Glade UI Toolbuilder](https://gitlab.gnome.org/GNOME/glade)

- To understand GTK3 Components look into the [Python GTK3 Tutorial](https://python-gtk-3-tutorial.readthedocs.io/en/latest/search.html?q=ApplicationWindow&check_keywords=yes&area=default)

- Also look into [PyGObject](https://pygobject.readthedocs.io/en/latest/guide/gtk_template.html) to know more about threading and async etc.
- [GI Python API](https://lazka.github.io/pgi-docs/#Gtk-3.0)
- https://developer.gnome.org/documentation/tutorials/application.html
- [GTK3 Python] https://github.com/sam-m888/python-gtk3-tutorial/tree/master

## My gripes with GTK

- Registered the signal in the wrong component? Oh then self.application() returns None!
- Want to quit the Gtk App? Gtk.main_quit() does not work anymore if more than one Window is there, instead use `Gio.Application.quit(self.get_application())` duh! Is this documented anywhere? No? Ah well must be a monday!
- Want to know which functions you can call on an Gtk.Application object? Then look into [Gtk.Application](https://lazka.github.io/pgi-docs/#Gtk-3.0/classes/Application.html#Gtk.Application) object and try the `get_windows()` function in Python! Oops doesn't exit, must be a Monday!
