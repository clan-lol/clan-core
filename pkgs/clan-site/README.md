# Clan Site

This is the source code for the whole clan site. It includes the home page, the blog, the documentation etc.

## Developing

To start the dev server

```sh
clan-site
```

Add `-b` to open the site in a new browser tab

```sh
clan-site -b
```

## Building

To create a production version of the site:

```sh
clan-site build
```

Add `-s` to preview the build result

```sh
clan-site build -s
```

Similarly, passing `-b` (which assumes `-s`) opens the build result in a new browser tab.

```sh
clan-site build -b
```
