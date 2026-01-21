self.nixosModules.test-install-machine-without-system
->
clan.machines.test-install-machine-without-system <- used by the test via clan flake.nixosConfiguration
->
clan.machines.test-install-machine-${system} <- used by closureInfo
->
checks.*.nixos-test-installation
->
nodes.target
script = ''

''

##
