import {
  createSignal,
  createEffect,
  onCleanup,
  onMount,
  on,
  JSX,
} from "solid-js";
import "./cubes.css";

import * as THREE from "three";
import { MapControls } from "three/examples/jsm/controls/MapControls.js";
import { CSS2DRenderer } from "three/examples/jsm/renderers/CSS2DRenderer.js";

import { Toolbar } from "../components/Toolbar/Toolbar";
import { ToolbarButton } from "../components/Toolbar/ToolbarButton";
import { Divider } from "../components/Divider/Divider";
import { MachinesQueryResult, useMachinesQuery } from "../hooks/queries";
import { SceneData } from "../stores/clan";
import { Accessor } from "solid-js";
import { renderLoop } from "./RenderLoop";
import { ObjectRegistry } from "./ObjectRegistry";
import { MachineManager } from "./MachineManager";
import cx from "classnames";

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

// Can be imported by others via wrappers below
// Global signal for last clicked machine
const [lastClickedMachine, setLastClickedMachine] = createSignal<string | null>(
  null,
);

// Exported so others could also emit the signal if needed
// And for testing purposes
export function emitMachineClick(id: string | null) {
  setLastClickedMachine(id);
  if (id) {
    // Clear after a short delay to allow re-clicking the same machine
    setTimeout(() => {
      setLastClickedMachine(null);
    }, 100);
  }
}

/** Hook for components to subscribe */
export function useMachineClick() {
  return lastClickedMachine;
}

/*Gloabl signal*/
const [worldMode, setWorldMode] = createSignal<
  "default" | "select" | "service" | "create"
>("select");
export { worldMode, setWorldMode };

