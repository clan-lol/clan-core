# agit

A helper script for the AGit workflow with a gitea instance.

<!-- `$ agit --help` -->

```
usage: agit [-h] {create,c,list,l} ...

AGit utility for creating and pulling PRs

positional arguments:
  {create,c,list,l}  Commands
    create (c)       Create an AGit PR
    list (l)         List open AGit pull requests

options:
  -h, --help         show this help message and exit

The defaults that are assumed are:
TARGET_REMOTE_REPOSITORY = origin
DEFAULT_TARGET_BRANCH = main

Examples:
  $ agit create
  Opens editor to compose PR title and description (first line is title, rest is body)

  $ agit create --auto
  Creates PR using latest commit message automatically

  $ agit create --topic "my-feature"
  Set a custom topic.

  $ agit create --force
  Force push to a certain topic

  $ agit list
  Lists all open pull requests for the current repository
        
```

References:
- https://docs.gitea.com/usage/agit
- https://git-repo.info/en/2020/03/agit-flow-and-git-repo/
