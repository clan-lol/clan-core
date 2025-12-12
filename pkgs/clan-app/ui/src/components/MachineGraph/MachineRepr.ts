import * as THREE from "three";
import { ObjectRegistry } from "./ObjectRegistry";
import { createEffect, createRoot } from "solid-js";
import { renderLoop } from "./RenderLoop";
import { TextGeometry } from "three/examples/jsm/geometries/TextGeometry.js";
import { FontLoader } from "three/examples/jsm/loaders/FontLoader.js";
import jsonfont from "three/examples/fonts/helvetiker_regular.typeface.json";
import { Machine } from "@/src/models";

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

export function createMachineMesh() {
  const geometry = new THREE.BoxGeometry(CUBE_SIZE, CUBE_SIZE, CUBE_SIZE);
  const material = new THREE.MeshPhongMaterial({
    color: CUBE_COLOR,
    emissive: CUBE_EMISSIVE,
    shininess: 100,
    transparent: true,
  });

  const cubeMesh = new THREE.Mesh(geometry, material);
  cubeMesh.castShadow = true;
  cubeMesh.receiveShadow = true;
  cubeMesh.name = "cube";
  cubeMesh.position.set(0, CUBE_HEIGHT / 2 + BASE_HEIGHT, 0);

  const { baseMesh, baseMaterial } = createCubeBase(
    BASE_COLOR,
    BASE_EMISSIVE,
    new THREE.BoxGeometry(BASE_SIZE, BASE_HEIGHT, BASE_SIZE),
  );

  return {
    cubeMesh,
    baseMesh,
    baseMaterial,
    geometry,
    material,
  };
}

function createCubeBase(
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
  const baseMesh = new THREE.Mesh(geometry, baseMaterial);
  baseMesh.position.set(0, BASE_HEIGHT / 2, 0);
  baseMesh.receiveShadow = false;
  return { baseMesh, baseMaterial };
}

