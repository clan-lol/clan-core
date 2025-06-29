{ lib }:

rec {
  # Extract dependency graph from generators configuration
  # Returns: { generatorName = [ dep1 dep2 ... ]; ... }
  extractDependencyGraph =
    generators: lib.mapAttrs (_name: generator: generator.dependencies or [ ]) generators;

  # Topologically sort generators based on their dependencies
  # Returns: [ "gen1" "gen2" ... ] in dependency order
  toposortGenerators =
    generators:
    let
      depGraph = extractDependencyGraph generators;
      # lib.toposort expects a comparison function where a < b means a should come before b
      # If A depends on B, then B should come before A, so we want B < A
      # This means: B < A if A depends on B
      compareNodes = a: b: builtins.elem a (depGraph.${b} or [ ]);
      sortResult = lib.toposort compareNodes (lib.attrNames generators);
    in
    sortResult.result;

  # Create execution info for a single generator
  # Returns: { name = "gen"; finalScript = ...; inputs = {...}; ... }
  createGenExecInfo =
    generators: allGenerators: name:
    let
      generator = generators.${name};
      # Collect dependency outputs as inputs - look in allGenerators for deps
      depInputs = lib.listToAttrs (
        map (depName: {
          name = depName;
          value = allGenerators.${depName}.files or { };
        }) (generator.dependencies or [ ])
      );
    in
    {
      inherit name;
      finalScript = generator.finalScript;
      dependencies = generator.dependencies or [ ];
      inputs = depInputs;
      files = generator.files or { };
      prompts = generator.prompts or { };
      runtimeInputs = generator.runtimeInputs or [ ];
    };

  # Create execution plan for generators in dependency order
  # Returns: [ { name = "gen1"; finalScript = ...; inputs = {...}; } ... ]
  createExecutionPlan =
    config: allGenerators:
    let
      generators = config.clan.core.vars.generators;
      sortedNames = toposortGenerators generators;
    in
    map (createGenExecInfo generators allGenerators) sortedNames;

  # Generate execution script for a single generator
  generateGeneratorScript = pkgs: genInfo: isShared: ''
    echo "Executing ${if isShared then "shared " else ""}generator: ${genInfo.name}"

    # Create input directory with dependency outputs
    mkdir -p ./inputs/${genInfo.name}
    ${lib.concatStringsSep "\n" (
      lib.mapAttrsToList (depName: depFiles: ''
        mkdir -p ./inputs/${genInfo.name}/${depName}
        ${lib.concatStringsSep "\n" (
          lib.mapAttrsToList (fileName: _: ''
            # Check for dependency in machine-specific outputs first
            if [ -f "./outputs/${depName}/${fileName}" ]; then
              cp "./outputs/${depName}/${fileName}" "./inputs/${genInfo.name}/${depName}/${fileName}"
            # Check for dependency in shared outputs
            elif [ -f "${
              if isShared then "./outputs" else "../../shared/outputs"
            }/${depName}/${fileName}" ]; then
              cp "${
                if isShared then "./outputs" else "../../shared/outputs"
              }/${depName}/${fileName}" "./inputs/${genInfo.name}/${depName}/${fileName}"
            else
              echo "Error: Dependency file ${fileName} not found for generator ${genInfo.name}"
              echo "Current directory: $(pwd)"
              echo "Checked paths:"
              echo "  ./outputs/${depName}/${fileName}"
              echo "  ${if isShared then "./outputs" else "../../shared/outputs"}/${depName}/${fileName}"
              if [ -d "./inputs/${genInfo.name}/${depName}" ]; then
                echo "Input directory contents:"
                ls -la "./inputs/${genInfo.name}/${depName}/"
              fi
              exit 1
            fi
          '') depFiles
        )}
      '') genInfo.inputs
    )}

    # Create prompts directory
    mkdir -p ./prompts/${genInfo.name}
    ${lib.concatStringsSep "\n" (
      lib.mapAttrsToList (promptName: _prompt: ''
        echo "mock-prompt-value-${promptName}" > "./prompts/${genInfo.name}/${promptName}"
      '') genInfo.prompts
    )}

    # Create output directory
    mkdir -p ./outputs/${genInfo.name}

    # Execute finalScript with bubblewrap
    ${pkgs.bubblewrap}/bin/bwrap \
      --dev-bind /dev /dev \
      --proc /proc \
      --tmpfs /tmp \
      --ro-bind /nix/store /nix/store \
      --bind "./inputs/${genInfo.name}" /input \
      --ro-bind "./prompts/${genInfo.name}" /prompts \
      --bind "./outputs/${genInfo.name}" /output \
      --setenv in /input \
      --setenv prompts /prompts \
      --setenv out /output \
      --setenv PATH "${
        lib.makeBinPath (
          (genInfo.runtimeInputs or [ ])
          ++ [
            pkgs.bash
            pkgs.coreutils
          ]
        )
      }" \
      ${pkgs.runtimeShell} ${genInfo.finalScript}

    # Verify expected outputs were created
    ${lib.concatStringsSep "\n" (
      lib.mapAttrsToList (fileName: _fileInfo: ''
        if [ ! -f "./outputs/${genInfo.name}/${fileName}" ]; then
          echo "✗ Expected output file ${fileName} not found for generator ${genInfo.name}"
          exit 1
        else
          echo "✓ Generated ${if isShared then "shared " else ""}file: ${genInfo.name}/${fileName}"
        fi
      '') genInfo.files
    )}

    echo "✓ ${if isShared then "Shared " else ""}Generator ${genInfo.name} completed"
  '';

  # Create machine execution info
  # Returns: { sorted = [ "gen1" "gen2" ... ]; executionPlan = [...]; generators = {...}; }
  createMachineExecInfo = allGenerators: machine: rec {
    sorted = toposortGenerators generators;
    executionPlan = createExecutionPlan { clan.core.vars.generators = generators; } allGenerators;
    generators = lib.filterAttrs (_name: gen: !(gen.share or false)) machine.clan.core.vars.generators;
  };

  # Collect all generators from all machines
  collectAllGenerators =
    nodes:
    lib.foldl' (acc: machine: acc // machine.clan.core.vars.generators) { } (lib.attrValues nodes);

  # Generate shell script for executing generators in dependency order with bubblewrap
  generateExecutionScript =
    pkgs: nodes:
    let
      # Collect all generators from all machines
      allGenerators = collectAllGenerators nodes;

      # Separate shared and per-machine generators
      sharedGenerators = lib.filterAttrs (_name: gen: gen.share or false) allGenerators;

      # Create execution plans
      sharedExecutionPlan =
        if sharedGenerators != { } then
          createExecutionPlan { clan.core.vars.generators = sharedGenerators; } allGenerators
        else
          [ ];

      machineExecutions = lib.mapAttrs (_machineName: createMachineExecInfo allGenerators) nodes;
    in
    ''
      echo "Running vars check using Nix-based executor..."

      # Execute shared generators first
      ${lib.optionalString (sharedGenerators != { }) ''
        echo "Executing shared generators..."
        mkdir -p ./shared
        cd ./shared

        ${lib.concatStringsSep "\n" (
          map (genInfo: generateGeneratorScript pkgs genInfo true) sharedExecutionPlan
        )}

        cd ..
        echo "✓ Shared generators completed"
      ''}

      # Execute generators for each machine in topological order
      ${lib.concatStringsSep "\n" (
        lib.mapAttrsToList (machineName: execInfo: ''
          echo "Processing machine: ${machineName}"
          echo "Generator execution order: ${lib.concatStringsSep " -> " execInfo.sorted}"

          # Create machine-specific work directory
          mkdir -p ./work/${machineName}
          cd ./work/${machineName}

          # Execute each generator in dependency order
          ${lib.concatStringsSep "\n" (
            map (genInfo: generateGeneratorScript pkgs genInfo false) execInfo.executionPlan
          )}

          cd ../..
          echo "✓ Machine ${machineName} completed"

        '') machineExecutions
      )}

      echo "✓ All vars checks completed successfully"
      touch $out
    '';
}
