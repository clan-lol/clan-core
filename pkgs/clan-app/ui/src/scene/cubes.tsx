import {
  createSignal,
  createEffect,
  onCleanup,
  onMount,
  createMemo,
  on,
} from "solid-js";
import "./cubes.css";

import * as THREE from "three";
import { MapControls } from "three/examples/jsm/controls/MapControls.js";
import {
  CSS2DRenderer,
  CSS2DObject,
} from "three/examples/jsm/renderers/CSS2DRenderer.js";

import { Toolbar } from "../components/Toolbar/Toolbar";
import { ToolbarButton } from "../components/Toolbar/ToolbarButton";
import { Divider } from "../components/Divider/Divider";
import { MachinesQueryResult } from "../queries/queries";
import { SceneData } from "../stores/clan";
import { unwrap } from "solid-js/store";
import { Accessor } from "solid-js";
import { renderLoop } from "./RenderLoop";

function garbageCollectGroup(group: THREE.Group) {
  for (const child of group.children) {
    if (child instanceof THREE.Mesh) {
      child.geometry.dispose();
      if (Array.isArray(child.material)) {
        child.material.forEach((material) => material.dispose());
      } else {
        child.material.dispose();
      }
    } else {
      console.warn("Unknown child type in group:", child);
    }
  }
  group.clear(); // Clear the group
}

function getFloorPosition(
  camera: THREE.Camera,
  floor: THREE.Object3D,
): [number, number, number] {
  const cameraPosition = camera.position.clone();

  // Get camera's direction
  const direction = new THREE.Vector3();
  camera.getWorldDirection(direction);

  // Define floor plane (XZ-plane at y=0)
  const floorPlane = new THREE.Plane(new THREE.Vector3(0, 1, 0), 0); // Normal = up, constant = 0

  // Create ray from camera
  const ray = new THREE.Ray(cameraPosition, direction);

  // Get intersection point
  const intersection = new THREE.Vector3();
  ray.intersectPlane(floorPlane, intersection);

  return intersection.toArray() as [number, number, number];
}

function keyFromPos(pos: [number, number]): string {
  return `${pos[0]},${pos[1]}`;
}

// type SceneDataUpdater = (sceneData: SceneData) => void;

