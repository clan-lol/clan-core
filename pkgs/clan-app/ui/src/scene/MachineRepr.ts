import * as THREE from "three";
import { ObjectRegistry } from "./ObjectRegistry";
import { CSS2DObject } from "three/examples/jsm/renderers/CSS2DRenderer.js";
import { Accessor, createEffect, createRoot, on } from "solid-js";
import { renderLoop } from "./RenderLoop";

// Constants
const BASE_SIZE = 0.9;
const CUBE_SIZE = BASE_SIZE / 1.5;
const CUBE_HEIGHT = CUBE_SIZE;
const BASE_HEIGHT = 0.05;
const CUBE_COLOR = 0xe2eff0;
const CUBE_EMISSIVE = 0x303030;

const CUBE_SELECTED_COLOR = 0x4b6767;

const BASE_COLOR = 0xdbeaeb;
const BASE_EMISSIVE = 0x0c0c0c;
const BASE_SELECTED_COLOR = 0x69b0e3;
const BASE_SELECTED_EMISSIVE = 0x666666; // Emissive color for selected bases

export class MachineRepr {
  public id: string;
  public group: THREE.Group;

  private cubeMesh: THREE.Mesh;
  private baseMesh: THREE.Mesh;
  private geometry: THREE.BoxGeometry;
  private material: THREE.MeshPhongMaterial;

  private disposeRoot: () => void;

  constructor(
    scene: THREE.Scene,
    registry: ObjectRegistry,
    position: THREE.Vector2,
    id: string,
    selectedSignal: Accessor<Set<string>>,
  ) {
    this.id = id;
    this.geometry = new THREE.BoxGeometry(CUBE_SIZE, CUBE_SIZE, CUBE_SIZE);
    this.material = new THREE.MeshPhongMaterial({
      color: CUBE_COLOR,
      emissive: CUBE_EMISSIVE,
      shininess: 100,
    });

    this.cubeMesh = new THREE.Mesh(this.geometry, this.material);
    this.cubeMesh.castShadow = true;
    this.cubeMesh.receiveShadow = true;
    this.cubeMesh.userData = { id };
    this.cubeMesh.name = "cube";
    this.cubeMesh.position.set(0, CUBE_HEIGHT / 2 + BASE_HEIGHT, 0);

    this.baseMesh = this.createCubeBase(
      BASE_COLOR,
      BASE_EMISSIVE,
      new THREE.BoxGeometry(BASE_SIZE, BASE_HEIGHT, BASE_SIZE),
    );
    this.baseMesh.name = "base";

    const label = this.createLabel(id);
    this.cubeMesh.add(label);

    const shadowPlaneMaterial = new THREE.MeshStandardMaterial({
      color: BASE_COLOR, // any color you like
      roughness: 1,
      metalness: 0,
      transparent: true,
      opacity: 0.4,
    });

    const shadowPlane = new THREE.Mesh(
      new THREE.PlaneGeometry(BASE_SIZE, BASE_SIZE),
      shadowPlaneMaterial,
    );

    shadowPlane.receiveShadow = true;
    shadowPlane.rotation.x = -Math.PI / 2;
    shadowPlane.position.set(0, BASE_HEIGHT + 0.0001, 0);

    this.group = new THREE.Group();
    this.group.add(this.cubeMesh);
    this.group.add(this.baseMesh);
    this.group.add(shadowPlane);

    this.group.position.set(position.x, 0, position.y);
    this.group.userData.id = id;

    this.disposeRoot = createRoot((disposeEffects) => {
      createEffect(
        on(selectedSignal, (selectedIds) => {
          const isSelected = selectedIds.has(this.id);
          // Update cube
          (this.cubeMesh.material as THREE.MeshPhongMaterial).color.set(
            isSelected ? CUBE_SELECTED_COLOR : CUBE_COLOR,
          );

          // Update base
          (this.baseMesh.material as THREE.MeshPhongMaterial).color.set(
            isSelected ? BASE_SELECTED_COLOR : BASE_COLOR,
          );
          (this.baseMesh.material as THREE.MeshPhongMaterial).emissive.set(
            isSelected ? BASE_SELECTED_EMISSIVE : BASE_EMISSIVE,
          );

          renderLoop.requestRender();
        }),
      );

      return disposeEffects;
    });

    scene.add(this.group);

    registry.add({
      object: this.group,
      id,
      type: "machine",
      dispose: () => this.dispose(scene),
    });
  }

  private createCubeBase(
    color: THREE.ColorRepresentation,
    emissive: THREE.ColorRepresentation,
    geometry: THREE.BoxGeometry,
  ) {
    const baseMaterial = new THREE.MeshPhongMaterial({
      color,
      emissive,
      transparent: true,
      opacity: 1,
    });
    const base = new THREE.Mesh(geometry, baseMaterial);
    base.position.set(0, BASE_HEIGHT / 2, 0);
    base.receiveShadow = false;
    return base;
  }

  private createLabel(id: string) {
    const div = document.createElement("div");
    div.className = "machine-label";
    div.textContent = id;
    const label = new CSS2DObject(div);
    label.position.set(0, CUBE_SIZE + 0.1, 0);
    return label;
  }

  dispose(scene: THREE.Scene) {
    this.disposeRoot?.(); // Stop SolidJS effects

    scene.remove(this.group);

    this.geometry.dispose();
    this.material.dispose();
    (this.baseMesh.material as THREE.Material).dispose();
  }
}
