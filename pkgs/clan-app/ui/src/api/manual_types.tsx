export interface Machine {
  machine: {
    name: string;
    flake: {
      identifier: string;
    };
    override_target_host: string | null;
    private_key: string | null;
  };
}
