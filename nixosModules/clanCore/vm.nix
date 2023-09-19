{ config, options, lib, ... }: {
  system.clan.vm.config = {
    enabled = options.virtualisation ? cores;
  } // (lib.optionalAttrs (options.virtualisation ? cores) {
    inherit (config.virtualisation) cores graphics;
    memory_size = config.virtualisation.memorySize;
  });
}
