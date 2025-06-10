# agit

A helper script for the AGit workflow with a gitea instance.

<!-- `$ agit --help` -->

```
usage: agit [-h] {create,c} ...

AGit utility for creating and pulling PRs

positional arguments:
  {create,c}    Commands
    create (c)  Create an AGit PR

options:
  -h, --help    show this help message and exit

The defaults that are assumed are:
TARGET_REMOTE_REPOSITORY = origin
DEFAULT_TARGET_BRANCH = main

Examples:
  $ agit create
  Will create an AGit Pr with the latest commit message title as it's topic.

  $ agit create --topic "my-feature"
  Set a custom topic.

  $ agit create --force
  Force push to a certain topic
        
```

References:
- https://docs.gitea.com/usage/agit
- https://git-repo.info/en/2020/03/agit-flow-and-git-repo/
