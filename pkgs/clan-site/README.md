# Clan Site

This is the source code for the whole clan site. It includes the home page, the blog, the documentation etc.

## Developing

To start the dev server

```sh
clan-site
```

This is same as running `clan-site dev`.

Add `-b` to open the site in a new browser tab

```sh
clan-site dev -b
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

## Lint

Clan Site uses a quite strict coding standard. To lint the code base, run

```sh
clan-site lint
```

## Lint

Clan Site uses a quite strict coding standard. To lint the code base, run

```sh
clan-site lint
```

To auto-fix the lint errors: run

```sh
clan-site lint --fix
```

## Pagefind Playground

Pagefind offers a playground page that allows experimenting with different parameters that affect the order of search results. This page is only available in dev mode (started by `clan-site` or `clan-site dev`), and is available at:

```
/_pagefind/docs/playground/index.html
```