export function CubeScene(props: {
  cubesQuery: MachinesQueryResult;
  onCreate: () => Promise<{ id: string }>;
  selectedIds: Accessor<Set<string>>;
  onSelect: (v: Set<string>) => void;
  sceneStore: Accessor<SceneData>;
  setMachinePos: (machineId: string, pos: [number, number] | null) => void;
  isLoading: boolean;
  clanURI: string;
  toolbarPopup?: JSX.Element;
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

  let sharedCubeGeometry: THREE.BoxGeometry;
  let sharedBaseGeometry: THREE.BoxGeometry;

  const [positionMode, setPositionMode] = createSignal<"grid" | "circle">(
    "grid",
  );
  // Managed by controls
  const [isDragging, setIsDragging] = createSignal(false);

  const [cursorPosition, setCursorPosition] = createSignal<[number, number]>();

  const [cameraInfo, setCameraInfo] = createSignal({
    position: { x: 0, y: 0, z: 0 },
    spherical: { radius: 0, theta: 0, phi: 0 },
  });

  // Grid configuration
  const GRID_SIZE = 1;

  const BASE_SIZE = 0.9; // Height of the cube above the ground
  const CUBE_SIZE = BASE_SIZE / 1.5; //
  const BASE_HEIGHT = 0.05; // Height of the cube above the ground
  const CUBE_Y = 0 + CUBE_SIZE / 2 + BASE_HEIGHT / 2; // Y position of the cube above the ground
  const CUBE_SEGMENT_HEIGHT = CUBE_SIZE / 1;

  const FLOOR_COLOR = 0xcdd8d9;

  const BASE_COLOR = 0xecfdff;
  const BASE_EMISSIVE = 0x0c0c0c;

  const CREATE_BASE_COLOR = 0x636363;
  const CREATE_BASE_EMISSIVE = 0xc5fad7;

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
    // controls.rotateSpeed = -0.8;
    // controls.enableRotate = false;
    controls.minZoom = 1.2;
    controls.maxZoom = 3.5;
    controls.addEventListener("change", () => {
      const aspect = container.clientWidth / container.clientHeight;
      const zoom = camera.zoom;
      camera.left = (-d * aspect) / zoom;
      camera.right = (d * aspect) / zoom;
      camera.top = d / zoom;
      camera.bottom = -d / zoom;
      camera.updateProjectionMatrix();
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

    controls.addEventListener("start", (e) => {
      setIsDragging(true);
    });
    controls.addEventListener("end", (e) => {
      setIsDragging(false);
    });

    // Lighting
    const ambientLight = new THREE.AmbientLight(0xd9f2f7, 0.72);
    scene.add(ambientLight);

    const directionalLight = new THREE.DirectionalLight(0xffffff, 3.5);

    // scene.add(new THREE.DirectionalLightHelper(directionalLight));
    // scene.add(new THREE.CameraHelper(camera));
    const lightPos = new THREE.Spherical(
      15,
      initialSphericalCameraPosition.phi - Math.PI / 8,
      initialSphericalCameraPosition.theta - Math.PI / 2,
    );
    directionalLight.position.setFromSpherical(lightPos);
    directionalLight.rotation.set(0, 0, 0);
    // initialSphericalCameraPosition
    directionalLight.castShadow = true;

    // Configure shadow camera for hard, crisp shadows
    directionalLight.shadow.camera.left = -20;
    directionalLight.shadow.camera.right = 20;
    directionalLight.shadow.camera.top = 20;
    directionalLight.shadow.camera.bottom = -20;
    directionalLight.shadow.camera.near = 0.1;
    directionalLight.shadow.camera.far = 30;
    directionalLight.shadow.mapSize.width = 4096; // Higher resolution for sharper shadows
    directionalLight.shadow.mapSize.height = 4096;
    directionalLight.shadow.radius = 1; // Hard shadows (low radius)
    directionalLight.shadow.blurSamples = 4; // Fewer samples for harder edges
    scene.add(directionalLight);
    scene.add(directionalLight.target);
    // scene.add(new THREE.CameraHelper(directionalLight.shadow.camera));

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

    const registry = new ObjectRegistry();

    const machineManager = new MachineManager(
      scene,
      registry,
      props.sceneStore,
      props.cubesQuery,
      props.selectedIds,
      props.setMachinePos,
    );

    // Click handler:
    // - Select/deselects a cube in mode
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

            setWorldMode("default");
          });
      }

      const rect = renderer.domElement.getBoundingClientRect();
      const mouse = new THREE.Vector2(
        ((event.clientX - rect.left) / rect.width) * 2 - 1,
        -((event.clientY - rect.top) / rect.height) * 2 + 1,
      );

      raycaster.setFromCamera(mouse, camera);
      const intersects = raycaster.intersectObjects(
        Array.from(machineManager.machines.values().map((m) => m.group)),
      );
      console.log("Intersects:", intersects);
      if (intersects.length > 0) {
        console.log("Clicked on cube:", intersects);
        const id = intersects[0].object.userData.id;

        if (worldMode() === "select") toggleSelection(id);

        emitMachineClick(id); // notify subscribers
      } else {
        emitMachineClick(null);

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

      // renderer.render(bgScene, bgCamera);
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

    // Initial render
    renderLoop.requestRender();

    // Cleanup function
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

      renderLoop.dispose();

      machineManager.dispose(scene);

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
    });
  });

  const onAddClick = (event: MouseEvent) => {
    setPositionMode("grid");
    setWorldMode("create");
    renderLoop.requestRender();
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

      // Skip snapping if there's already a cube at this position
      if (props.sceneStore()) {
        const positions = Object.values(props.sceneStore());
        const intersects = positions.some(
          (p) => p.position[0] === snapped.x && p.position[1] === snapped.z,
        );
        if (intersects) {
          return;
        }
      }

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

  const machinesQuery = useMachinesQuery(props.clanURI);

  return (
    <>
      <div
        class={cx(
          "cubes-scene-container",
          worldMode() === "default" && "cursor-no-drop",
          worldMode() === "select" && "cursor-pointer",
          worldMode() === "service" && "cursor-pointer",
          worldMode() === "create" && "cursor-cell",
          isDragging() && "!cursor-grabbing",
        )}
        ref={(el) => (container = el)}
      />
      <div class="toolbar-container">
        <div class="absolute bottom-full left-1/2 mb-2 -translate-x-1/2">
          {props.toolbarPopup}
        </div>
        <Toolbar>
          <ToolbarButton
            description="Select machine"
            name="Select"
            icon="Cursor"
            onClick={() => setWorldMode("select")}
            selected={worldMode() === "select"}
          />
          <ToolbarButton
            description="Create new machine"
            name="new-machine"
            icon="NewMachine"
            onClick={onAddClick}
            selected={worldMode() === "create"}
          />
          <Divider orientation="vertical" />
          <ToolbarButton
            description="Add new Service"
            name="modules"
            icon="Services"
            selected={worldMode() === "service"}
            onClick={() => {
              setWorldMode("service");
            }}
          />
          <ToolbarButton
            icon="Update"
            name="Reload"
            description="Reload machines"
            onClick={() => machinesQuery.refetch()}
          />
        </Toolbar>
      </div>
    </>
  );
}
