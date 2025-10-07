This guide explains how to set up a [Hetzner Storage Box](https://docs.hetzner.com/storage/storage-box/general) as a backup destination instead of using an internal Clan backup server. Follow the steps below to configure and verify the setup.

### Step 1: Create a Hetzner Storage Box

Begin by [creating a Hetzner Storage Box account](https://docs.hetzner.com/storage/storage-box/getting-started/creating-a-storage-box).

### Step 2: Create a Sub-Account

Set up a sub-account for your `jon` machine. Save the SSH password for this account in your password manager for future reference.

### Step 3: Configure BorgBackup in `clan.nix`

Add the BorgBackup service to your `clan.nix` configuration. In this example, the `jon` machine will back up to `user-sub1@user-sub1.your-storagebox.de` in the `borgbackup` folder:

```nix hl_lines="9"
inventory.instances = {
  borgbackup = {
    module = {
      name = "borgbackup";
      input = "clan-core";
    };
    roles.client.machines."jon".settings = {
      destinations."storagebox" = {
        repo = "user-sub1@user-sub1.your-storagebox.de:/./borgbackup";
        rsh = ''ssh -p 23 -oStrictHostKeyChecking=accept-new -i /run/secrets/vars/borgbackup/borgbackup.ssh'';
      };
    };
  };
};
```

### Step 4: Generate SSH Keys

Run the following command to generate the SSH private keys:

```bash
clan vars generate
```

### Step 5: Add the Public Key to the Sub-Account

Add the generated SSH public key to the `user-sub1` account by running:

```bash
clan vars get jon borgbackup/borgbackup.ssh.pub | ssh -p23 user-sub1@user-sub1.your-storagebox.de install-ssh-key
```

### Step 6: Deploy the Configuration

Apply the changes to your Clan setup by executing:

```bash
clan machines update
```

### Step 7: Verify the Setup

Check if the configuration works by starting the BorgBackup service on the `jon` machine:

```bash
systemctl start borgbackup-job-storagebox.service &
```

Then, inspect the service logs to ensure everything is functioning correctly:

```bash
journalctl -u borgbackup-job-storagebox.service
```