export function CubeScene(props: {
  cubesQuery: MachinesQueryResult;
  onCreate: () => Promise<{ id: string }>;
  selectedIds: Accessor<Set<string>>;
  onSelect: (v: Set<string>) => void;
  sceneStore: Accessor<SceneData>;
  setMachinePos: (machineId: string, pos: [number, number]) => void;
  isLoading: boolean;
}) {
  let container: HTMLDivElement;
  let scene: THREE.Scene;
  let camera: THREE.OrthographicCamera;
  let renderer: THREE.WebGLRenderer;
  let labelRenderer: CSS2DRenderer;
  let floor: THREE.Mesh;
  let controls: MapControls;
  // Raycaster for clicking
  const raycaster = new THREE.Raycaster();
  let initBase: THREE.Mesh | undefined;

  // Create background scene
  const bgScene = new THREE.Scene();
  const bgCamera = new THREE.OrthographicCamera(-1, 1, 1, -1, 0, 1);

  const groupMap = new Map<string, THREE.Group>();

  const occupiedPositions = new Set<string>();

  let sharedCubeGeometry: THREE.BoxGeometry;
  let sharedBaseGeometry: THREE.BoxGeometry;

  const [positionMode, setPositionMode] = createSignal<"grid" | "circle">(
    "grid",
  );

  const [worldMode, setWorldMode] = createSignal<"view" | "create">("view");

  const [cursorPosition, setCursorPosition] = createSignal<[number, number]>();

  const [cameraInfo, setCameraInfo] = createSignal({
    position: { x: 0, y: 0, z: 0 },
    spherical: { radius: 0, theta: 0, phi: 0 },
  });

  // Animation configuration
  const ANIMATION_DURATION = 800; // milliseconds

  // Grid configuration
  const GRID_SIZE = 2;
  const CUBE_SPACING = 2;

  const BASE_SIZE = 0.9; // Height of the cube above the ground
  const CUBE_SIZE = BASE_SIZE / 1.5; //
  const BASE_HEIGHT = 0.05; // Height of the cube above the ground
  const CUBE_Y = 0 + CUBE_SIZE / 2 + BASE_HEIGHT / 2; // Y position of the cube above the ground
  const CUBE_SEGMENT_HEIGHT = CUBE_SIZE / 1;

  const FLOOR_COLOR = 0xcdd8d9;

  const CUBE_COLOR = 0xd7e0e1;
  const CUBE_EMISSIVE = 0x303030; // Emissive color for cubes

  const CUBE_SELECTED_COLOR = 0x4b6767;

  const BASE_COLOR = 0xecfdff;
  const BASE_EMISSIVE = 0x0c0c0c;
  const BASE_SELECTED_COLOR = 0x69b0e3;
  const BASE_SELECTED_EMISSIVE = 0x666666; // Emissive color for selected bases

  const CREATE_BASE_COLOR = 0x636363;
  const CREATE_BASE_EMISSIVE = 0xc5fad7;

  createEffect(() => {
    // Update when API updates.
    if (props.cubesQuery.data) {
      const actualMachines = Object.keys(props.cubesQuery.data);
      const rawStored = unwrap(props.sceneStore());
      const placed: Set<string> = rawStored
        ? new Set(Object.keys(rawStored))
        : new Set();
      const nonPlaced = actualMachines.filter((m) => !placed.has(m));

      // Initialize occupied positions from previously placed cubes
      for (const id of placed) {
        occupiedPositions.add(keyFromPos(rawStored[id].position));
      }

      // Push not explizitly placed machines to the scene
      // TODO: Make the user place them manually
      // We just calculate some next free position
      for (const id of nonPlaced) {
        console.log("adding", id);
        const position = nextGridPos();
        console.log("Got pos", position);

        // Add the machine to the store
        // Adding it triggers a reactive update
        props.setMachinePos(id, position);
        occupiedPositions.add(keyFromPos(position));
      }
    }
  });

  function getGridPosition(id: string): [number, number, number] {
    // TODO: Detect collision with other cubes
    const machine = props.sceneStore()[id];
    console.log("getGridPosition", id, machine);
    if (machine) {
      return [machine.position[0], 0, machine.position[1]];
    }
    // Some fallback to get the next free position
    // If the position wasn't avilable in the store
    console.warn(`Position for ${id} not set`);
    return [0, 0, 0];
  }

  function nextGridPos(): [number, number] {
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

  // Circle IDEA:
  // Need to talk with timo and W about this
  const getCirclePosition =
    (center: [number, number, number]) =>
    (_id: string, index: number, total: number): [number, number, number] => {
      const r = total === 1 ? 0 : Math.sqrt(total) * CUBE_SPACING; // Radius based on total cubes
      const x = Math.cos((index / total) * 2 * Math.PI) * r + center[0];
      const z = Math.sin((index / total) * 2 * Math.PI) * r + center[2];
      // Position cubes at y = 0.5 to float above the ground
      return [x, CUBE_Y, z];
    };

  // Reactive cubes memo - this recalculates whenever data changes
  const cubes = createMemo(() => {
    console.log("Calculating cubes...");
    const sceneData = props.sceneStore(); // keep it reactive
    if (!sceneData) return [];

    const currentIds = Object.keys(sceneData);
    console.log("Current IDs:", currentIds);

    let cameraTarget = [0, 0, 0] as [number, number, number];
    if (camera && floor) {
      cameraTarget = getFloorPosition(camera, floor);
    }
    const getCubePosition =
      positionMode() === "grid"
        ? getGridPosition
        : getCirclePosition(cameraTarget);

    return currentIds.map((id, index) => {
      const activeIndex = currentIds.indexOf(id);

      const position = getCubePosition(id, index, currentIds.length);

      const targetPosition =
        activeIndex >= 0
          ? getCubePosition(id, activeIndex, currentIds.length)
          : getCubePosition(id, index, currentIds.length);

      return {
        id,
        position,
        targetPosition,
      };
    });
  });

  // Animation helper function
  function animateToPosition(
    thing: THREE.Object3D,
    targetPosition: [number, number, number],
    duration: number = ANIMATION_DURATION,
  ) {
    const startPosition = thing.position.clone();
    const endPosition = new THREE.Vector3(...targetPosition);
    const startTime = Date.now();

    function animate() {
      const elapsed = Date.now() - startTime;
      const progress = Math.min(elapsed / duration, 1);

      // Smooth easing function
      const easeProgress = 1 - Math.pow(1 - progress, 3);

      thing.position.lerpVectors(startPosition, endPosition, easeProgress);

      if (progress < 1) {
        requestAnimationFrame(animate);
        renderLoop.requestRender();
      }
    }

    animate();
  }

  function createCubeBase(
    cube_pos: [number, number, number],
    opacity = 1,
    color: THREE.ColorRepresentation = BASE_COLOR,
    emissive: THREE.ColorRepresentation = BASE_EMISSIVE,
  ) {
    const baseMaterial = new THREE.MeshPhongMaterial({
      opacity,
      color,
      emissive,
      // flatShading: true,
      transparent: true,
    });
    const base = new THREE.Mesh(sharedBaseGeometry, baseMaterial);
    base.position.set(cube_pos[0], BASE_HEIGHT / 2, cube_pos[2]);
    base.receiveShadow = true;
    return base;
  }

  function toggleSelection(id: string) {
    const next = new Set<string>();
    next.add(id);
    props.onSelect(next);
  }

  function updateMeshColors(
    selected: Set<string>,
    prev: Set<string> | undefined,
  ) {
    for (const id of selected) {
      const group = groupMap.get(id);
      if (!group) {
        console.warn(`UPDATE COLORS: Group not found for id: ${id}`);
        continue;
      }
      const base = group.children.find((child) => child.name === "base");
      if (!base || !(base instanceof THREE.Mesh)) {
        console.warn(`UPDATE COLORS: Base mesh not found for id: ${id}`);
        continue;
      }
      const cube = group.children.find((child) => child.name === "cube");
      if (!cube || !(cube instanceof THREE.Mesh)) {
        console.warn(`UPDATE COLORS: Cube mesh not found for id: ${id}`);
        continue;
      }

      const baseMaterial = base.material as THREE.MeshPhongMaterial;
      const cubeMaterial = cube.material as THREE.MeshPhongMaterial;

      baseMaterial.color.set(BASE_SELECTED_COLOR);
      baseMaterial.emissive.set(BASE_SELECTED_EMISSIVE);

      cubeMaterial.color.set(CUBE_SELECTED_COLOR);
    }

    const deselected = Array.from(prev || []).filter((s) => !selected.has(s));

    for (const id of deselected) {
      const group = groupMap.get(id);
      if (!group) {
        console.warn(`UPDATE COLORS: Group not found for id: ${id}`);
        continue;
      }
      const base = group.children.find((child) => child.name === "base");
      if (!base || !(base instanceof THREE.Mesh)) {
        console.warn(`UPDATE COLORS: Base mesh not found for id: ${id}`);
        continue;
      }
      const cube = group.children.find((child) => child.name === "cube");
      if (!cube || !(cube instanceof THREE.Mesh)) {
        console.warn(`UPDATE COLORS: Cube mesh not found for id: ${id}`);
        continue;
      }

      const baseMaterial = base.material as THREE.MeshPhongMaterial;
      const cubeMaterial = cube.material as THREE.MeshPhongMaterial;

      baseMaterial.color.set(BASE_COLOR);
      baseMaterial.emissive.set(BASE_EMISSIVE);

      cubeMaterial.color.set(CUBE_COLOR);
    }

    renderLoop.requestRender();
  }

  const initialCameraPosition = { x: 20, y: 20, z: 20 };
  const initialSphericalCameraPosition = new THREE.Spherical();
  initialSphericalCameraPosition.setFromVector3(
    new THREE.Vector3(
      initialCameraPosition.x,
      initialCameraPosition.y,
      initialCameraPosition.z,
    ),
  );

  const grid = new THREE.GridHelper(1000, 1000 / 1, 0xe1edef, 0xe1edef);

  onMount(() => {
    // Scene setup
    scene = new THREE.Scene();
    // Transparent background
    scene.background = null;

    // Create a fullscreen quad with a gradient shader
    // TODO: Recalculate gradient depending on container size
    const uniforms = {
      colorTop: { value: new THREE.Color("#edf1f1") }, // Top color
      colorBottom: { value: new THREE.Color("#e3e7e7") }, // Bottom color
      resolution: {
        value: new THREE.Vector2(window.innerWidth, window.innerHeight),
      },
    };

    const bgMaterial = new THREE.ShaderMaterial({
      uniforms,
      vertexShader: `
        void main() {
          gl_Position = vec4(position, 1.0);
        }
      `,
      fragmentShader: `
        uniform vec3 colorTop;
        uniform vec3 colorBottom;
        uniform vec2 resolution;

        void main() {
          float y = gl_FragCoord.y / resolution.y;
          gl_FragColor = vec4(mix(colorBottom, colorTop, y), 1.0);
        }
      `,
      depthTest: false,
      depthWrite: false,
    });

    // Create fullscreen quad geometry
    const bgGeometry = new THREE.PlaneGeometry(2, 2);
    const bgMesh = new THREE.Mesh(bgGeometry, bgMaterial);
    bgScene.add(bgMesh);

    // Camera setup
    // /container!.clientWidth / container!.clientHeight,
    const aspect = window.innerWidth / window.innerHeight;
    const d = 20;
    const zoom = 2.5;
    camera = new THREE.OrthographicCamera(
      (-d * aspect) / zoom,
      (d * aspect) / zoom,
      d / zoom,
      -d / zoom,
      0.001,
      1000,
    );
    camera.zoom = zoom;

    camera.position.setFromSpherical(initialSphericalCameraPosition);
    camera.lookAt(0, 0, 0);
    camera.updateProjectionMatrix();

    // Renderer setup
    renderer = new THREE.WebGLRenderer({
      antialias: true,
      alpha: true,
      logarithmicDepthBuffer: true,
    });
    renderer.setSize(container.clientWidth, container.clientHeight);
    renderer.shadowMap.enabled = true;
    renderer.shadowMap.type = THREE.PCFSoftShadowMap;
    renderer.autoClear = false;
    container.appendChild(renderer.domElement);

    // Label renderer
    labelRenderer = new CSS2DRenderer();
    labelRenderer.setSize(container.clientWidth, container.clientHeight);
    labelRenderer.domElement.style.position = "absolute";
    labelRenderer.domElement.style.top = "0px";
    labelRenderer.domElement.style.pointerEvents = "none";
    labelRenderer.domElement.style.zIndex = "0";
    container.appendChild(labelRenderer.domElement);

    controls = new MapControls(camera, renderer.domElement);
    controls.enableDamping = true; // an animation loop is required when either damping or auto-rotation are enabled
    controls.mouseButtons.RIGHT = null;
    controls.enableRotate = false;
    controls.minZoom = 1.2;
    controls.maxZoom = 3.5;
    controls.addEventListener("change", () => {
      // const aspect = container.clientWidth / container.clientHeight;
      // const zoom = camera.zoom;
      // camera.left = (-d * aspect) / zoom;
      // camera.right = (d * aspect) / zoom;
      // camera.top = d / zoom;
      // camera.bottom = -d / zoom;
      // camera.updateProjectionMatrix();
      renderLoop.requestRender();
    });

    renderLoop.init(
      scene,
      camera,
      renderer,
      labelRenderer,
      controls,
      bgScene,
      bgCamera,
    );

    // Lighting
    const ambientLight = new THREE.AmbientLight(0xffffff, 1);
    scene.add(ambientLight);

    const directionalLight = new THREE.DirectionalLight(0xffffff, 2);

    // scene.add(new THREE.DirectionalLightHelper(directionalLight));
    // scene.add(new THREE.CameraHelper(directionalLight.shadow.camera));
    // scene.add(new THREE.CameraHelper(camera));
    const lightPos = new THREE.Spherical(
      1000,
      initialSphericalCameraPosition.phi - Math.PI / 8,
      initialSphericalCameraPosition.theta - Math.PI / 2,
    );
    directionalLight.position.setFromSpherical(lightPos);
    directionalLight.target.position.set(0, 0, 0); // Point light at the center
    // initialSphericalCameraPosition
    directionalLight.castShadow = true;

    // Configure shadow camera for hard, crisp shadows
    directionalLight.shadow.camera.left = -30;
    directionalLight.shadow.camera.right = 30;
    directionalLight.shadow.camera.top = 30;
    directionalLight.shadow.camera.bottom = -30;
    directionalLight.shadow.camera.near = 0.1;
    directionalLight.shadow.camera.far = 2000;
    directionalLight.shadow.mapSize.width = 4096; // Higher resolution for sharper shadows
    directionalLight.shadow.mapSize.height = 4096;
    directionalLight.shadow.radius = 1; // Hard shadows (low radius)
    directionalLight.shadow.blurSamples = 4; // Fewer samples for harder edges
    scene.add(directionalLight);
    scene.add(directionalLight.target);

    // Floor/Ground - Make it invisible but keep it for reference
    const floorGeometry = new THREE.PlaneGeometry(1000, 1000);
    const floorMaterial = new THREE.MeshBasicMaterial({
      color: FLOOR_COLOR,
      transparent: true,
      opacity: 0.0, // Make completely invisible
    });
    floor = new THREE.Mesh(floorGeometry, floorMaterial);
    floor.rotation.x = -Math.PI / 2;
    floor.position.y = 0; // Keep at ground level for reference
    scene.add(floor);

    // grid.material.opacity = 0.2;
    // grid.material.transparent = true;
    grid.position.y = 0.001; // Slightly above the floor to avoid z-fighting
    // grid.rotation.x = -Math.PI / 2;
    grid.position.x = 0.5;
    grid.position.z = 0.5;
    scene.add(grid);

    // Shared geometries for cubes and bases
    // This allows us to reuse the same geometry for all cubes and bases
    sharedCubeGeometry = new THREE.BoxGeometry(
      CUBE_SIZE,
      CUBE_SEGMENT_HEIGHT,
      CUBE_SIZE,
    );
    sharedBaseGeometry = new THREE.BoxGeometry(
      BASE_SIZE,
      BASE_HEIGHT,
      BASE_SIZE,
    );

    // Important create CubeBase depends on sharedBaseGeometry
    initBase = createCubeBase(
      [1, BASE_HEIGHT / 2, 1],
      1,
      CREATE_BASE_COLOR,
      CREATE_BASE_EMISSIVE,
    );
    initBase.visible = false;

    scene.add(initBase);

    // const spherical = new THREE.Spherical();
    // spherical.setFromVector3(camera.position);

    // Function to update camera info
    const updateCameraInfo = () => {
      const spherical = new THREE.Spherical();
      spherical.setFromVector3(camera.position);
      setCameraInfo({
        position: {
          x: Math.round(camera.position.x * 100) / 100,
          y: Math.round(camera.position.y * 100) / 100,
          z: Math.round(camera.position.z * 100) / 100,
        },
        spherical: {
          radius: Math.round(spherical.radius * 100) / 100,
          theta: Math.round(spherical.theta * 100) / 100,
          phi: Math.round(spherical.phi * 100) / 100,
        },
      });
    };

    // Initial camera info update
    updateCameraInfo();

    createEffect(
      on(worldMode, (mode) => {
        if (mode === "create") {
          initBase!.visible = true;
        } else {
          initBase!.visible = false;
        }
        renderLoop.requestRender();
      }),
    );

    // Click handler:
    // - Select/deselects a cube in "view" mode
    // - Creates a new cube in "create" mode
    const onClick = (event: MouseEvent) => {
      if (worldMode() === "create") {
        props
          .onCreate()
          .then(({ id }) => {
            //Successfully created machine
            const pos = cursorPosition();
            if (!pos) {
              console.warn("No position set for new cube");
              return;
            }
            props.setMachinePos(id, pos);
          })
          .catch((error) => {
            console.error("Error creating cube:", error);
          })
          .finally(() => {
            if (initBase) initBase.visible = false;

            setWorldMode("view");
          });
      }

      const rect = renderer.domElement.getBoundingClientRect();
      const mouse = new THREE.Vector2(
        ((event.clientX - rect.left) / rect.width) * 2 - 1,
        -((event.clientY - rect.top) / rect.height) * 2 + 1,
      );

      raycaster.setFromCamera(mouse, camera);
      const intersects = raycaster.intersectObjects(
        Array.from(groupMap.values()),
      );
      console.log("Intersects:", intersects);
      if (intersects.length > 0) {
        const id = intersects[0].object.userData.id;
        toggleSelection(id);
      } else {
        props.onSelect(new Set<string>()); // Clear selection if clicked outside cubes
      }
    };

    renderer.domElement.addEventListener("click", onClick);

    renderLoop.requestRender();

    // Handle window resize
    const handleResize = () => {
      const aspect = container.clientWidth / container.clientHeight;
      const zoom = camera.zoom;
      camera.left = (-d * aspect) / zoom;
      camera.right = (d * aspect) / zoom;
      camera.top = d / zoom;
      camera.bottom = -d / zoom;
      camera.updateProjectionMatrix();

      renderer.setSize(container.clientWidth, container.clientHeight);
      labelRenderer.setSize(container.clientWidth, container.clientHeight);

      // Update background shader resolution
      uniforms.resolution.value.set(
        container.clientWidth,
        container.clientHeight,
      );

      renderer.render(bgScene, bgCamera);
      renderLoop.requestRender();
    };

    renderer.domElement.addEventListener("mousemove", onMouseMove);

    window.addEventListener("resize", handleResize);
    // For debugging,
    // TODO: Remove in production
    window.addEventListener(
      "contextmenu",
      (e) => {
        e.stopPropagation();
      },
      { capture: true },
    );

    // Cleanup function
    onCleanup(() => {
      renderLoop.dispose();

      renderer.domElement.removeEventListener("click", onClick);
      renderer.domElement.removeEventListener("mousemove", onMouseMove);
      window.removeEventListener("resize", handleResize);

      if (initBase) {
        initBase.geometry.dispose();
        if (Array.isArray(initBase.material)) {
          initBase.material.forEach((material) => material.dispose());
        } else {
          initBase.material.dispose();
        }
      }

      if (container) {
        container.innerHTML = "";
      }

      groupMap.forEach((group) => {
        garbageCollectGroup(group);
        scene.remove(group);
      });
      groupMap.clear();
    });
  });

  function createCube(
    gridPosition: [number, number],
    userData: { id: string },
  ) {
    // Creates a cube, base, and other visuals
    // Groups them together in the scene
    const cubeMaterial = new THREE.MeshPhongMaterial({
      color: CUBE_COLOR,
      emissive: CUBE_EMISSIVE,
      // specular: 0xffffff,
      shininess: 100,
    });
    const cubeMesh = new THREE.Mesh(sharedCubeGeometry, cubeMaterial);
    cubeMesh.castShadow = true;
    cubeMesh.receiveShadow = true;
    cubeMesh.userData = userData;
    cubeMesh.name = "cube"; // Name for easy identification
    cubeMesh.position.set(0, CUBE_Y, 0);

    const baseMesh = createCubeBase([0, BASE_HEIGHT / 2, 0]);
    baseMesh.name = "base"; // Name for easy identification

    const nameDiv = document.createElement("div");
    nameDiv.className = "machine-label";
    nameDiv.textContent = `${userData.id}`;

    const nameLabel = new CSS2DObject(nameDiv);
    nameLabel.position.set(0, CUBE_Y + CUBE_SIZE / 2 - 0.2, 0);
    cubeMesh.add(nameLabel);

    // TODO: Destroy Group in onCleanup
    const group = new THREE.Group();
    group.add(cubeMesh);
    group.add(baseMesh);
    group.position.set(gridPosition[0], 0, gridPosition[1]); // Position on the grid

    group.userData.id = userData.id;
    return group;
  }

  // Effect to manage cube meshes - this runs whenever cubes() changes
  createEffect(() => {
    const currentCubes = cubes();

    const existing = new Set(groupMap.keys());

    // Update existing cubes and create new ones
    currentCubes.forEach((cube) => {
      const existingGroup = groupMap.get(cube.id);

      console.log(
        "Processing cube:",
        cube.id,
        "Existing group:",
        existingGroup,
      );
      if (!existingGroup) {
        const group = createCube([cube.position[0], cube.position[2]], {
          id: cube.id,
        });
        scene.add(group);
        groupMap.set(cube.id, group);
      } else {
        // Only animate position if not being deleted
        const targetPosition = cube.targetPosition || cube.position;
        const currentPosition = existingGroup.position.toArray() as [
          number,
          number,
          number,
        ];
        const target = targetPosition;
        // Check if position actually changed
        if (
          Math.abs(currentPosition[0] - target[0]) > 0.01 ||
          Math.abs(currentPosition[1] - target[1]) > 0.01 ||
          Math.abs(currentPosition[2] - target[2]) > 0.01
        ) {
          animateToPosition(existingGroup, target);
        }
      }

      existing.delete(cube.id);
    });

    // Remove cubes that are no longer in the state and not being deleted
    existing.forEach((id) => {
      if (!currentCubes.find((d) => d.id == id)) {
        const group = groupMap.get(id);
        if (group) {
          console.log("Cleaning...", id);
          garbageCollectGroup(group);
          scene.remove(group);
          groupMap.delete(id);
          const pos = group.position.toArray() as [number, number, number];
          occupiedPositions.delete(keyFromPos([pos[0], pos[2]]));
        }
      }
    });

    renderLoop.requestRender();
  });

  createEffect(
    on(props.selectedIds, (curr, prev) => {
      console.log("Selected cubes:", curr);
      // Update colors of selected cubes
      updateMeshColors(curr, prev);
    }),
  );

  onCleanup(() => {
    for (const group of groupMap.values()) {
      garbageCollectGroup(group);
      scene.remove(group);
    }
    groupMap.clear();

    // Dispose shared geometries
    sharedCubeGeometry?.dispose();
    sharedBaseGeometry?.dispose();

    renderer?.dispose();
  });

  const onHover = (inside: boolean) => (event: MouseEvent) => {
    const pos = nextGridPos();
    if (!initBase) return;

    if (initBase.visible === false && inside) {
      initBase.position.set(pos[0], BASE_HEIGHT / 2, pos[1]);
      initBase.visible = true;
    }
    renderLoop.requestRender();
  };

  const onAddClick = (event: MouseEvent) => {
    setPositionMode("grid");
    setWorldMode("create");
  };
  const onMouseMove = (event: MouseEvent) => {
    if (worldMode() !== "create") return;
    if (!initBase) return;

    initBase.visible = true;

    const rect = renderer.domElement.getBoundingClientRect();
    const mouse = new THREE.Vector2(
      ((event.clientX - rect.left) / rect.width) * 2 - 1,
      -((event.clientY - rect.top) / rect.height) * 2 + 1,
    );
    raycaster.setFromCamera(mouse, camera);
    const intersects = raycaster.intersectObject(floor);
    if (intersects.length > 0) {
      const point = intersects[0].point;
      // Snap to grid
      const snapped = new THREE.Vector3(
        Math.round(point.x / GRID_SIZE) * GRID_SIZE,
        0,
        Math.round(point.z / GRID_SIZE) * GRID_SIZE,
      );

      if (
        Math.abs(initBase.position.x - snapped.x) > 0.01 ||
        Math.abs(initBase.position.z - snapped.z) > 0.01
      ) {
        // Only request render if the position actually changed
        initBase.position.set(snapped.x, 0, snapped.z);
        setCursorPosition([snapped.x, snapped.z]); // Update next position for cube creation
        renderLoop.requestRender();
      }
    }
  };

  return (
    <>
      <div class="cubes-scene-container" ref={(el) => (container = el)} />
      <div class="toolbar-container">
        <Toolbar>
          <ToolbarButton
            name="Select"
            icon="Cursor"
            onClick={() => setWorldMode("view")}
            selected={worldMode() === "view"}
          />
          <ToolbarButton
            name="new-machine"
            icon="NewMachine"
            disabled={positionMode() === "circle"}
            onClick={onAddClick}
            selected={worldMode() === "create"}
          />
          <Divider orientation="vertical" />
          <ToolbarButton
            name="modules"
            icon="Modules"
            onClick={() => {
              if (positionMode() === "grid") {
                setPositionMode("circle");
                setWorldMode("view");
                grid.visible = false;
              } else {
                setPositionMode("grid");
                grid.visible = true;
              }
            }}
          />
          <ToolbarButton name="delete" icon="Trash" />
        </Toolbar>
      </div>
    </>
  );
}
