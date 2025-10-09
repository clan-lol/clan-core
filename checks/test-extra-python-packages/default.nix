(
  { ... }:
  {
    name = "test-extra-python-packages";

    extraPythonPackages = ps: [ ps.numpy ];

    nodes.machine =
      { ... }:
      {
        networking.hostName = "machine";
      };

    testScript = ''
      import numpy as np

      start_all()
      machine.wait_for_unit("multi-user.target")

      # Test availability of numpy
      arr = np.array([1, 2, 3])
      print(f"Numpy array: {arr}")
      assert len(arr) == 3
    '';
  }
)