// Function to build rounded rect shape
function roundedRectShape(w: number, h: number, r: number) {
  const shape = new THREE.Shape();
  const x = -w / 2;
  const y = -h / 2;

  shape.moveTo(x + r, y);
  shape.lineTo(x + w - r, y);
  shape.quadraticCurveTo(x + w, y, x + w, y + r);
  shape.lineTo(x + w, y + h - r);
  shape.quadraticCurveTo(x + w, y + h, x + w - r, y + h);
  shape.lineTo(x + r, y + h);
  shape.quadraticCurveTo(x, y + h, x, y + h - r);
  shape.lineTo(x, y + r);
  shape.quadraticCurveTo(x, y, x + r, y);
  return shape;
}

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
    machine: Machine,
    camera: THREE.Camera,
  ) {
    this.id = machine.id;
    this.camera = camera;

    const { baseMesh, cubeMesh, geometry, material } = createMachineMesh();
    this.cubeMesh = cubeMesh;
    this.cubeMesh.userData = { id: machine.id };

    this.baseMesh = baseMesh;
    this.baseMesh.name = "base";

    this.geometry = geometry;
    this.material = material;

    const label = this.createLabel(machine.id);

    const shadowPlaneMaterial = new THREE.MeshStandardMaterial({
      color: BASE_COLOR,
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
    this.group.userData.id = machine.id;

    this.disposeRoot = createRoot((disposeEffects) => {
      createEffect(() => {
        // Update cube
        (this.cubeMesh.material as THREE.MeshPhongMaterial).color.set(
          machine.isActive ? CUBE_SELECTED_COLOR : CUBE_COLOR,
        );

        // Update base
        (this.baseMesh.material as THREE.MeshPhongMaterial).color.set(
          machine.isActive ? BASE_SELECTED_COLOR : BASE_COLOR,
        );

        // TOOD: Find a different way to show both selected & highlighted
        // I.e. via outline or pulsing
        // selected > highlighted > normal
        (this.baseMesh.material as THREE.MeshPhongMaterial).emissive.set(
          machine.isHighlighted ? HIGHLIGHT_COLOR : 0x000000,
        );

        renderLoop.requestRender();
      });

      return disposeEffects;
    });

    scene.add(this.group);

    registry.add({
      object: this.group,
      id: machine.id,
      type: "machine",
      dispose: () => this.dispose(scene),
    });
  }

  public setPosition(position: THREE.Vector2) {
    this.group.position.set(position.x, 0, position.y);
    renderLoop.requestRender();
  }

  private createLabel(id: string) {
    const group = new THREE.Group();
    // 0x162324
    // const text = new Text();
    // text.text = id;
    // text.font = ttf;
    // text.fontSize = 0.1;
    // text.color = 0xffffff;
    // text.anchorX = "center";
    // text.anchorY = "middle";
    // text.position.set(0, 0, 0.01);
    // text.outlineWidth = 0.005;
    // text.outlineColor = 0x162324;
    //   text.sync(() => {
    //     renderLoop.requestRender();
    //   });

    const textMaterial = new THREE.MeshPhongMaterial({
      color: 0xffffff,
    });
    const textGeo = new TextGeometry(id, {
      font: new FontLoader().parse(jsonfont),
      size: 0.09,
      depth: 0.001,
      curveSegments: 12,
      bevelEnabled: false,
    });

    const text = new THREE.Mesh(textGeo, textMaterial);
    textGeo.computeBoundingBox();

    const bbox = textGeo.boundingBox;
    if (bbox) {
      const xMid = -0.5 * (bbox.max.x - bbox.min.x);
      // const yMid = -0.5 * (bbox.max.y - bbox.min.y);
      // const zMid = -0.5 * (bbox.max.z - bbox.min.z);

      // Translate geometry so center is at origin / baseline aligned with y=0
      textGeo.translate(xMid, -0.035, 0);
    }

    // --- Background (rounded rect) ---
    const padding = 0.04;
    const textWidth = bbox ? bbox.max.x - bbox.min.x : 1;
    const bgWidth = textWidth + 10 * padding;
    // const bgWidth = text.text.length * 0.07 + padding;
    const bgHeight = 0.1 + 2 * padding;
    const radius = 0.02;

    const bgShape = roundedRectShape(bgWidth, bgHeight, radius);
    const bgGeom = new THREE.ShapeGeometry(bgShape);
    const bgMat = new THREE.MeshBasicMaterial({ color: 0x162324 });
    const bg = new THREE.Mesh(bgGeom, bgMat);
    bg.position.set(0, 0, -0.01);

    // --- Arrow (triangle pointing down) ---
    const arrowShape = new THREE.Shape();
    arrowShape.moveTo(-0.05, 0);
    arrowShape.lineTo(0.05, 0);
    arrowShape.lineTo(0, -0.05);
    arrowShape.closePath();

    const arrowGeom = new THREE.ShapeGeometry(arrowShape);
    const arrow = new THREE.Mesh(arrowGeom, bgMat);
    arrow.position.set(0, -bgHeight / 2, -0.001);

    // --- Group ---
    group.add(bg);
    group.add(arrow);
    group.add(text);

    // Position above cube
    group.position.set(0, CUBE_SIZE + 0.3, 0);

    // Billboard
    group.userData.isLabel = true; // Mark as label to receive billboarding update in render loop
    group.quaternion.copy(this.camera.quaternion);

    return group;
  }

  dispose(scene: THREE.Scene) {
    this.disposeRoot?.(); // Stop SolidJS effects

    scene.remove(this.group);

    this.geometry.dispose();
    this.material.dispose();

    this.group.clear();

    for (const child of this.cubeMesh.children) {
      if (child instanceof THREE.Mesh)
        (child.material as THREE.Material).dispose();

      if (child instanceof THREE.Object3D) child.remove();
    }
    (this.baseMesh.material as THREE.Material).dispose();
  }
}
