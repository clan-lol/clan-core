import {
  createSignal,
  createEffect,
  onCleanup,
  onMount,
  on,
  Show,
  Component,
} from "solid-js";
import styles from "./MachineGraph.module.css";

import * as THREE from "three";
import { MapControls } from "three/examples/jsm/controls/MapControls.js";
import { CSS2DRenderer } from "three/examples/jsm/renderers/CSS2DRenderer.js";

import { Toolbar } from "../Toolbar/Toolbar";
import { ToolbarButton } from "../Toolbar/ToolbarButton";
import { Divider } from "../Divider/Divider";
import { renderLoop } from "./RenderLoop";
import { ObjectRegistry } from "./ObjectRegistry";
import cx from "classnames";
import { Portal } from "solid-js/web";
import { Menu } from "../ContextMenu/ContextMenu";
import {
  clearHighlight,
  highlightGroups,
  setHighlightGroups,
} from "./highlightStore";
import { createMachineMesh, MachineRepr } from "./MachineRepr";
import client from "@/src/models/api/clan/client-call";
import SelectService from "@/src/workflows/ServiceInstance/SelectService";
import {
  ModalCancelError,
  ServiceInstance,
  ServiceInstanceContextProvider,
  useMachinesContext,
  useModalContext,
  useServiceInstancesContext,
} from "@/src/models";
import ServiceInstanceWorkflow from "@/src/workflows/ServiceInstance";

