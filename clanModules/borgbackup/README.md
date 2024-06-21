Efficient, deduplicating backup program with optional compression and secure encryption.
---

## Roles

- Client
- Server

## Configuration

Configure target machines where the backups should be sent to through `targets`.

Configure machines that should be backed up either through `includeMachines`
which will exclusively add the included machines to be backed up, or through
`excludeMachines`, which will add every machine except the excluded machine to the backup.
