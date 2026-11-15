{
  # Ensure this is unique among all clans you want to use.
  meta.name = "{{name}}";
  meta.domain = "{{domain}}";

  # Secrets are encrypted with age.
  # Docs: https://clan.lol/docs/unstable/guides/vars/age/age-backend
  vars.settings.secretStore = "age";

  # Age public keys of admins, that can decrypt all secrets of all machines
  # `clan init` adds your key here.
  vars.settings.recipients.default = [
    "{{ageRecipients}}"
  ];

  # Age public keys for individual machines. These replace the default recipient keys for
  # that machine, so list your own key again.
  # vars.settings.recipients.hosts.test-machine = [
  #   "age1..." # your key
  #   "age1..." # e.g. someone who only manages test-machine
  # ];

  # Hardware keys and other plugins
  # https://clan.lol/docs/unstable/guides/vars/sops/age-plugins
  # secrets.age.plugins = [
  #   "age-plugin-yubikey"          YubiKey and other PIV tokens
  #   "age-plugin-tpm"              the machine's TPM 2.0 chip
  #   "github:owner/repo#package"   plugins that are not in nixpkgs, e.g.
  # ];                              https://github.com/pinpox/age-plugin-bip39

  # Every directory in machines/ (e.g. from `clan machines create <name>`) is a
  # machine already. Add an entry here only to give it tags, which instances
  # below select with `roles.<role>.tags`, or to change its class.
  # inventory.machines = {
  #  test-machine = {
  #    tags = [ "server" ];
  #  };
  # };

  inventory.instances = {
    # Docs: https://clan.lol/docs/unstable/services/official/p2p-ssh-iroh
    # Lets `clan ssh` and `clan machines update` reach every machine through
    # iroh, without knowing its IP address and even behind NAT.
    p2p-ssh-iroh.roles.server.tags.all = { };

    # Docs: https://clan.lol/docs/unstable/services/official/internet
    # Connect to servers with a fixed public IP or hostname directly.
    # Does not configure the address on the machine itself.
    # internet.roles.default.machines = {
    #   test-machine.settings.host = "203.0.113.10";
    # };

    # Docs: https://clan.lol/docs/unstable/services/official/sshd
    # Runs sshd with persistent, CA-signed host keys.
    sshd = {
      roles.server.tags.all = { };
      # SSH public keys that may log in as root on all machines.
      roles.server.settings.authorizedKeys = {
        "admin-machine-1" = "PASTE_YOUR_KEY_HERE";
      };
    };

    # Docs: https://clan.lol/docs/unstable/services/official/users
    # Generates a random root password for all machines.
    user-root = {
      module.name = "users";
      roles.default.tags.all = { };
      roles.default.settings.user = "root";
    };
  };
}