export const MachineGraph: Component = () => {
  let container: HTMLDivElement;
  let scene: THREE.Scene;
  let camera: THREE.OrthographicCamera;
  let renderer: THREE.WebGLRenderer;
  let labelRenderer: CSS2DRenderer;
  let floor: THREE.Mesh;
  let controls: MapControls;
  // Raycaster for clicking
  const raycaster = new THREE.Raycaster();
  let actionBase: THREE.Mesh | undefined;
  let actionMachine: THREE.Group | undefined;

  // Create background scene
  const bgScene = new THREE.Scene();
  const bgCamera = new THREE.OrthographicCamera(-1, 1, 1, -1, 0, 1);

  const groupMap = new Map<string, THREE.Group>();

  let sharedCubeGeometry: THREE.BoxGeometry;
  let sharedBaseGeometry: THREE.BoxGeometry;

  const [, { openModal }] = useModalContext<"addMachine">();
  const [machines, { activateMachine, deactivateMachine }] =
    useMachinesContext();
  const [, { createServiceInstance }] = useServiceInstancesContext();
  const [editingServinceInstance, setEditingServinceInstance] =
    createSignal<ServiceInstance | null>(null);

  const [actionMode, setActionMode] = createSignal<
    "select" | "service" | "create" | "move"
  >("select");
  // Managed by controls
  const [isDragging, setIsDragging] = createSignal(false);

  const [cancelMove, setCancelMove] = createSignal<NodeJS.Timeout>();

  // TODO: Unify this with actionRepr position
  const [cursorPosition, setCursorPosition] = createSignal<[number, number]>();

  // Context menu state
  const [contextOpen, setContextOpen] = createSignal(false);
  const [menuPos, setMenuPos] = createSignal<{ x: number; y: number }>();
  const [menuIntersection, setMenuIntersection] = createSignal<string[]>([]);

  // Grid configuration
  const GRID_SIZE = 1;

  const BASE_SIZE = 0.9; // Height of the cube above the ground
  const CUBE_SIZE = BASE_SIZE / 1.5; //
  const BASE_HEIGHT = 0.05; // Height of the cube above the ground
  const CUBE_SEGMENT_HEIGHT = CUBE_SIZE / 1;

  const FLOOR_COLOR = 0xcdd8d9;

  const BASE_COLOR = 0xecfdff;
  const BASE_EMISSIVE = 0x0c0c0c;

  const ACTION_BASE_COLOR = 0x636363;

  const CREATE_BASE_EMISSIVE = 0xc5fad7;
  const MOVE_BASE_EMISSIVE = 0xb2d7ff;

  const sceneMachines: Record<string, MachineRepr> = {};

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

    // Lighting
    const ambientLight = new THREE.AmbientLight(0xd9f2f7, 0.72);
    scene.add(ambientLight);

    const directionalLight = new THREE.DirectionalLight(0xffffff, 3.5);

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
    actionBase = createCubeBase(
      [1, BASE_HEIGHT / 2, 1],
      1,
      ACTION_BASE_COLOR,
      CREATE_BASE_EMISSIVE,
    );
    actionBase.visible = false;

    scene.add(actionBase);

    function createActionMachine() {
      const { baseMesh, cubeMesh, material, baseMaterial } =
        createMachineMesh();
      const group = new THREE.Group();
      group.add(baseMesh);
      group.add(cubeMesh);
      // group.scale.set(0.75, 0.75, 0.75);
      material.opacity = 0.6;
      baseMaterial.opacity = 0.3;
      baseMaterial.emissive.set(MOVE_BASE_EMISSIVE);
      // Hide until needed
      group.visible = false;
      return group;
    }
    actionMachine = createActionMachine();
    scene.add(actionMachine);

    createEffect(
      on(actionMode, (mode) => {
        if (mode === "create") {
          actionBase!.visible = true;
        } else {
          actionBase!.visible = false;
        }
        renderLoop.requestRender();
      }),
    );

    const registry = new ObjectRegistry();

    createEffect(() => {
      for (const machine of Object.values(machines().all)) {
        if (!sceneMachines[machine.id]) {
          const repr = new MachineRepr(
            scene,
            registry,
            new THREE.Vector2(
              machine.data.position[0],
              machine.data.position[1],
            ),
            machine.id,
            () => machine.isActive,
            highlightGroups,
            camera,
          );
          sceneMachines[machine.id] = repr;
          scene.add(repr.group);
        } else {
          sceneMachines[machine.id].setPosition(
            new THREE.Vector2(
              machine.data.position[0],
              machine.data.position[1],
            ),
          );
        }
      }
      renderLoop.requestRender();
    });

    // Click handler:
    // - Select/deselects a cube in mode
    // - Creates a new cube in "create" mode
    const onClickGraph = async (event: MouseEvent) => {
      if (actionMode() === "create") {
        try {
          await openModal("addMachine", {
            position: cursorPosition()!,
          });
        } catch (err) {
          if (err instanceof ModalCancelError) {
            return;
          }
          throw err;
        }
        if (actionBase) actionBase.visible = false;
        setActionMode("select");
        return;
      }

      if (actionMode() === "move") {
        const currId = menuIntersection().at(0);
        const pos = cursorPosition();
        if (!currId || !pos) return;

        setActionMode("select");
        clearHighlight("move");
      }

      const rect = renderer.domElement.getBoundingClientRect();
      const mouse = new THREE.Vector2(
        ((event.clientX - rect.left) / rect.width) * 2 - 1,
        -((event.clientY - rect.top) / rect.height) * 2 + 1,
      );

      raycaster.setFromCamera(mouse, camera);
      const intersects = raycaster.intersectObjects(
        Array.from(Object.values(sceneMachines).map((m) => m.group)),
      );
      if (intersects.length > 0) {
        const id = intersects.find((i) => i.object.userData?.id)?.object
          .userData.id as string | undefined;

        if (!id) return;

        if (actionMode() === "select") {
          activateMachine(id);
        }

        console.log("Clicked on machine", id);
        emitMachineClick(id); // notify subscribers
      } else {
        emitMachineClick(null);

        if (actionMode() === "select") props.onSelect(new Set<string>());
      }
    };

    renderer.domElement.addEventListener("click", onClickGraph);

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

    const handleMouseDown = (e: MouseEvent) => {
      const { machines, intersection } = intersectMachines(
        e,
        renderer,
        camera,
        sceneMachines,
        raycaster,
      );
      if (e.button === 0) {
        // Left button

        if (actionMode() === "select" && machines.length) {
          // Disable controls to avoid conflict
          controls.enabled = false;

          // Change cursor to grabbing
          // LongPress, if not canceled, enters move mode
          const cancelMove = setTimeout(() => {
            setIsDragging(true);
            const pos =
              machines[0]?.group.position || new THREE.Vector3(0, 0, 0);
            actionMachine?.position.set(pos.x, 0, pos.z);
            // Set machine as flying
            setHighlightGroups({ move: new Set(machines) });

            setActionMode("move");
            renderLoop.requestRender();
          }, 500);
          setCancelMove(cancelMove);
        }
      }

      if (e.button === 2) {
        e.preventDefault();
        e.stopPropagation();
        if (!intersection.length) return;
        setMenuIntersection(machines);
        setMenuPos({ x: e.clientX, y: e.clientY });
        setContextOpen(true);
      }
    };
    const handleMouseUp = (e: MouseEvent) => {
      if (e.button === 0) {
        setIsDragging(false);
        if (cancelMove()) {
          clearTimeout(cancelMove()!);
          setCancelMove(undefined);
        }
        // Always re-enable controls
        controls.enabled = true;

        if (actionMode() === "move") {
          // Set machine as not flying
          const pos = actionMachine!.position.toArray();
          props.setMachinePos(highlightGroups["move"].values().next().value!, [
            pos[0], // x
            pos[2], // z
          ]);
          clearHighlight("move");
          setActionMode("select");
          renderLoop.requestRender();
        }
      }
    };

    renderer.domElement.addEventListener("mousedown", handleMouseDown);
    renderer.domElement.addEventListener("mouseup", handleMouseUp);
    renderer.domElement.addEventListener("mousemove", onMouseMove);

    window.addEventListener("resize", handleResize);

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

      for (const machine of Object.values(sceneMachines)) {
        machine.dispose(scene);
      }

      renderer.domElement.removeEventListener("click", onClickGraph);
      renderer.domElement.removeEventListener("mousemove", onMouseMove);
      window.removeEventListener("resize", handleResize);

      if (actionBase) {
        actionBase.geometry.dispose();
        if (Array.isArray(actionBase.material)) {
          actionBase.material.forEach((material) => material.dispose());
        } else {
          actionBase.material.dispose();
        }
      }

      if (container) {
        container.innerHTML = "";
      }
    });
  });

  const snapToGrid = (point: THREE.Vector3) => {
    // Snap to grid
    const snapped = new THREE.Vector3(
      Math.round(point.x / GRID_SIZE) * GRID_SIZE,
      0,
      Math.round(point.z / GRID_SIZE) * GRID_SIZE,
    );

    // Skip snapping if there's already a cube at this position
    const positions = Object.entries(machines().all);
    const intersects = positions.some(
      ([, machine]) =>
        machine.data.position[0] === snapped.x &&
        machine.data.position[1] === snapped.z,
    );
    const movingMachine = Array.from(highlightGroups["move"] || [])[0];
    const startingPos = positions.find(
      ([machineId]) => machineId === movingMachine,
    );
    if (startingPos) {
      const isStartingPos =
        snapped.x === startingPos[1].data.position[0] &&
        snapped.z === startingPos[1].data.position[1];
      // If Intersect any other machine and not the one being moved
      if (!isStartingPos && intersects) {
        return;
      }
    } else {
      if (intersects) {
        return;
      }
    }

    return snapped;
  };

  const onClickToolbarAdd = (event: MouseEvent) => {
    setActionMode("create");
    renderLoop.requestRender();
  };
  const onMouseMove = (event: MouseEvent) => {
    if (!(actionMode() === "create" || actionMode() === "move")) return;

    const actionRepr = actionMode() === "create" ? actionBase : actionMachine;
    if (!actionRepr) return;

    actionRepr.visible = true;

    // Calculate mouse position in normalized device coordinates
    // (-1 to +1) for both components

    const rect = renderer.domElement.getBoundingClientRect();
    const mouse = new THREE.Vector2(
      ((event.clientX - rect.left) / rect.width) * 2 - 1,
      -((event.clientY - rect.top) / rect.height) * 2 + 1,
    );
    raycaster.setFromCamera(mouse, camera);
    const intersects = raycaster.intersectObject(floor);
    if (intersects.length > 0) {
      const point = intersects[0].point;

      const snapped = snapToGrid(point);
      if (!snapped) return;
      if (
        Math.abs(actionRepr.position.x - snapped.x) > 0.01 ||
        Math.abs(actionRepr.position.z - snapped.z) > 0.01
      ) {
        // Only request render if the position actually changed
        actionRepr.position.set(snapped.x, 0, snapped.z);
        setCursorPosition([snapped.x, snapped.z]); // Update next position for cube creation
        renderLoop.requestRender();
      }
    }
  };
  const handleMenuSelect = async (mode: "move" | "delete") => {
    const firstId = menuIntersection()[0];
    if (!firstId) {
      return;
    }
    const machine = machineManager.machines.get(firstId);
    if (mode === "delete") {
      console.log("deleting machine", firstId);
      await client.post("delete_machine", {
        body: {
          machine: { flake: { identifier: props.clanURI }, name: firstId },
        },
      });
      navigateToClan(navigate, props.clanURI);
      ctx.machinesQuery.refetch();
      ctx.serviceInstancesQuery.refetch();
      return;
    }

    // Else "move" mode
    setActionMode(mode);
    setHighlightGroups({ move: new Set(menuIntersection()) });

    // Find the position of the first selected machine
    // Set the actionMachine position to that
    if (machine && actionMachine) {
      actionMachine.position.set(
        machine.group.position.x,
        0,
        machine.group.position.z,
      );
      setCursorPosition([machine.group.position.x, machine.group.position.z]);
    }
  };

  return (
    <>
      <Show when={contextOpen()}>
        <Portal mount={document.body}>
          <Menu
            onSelect={handleMenuSelect}
            intersect={menuIntersection()}
            x={menuPos()!.x - 10}
            y={menuPos()!.y - 10}
            close={() => setContextOpen(false)}
          />
        </Portal>
      </Show>
      <div
        class={cx(
          styles.cubesSceneContainer,
          {
            select: "cursor-pointer",
            service: "cursor-pointer",
            create: "cursor-cell",
            move: "",
          }[actionMode()],
          isDragging() && "cursor-grabbing",
        )}
        ref={(el) => (container = el)}
      />
      <div class={styles.toolbarContainer}>
        <Show when={actionMode() === "service"}>
          <div class="absolute bottom-full left-1/2 mb-2 -translate-x-1/2">
            <SelectService
              onSelect={(service) => {
                setActionMode("select");
                if (service.instances.length === 0) {
                  const instance = createServiceInstance(service);
                  setEditingServinceInstance(instance);
                } else {
                  setEditingServinceInstance(service.instances[0]);
                }
              }}
              onClose={() => setActionMode("select")}
            />
          </div>
        </Show>
        <Toolbar>
          <ToolbarButton
            description="Select machine"
            name="Select"
            icon="Cursor"
            onClick={() => setActionMode("select")}
            selected={actionMode() === "select"}
          />
          <ToolbarButton
            description="Create new machine"
            name="new-machine"
            icon="NewMachine"
            onClick={onClickToolbarAdd}
            selected={actionMode() === "create"}
          />
          <Divider orientation="vertical" />
          <ToolbarButton
            description="Add new Service"
            name="modules"
            icon="Services"
            selected={actionMode() === "service"}
            onClick={() => {
              deactivateMachine();
              setActionMode("service");
            }}
          />
          <ToolbarButton
            icon="Update"
            name="Reload"
            description="Reload machines"
            onClick={() => machinesQuery.refetch()}
          />
        </Toolbar>
        <Show when={editingServinceInstance()}>
          {(editingServinceInstance) => (
            <ServiceInstanceContextProvider
              serviceInstance={editingServinceInstance}
            >
              <ServiceInstanceWorkflow
                onClose={() => setEditingServinceInstance(null)}
                onDone={() => setEditingServinceInstance(null)}
              />
            </ServiceInstanceContextProvider>
          )}
        </Show>
      </div>
    </>
  );
};
export default MachineGraph;

function intersectMachines(
  event: MouseEvent,
  renderer: THREE.WebGLRenderer,
  camera: THREE.Camera,
  sceneMachines: Record<string, MachineRepr> = {},
  raycaster: THREE.Raycaster,
) {
  const rect = renderer.domElement.getBoundingClientRect();
  const mouse = new THREE.Vector2(
    ((event.clientX - rect.left) / rect.width) * 2 - 1,
    -((event.clientY - rect.top) / rect.height) * 2 + 1,
  );
  raycaster.setFromCamera(mouse, camera);
  const intersects = raycaster.intersectObjects(
    Object.values(sceneMachines).map((m) => m.group),
  );

  return {
    machines: intersects.map((i) => i.object.userData.id),
    intersection: intersects,
  };
}

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
