# Backups

When self-hosting services, it's important to have a robust backup and restore strategy.
Therefore clan comes with a backup integration based on [borgbackup](https://www.borgbackup.org/).
More backup backends may come in future as clan provides an interchangeable interface on top of the backup implementation.

# Getting started with borgbackup

Borgbackup consists of two components a backup repository that can be hosted on one machine and contains the backup
and a backup client that will push it's data to the backup repository.

## Borgbackup client

First you need to specify the remote server to backup to. Replace `hostname` with a reachable dns or ip address.

```nix
{
  clan.borgbackup.destinations = {
    myhostname = {
      repo = "borg@hostname:/var/lib/borgbackup/myhostname";
    };
  };
}
```

Services in clan can specify custom folders that need a backup by setting `clanCore.state.<service>.folders` option.
As a user you can also append to the list by adding your own directories to be backed up i.e.:

```nix
{ clanCore.state.userdata.folders = [ "/home" "/root" ]; }
```

Than run `clan secrets generate <yourmachine>` replacing `<yourmachine>` with the actual machine name.
This will generate the backup borg credentials and ssh keys for accessing the borgbackup repository.
Your ssh public key will be stored in the root of the repository here at this location `./machines/<yourmachine>/facts/borgbackup.ssh.pub`.
We need this for the next step.

## Borgbackup repository

In the next step we are going to set up the backup server.
Choose here a machine with sufficient disk space.
The machine needs to have the ssh daemon enabled as it is used in borgbackup for accessing the backup repository.
Add the following configuration to your backup server:

```nix
{
  openssh.services.enable = true;
  services.borgbackup.repos = {
    myhostname = {
      path = "/var/lib/borgbackup/myhostname";
      authorizedKeys = [
        (builtins.readFile ./machines/myhostname/facts/borgbackup.ssh.pub)
      ];
    };
  };
}
```

Replace `myhostname` with the name of the machine you want to backup. The path to the public key needs to be relative to the
configuration file, so you may have to adapt it if the configuration is not in the root directory of your clan flake.

Afterwards run `clan machines update` to update both the borgbackup server and the borgbackup client.

By default the backup is scheduled every night at 01:00 midnight. If machines are not online around this time,
they will attempt to run the backup once they come back.

When the next backup is scheduled, can be inspected like this on the device:

```
$ systemctl list-timers | grep -E 'NEXT|borg'
NEXT                                   LEFT LAST                              PASSED UNIT                               ACTIVATES
Thu 2024-03-14 01:00:00 CET             17h Wed 2024-03-13 01:00:00 CET       6h ago borgbackup-job-myhostname.timer borgbackup-job-myhostname.service
```

```

```


