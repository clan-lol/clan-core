import * as THREE from "three";
import { ObjectRegistry } from "./ObjectRegistry";
import { CSS2DObject } from "three/examples/jsm/renderers/CSS2DRenderer.js";
import { Accessor, createEffect, createRoot, on } from "solid-js";
import { renderLoop } from "./RenderLoop";
// @ts-expect-error: No types for troika-three-text
import { Text } from "troika-three-text";
import ttf from "../../.fonts/CommitMonoV143-VF.ttf";

// Constants
const BASE_SIZE = 0.9;
const CUBE_SIZE = BASE_SIZE / 1.5;
const CUBE_HEIGHT = CUBE_SIZE;
const BASE_HEIGHT = 0.05;
const CUBE_COLOR = 0xe2eff0;
const CUBE_EMISSIVE = 0x303030;

const CUBE_SELECTED_COLOR = 0x4b6767;
const HIGHLIGHT_COLOR = 0x00ee66;

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
  private camera: THREE.Camera;

  private disposeRoot: () => void;

  constructor(
    scene: THREE.Scene,
    registry: ObjectRegistry,
    position: THREE.Vector2,
    id: string,
    selectedSignal: Accessor<Set<string>>,
    highlightGroups: Record<string, Set<string>>, // Reactive store
    camera: THREE.Camera,
  ) {
    this.id = id;
    this.camera = camera;
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
    this.group.add(label);
    this.group.add(this.cubeMesh);
    this.group.add(this.baseMesh);
    this.group.add(shadowPlane);

    this.group.position.set(position.x, 0, position.y);
    this.group.userData.id = id;

    this.disposeRoot = createRoot((disposeEffects) => {
      createEffect(
        on(
          [selectedSignal, () => Object.entries(highlightGroups)],
          ([selectedIds, groups]) => {
            const isSelected = selectedIds.has(this.id);
            const highlightedGroups = groups
              .filter(([, ids]) => ids.has(this.id))
              .map(([name]) => name);

            // console.log("MachineRepr effect", id, highlightedGroups);
            // Update cube
            (this.cubeMesh.material as THREE.MeshPhongMaterial).color.set(
              isSelected ? CUBE_SELECTED_COLOR : CUBE_COLOR,
            );

            // Update base
            (this.baseMesh.material as THREE.MeshPhongMaterial).color.set(
              isSelected ? BASE_SELECTED_COLOR : BASE_COLOR,
            );

            // TOOD: Find a different way to show both selected & highlighted
            // I.e. via outline or pulsing
            // selected > highlighted > normal
            (this.baseMesh.material as THREE.MeshPhongMaterial).emissive.set(
              highlightedGroups.length > 0 ? HIGHLIGHT_COLOR : 0x000000,
            );
            // (this.baseMesh.material as THREE.MeshPhongMaterial).emissive.set(
            //   isSelected ? BASE_SELECTED_EMISSIVE : BASE_EMISSIVE,
            // );

            renderLoop.requestRender();
          },
        ),
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

  public setPosition(position: THREE.Vector2) {
    this.group.position.set(position.x, 0, position.y);
    renderLoop.requestRender();
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
    const text = new Text();
    text.text = id;
    text.font = ttf;
    // text.font = ".fonts/CommitMonoV143-VF.woff2"; // <-- normal web font, not JSON
    text.fontSize = 0.15; // relative to your cube size
    text.color = 0x000000; // any THREE.Color
    text.anchorX = "center"; // horizontal centering
    text.anchorY = "bottom"; // baseline aligns to cube top
    text.position.set(0, CUBE_SIZE + 0.05, 0);

    // If you want it to always face camera:
    text.userData.isLabel = true;
    text.outlineWidth = 0.005;
    text.outlineColor = 0x333333;
    text.quaternion.copy(this.camera.quaternion);

    // Re-render on text changes
    text.sync(() => {
      renderLoop.requestRender();
    });
    return text;
  }

  dispose(scene: THREE.Scene) {
    this.disposeRoot?.(); // Stop SolidJS effects

    scene.remove(this.group);

    this.geometry.dispose();
    this.material.dispose();
    for (const child of this.cubeMesh.children) {
      if (child instanceof THREE.Mesh)
        (child.material as THREE.Material).dispose();

      if (child instanceof CSS2DObject) child.element.remove();

      if (child instanceof THREE.Object3D) child.remove();
    }
    (this.baseMesh.material as THREE.Material).dispose();
  }
}
