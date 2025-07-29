import { Accessor, createEffect, createRoot } from "solid-js";
import { MachineRepr } from "./MachineRepr";
import * as THREE from "three";
import { SceneData } from "../stores/clan";
import { MachinesQueryResult } from "../queries/queries";
import { ObjectRegistry } from "./ObjectRegistry";
import { renderLoop } from "./RenderLoop";

function keyFromPos(pos: [number, number]): string {
  return `${pos[0]},${pos[1]}`;
}

const CUBE_SPACING = 2;

export class MachineManager {
  public machines = new Map<string, MachineRepr>();

  private disposeRoot: () => void;

  private machinePositionsSignal: Accessor<SceneData>;

  constructor(
    scene: THREE.Scene,
    registry: ObjectRegistry,
    machinePositionsSignal: Accessor<SceneData>,
    machinesQueryResult: MachinesQueryResult,
    selectedIds: Accessor<Set<string>>,
    setMachinePos: (id: string, position: [number, number]) => void,
  ) {
    this.machinePositionsSignal = machinePositionsSignal;

    this.disposeRoot = createRoot((disposeEffects) => {
      createEffect(() => {
        const machines = machinePositionsSignal();

        Object.entries(machines).forEach(([id, data]) => {
          const machineRepr = new MachineRepr(
            scene,
            registry,
            new THREE.Vector2(data.position[0], data.position[1]),
            id,
            selectedIds,
          );
          this.machines.set(id, machineRepr);
          scene.add(machineRepr.group);
        });
        renderLoop.requestRender();
      });

      // Push positions of previously existing machines to the scene
      // TODO: Maybe we should do this in some post query hook?
      createEffect(() => {
        if (!machinesQueryResult.data) return;

        const actualMachines = Object.keys(machinesQueryResult.data);
        const machinePositions = machinePositionsSignal();
        const placed: Set<string> = machinePositions
          ? new Set(Object.keys(machinePositions))
          : new Set();

        const nonPlaced = actualMachines.filter((m) => !placed.has(m));

        // Push not explizitly placed machines to the scene
        // TODO: Make the user place them manually
        // We just calculate some next free position
        for (const id of nonPlaced) {
          console.log("adding", id);
          const position = this.nextGridPos();

          setMachinePos(id, position);
        }
      });

      return disposeEffects;
    });
  }

  nextGridPos(): [number, number] {
    const occupiedPositions = new Set(
      Object.values(this.machinePositionsSignal()).map((data) =>
        keyFromPos(data.position),
      ),
    );

    let x = 0,
      z = 0;
    let layer = 1;

    while (layer < 100) {
      // right
      for (let i = 0; i < layer; i++) {
        const pos = [x * CUBE_SPACING, z * CUBE_SPACING] as [number, number];
        const key = keyFromPos(pos);
        if (!occupiedPositions.has(key)) {
          return pos;
        }
        x += 1;
      }
      // down
      for (let i = 0; i < layer; i++) {
        const pos = [x * CUBE_SPACING, z * CUBE_SPACING] as [number, number];
        const key = keyFromPos(pos);
        if (!occupiedPositions.has(key)) {
          return pos;
        }
        z += 1;
      }
      layer++;
      // left
      for (let i = 0; i < layer; i++) {
        const pos = [x * CUBE_SPACING, z * CUBE_SPACING] as [number, number];
        const key = keyFromPos(pos);
        if (!occupiedPositions.has(key)) {
          return pos;
        }
        x -= 1;
      }
      // up
      for (let i = 0; i < layer; i++) {
        const pos = [x * CUBE_SPACING, z * CUBE_SPACING] as [number, number];
        const key = keyFromPos(pos);
        if (!occupiedPositions.has(key)) {
          return pos;
        }
        z -= 1;
      }
      layer++;
    }
    console.warn("No free grid positions available, returning [0, 0]");
    // Fallback if no position was found
    return [0, 0] as [number, number];
  }

  dispose(scene: THREE.Scene) {
    for (const machine of this.machines.values()) {
      machine.dispose(scene);
    }
    // Stop SolidJS effects
    this.disposeRoot?.();
    // Clear references
    this.machines?.clear();
  }
}

// TODO: For service focus
// const getCirclePosition =
//   (center: [number, number, number]) =>
//   (_id: string, index: number, total: number): [number, number, number] => {
//     const r = total === 1 ? 0 : Math.sqrt(total) * CUBE_SPACING; // Radius based on total cubes
//     const x = Math.cos((index / total) * 2 * Math.PI) * r + center[0];
//     const z = Math.sin((index / total) * 2 * Math.PI) * r + center[2];
//     // Position cubes at y = 0.5 to float above the ground
//     return [x, CUBE_Y, z];
//   };
