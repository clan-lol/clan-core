

In this section we go over how to manage your collection of backups with the clan command.

### Listing states

To see which files (`states`) will be backed up on a specific machine, use:

```bash
clan state list jon
```

This will show all configured states for the machine `jon`, for example:

```text
· service: linkding
  folders:
  - /var/backup/linkding
  preBackupCommand: pre-backup-linkding
  postRestoreCommand: post-restore-linkding

· service: zerotier
  folders:
  - /var/lib/zerotier-one
```

### Creating backups

To create a backup of a machine (e.g., `jon`), run:

```bash
clan backups create jon
```

This will backup all configured states (`zerotier` and `linkding` in this
example) from the machine `jon`.

### Listing available backups

To see all available backups, use:

```bash
clan backups list
```

This will display all backups with their timestamps:

```text
storagebox::username@username.your-storagebox.de:/./borgbackup::jon-jon-2025-07-22T19:40:10
storagebox::username@username.your-storagebox.de:/./borgbackup::jon-jon-2025-07-23T01:00:00
storagebox::username@username.your-storagebox.de:/./borgbackup::jon-storagebox-2025-07-24T01:00:00
storagebox::username@username.your-storagebox.de:/./borgbackup::jon-storagebox-2025-07-24T06:02:35
```

### Restoring backups

For restoring a backup you have two options.

#### Full restoration

To restore all services from a backup:

```bash
clan backups restore jon borgbackup storagebox::u444061@u444061.your-storagebox.de:/./borgbackup::jon-storagebox-2025-07-24T06:02:35
```

#### Partial restoration

To restore only a specific service (e.g., `linkding`):

```bash
clan backups restore --service linkding jon borgbackup storagebox::u444061@u444061.your-storagebox.de:/./borgbackup::jon-storagebox-2025-07-24T06:02:35
```


