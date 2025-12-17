import {
  createSignal,
  createEffect,
  onCleanup,
  onMount,
  Show,
  Component,
  batch,
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
import { createMachineMesh, MachineRepr } from "./MachineRepr";
import ServiceDialog from "@/src/components/MachineGraph/Service";
import { useMachinesContext } from "@/src/models";
import ServiceInstanceDialog from "@/src/components/MachineGraph/ServiceInstance";
import { isPosition } from "@/src/util";
import { useUIContext } from "@/src/models/ui";

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
  let actionBase: THREE.Mesh;
  let actionMachine: THREE.Group;
  let snappedMousePosition: readonly [number, number] | undefined;
  let mouseMoveData:
    | {
        timer?: number;
        startingPosition: readonly [number, number];
        targetMachineId: string;
      }
    | undefined;

  // Create background scene
  const bgScene = new THREE.Scene();
  const bgCamera = new THREE.OrthographicCamera(-1, 1, 1, -1, 0, 1);

  const groupMap = new Map<string, THREE.Group>();

  let sharedCubeGeometry: THREE.BoxGeometry;
  let sharedBaseGeometry: THREE.BoxGeometry;

  const [
    machines,
    {
      activateMachine,
      deactivateMachine,
      updateMachineData,
      toggleHighlightedMachines,
      setHighlightedMachines,
      unhighlightMachines,
      deleteMachine,
    },
  ] = useMachinesContext();

  const [ui, { setToolbarMode, showModal }] = useUIContext();
  // Managed by controls
  const [isDragging, setIsDragging] = createSignal(false);

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

    createEffect(() => {
      if (ui.toolbarMode.type === "create") {
        actionBase.visible = true;
      } else {
        actionBase.visible = false;
      }
      renderLoop.requestRender();
    });

    const registry = new ObjectRegistry();

    createEffect(() => {
      for (const machine of Object.values(machines().all)) {
        const sceneMachine = sceneMachines[machine.id];
        if (!sceneMachine) {
          const repr = new MachineRepr(
            scene,
            registry,
            new THREE.Vector2(
              machine.data.position[0],
              machine.data.position[1],
            ),
            machine,
            camera,
          );
          sceneMachines[machine.id] = repr;
          scene.add(repr.group);
        } else {
          sceneMachine.setPosition(
            new THREE.Vector2(
              machine.data.position[0],
              machine.data.position[1],
            ),
          );
        }
      }
      for (const [machineId, machine] of Object.entries(sceneMachines)) {
        if (machineId in machines().all) {
          continue;
        }
        machine.dispose(scene);
        delete sceneMachines[machineId];
      }
      renderLoop.requestRender();
    });

    // Click handler:
    // - Select/deselects a cube in mode
    // - Creates a new cube in "create" mode
    const onClickGraph = async (event: MouseEvent) => {
      if (ui.toolbarMode.type === "create") {
        if (!snappedMousePosition) return;
        showModal({
          type: "AddMachine",
          position: snappedMousePosition,
        });
        if (actionBase) actionBase.visible = false;
        setToolbarMode({ type: "select" });
        return;
      }

      if (ui.toolbarMode.type === "move") {
        const currId = menuIntersection().at(0);
        if (!currId || !snappedMousePosition) return;

        setToolbarMode({ type: "select" });
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

        if (ui.toolbarMode.type === "select") {
          activateMachine(id);
        } else if (
          ui.toolbarMode.type === "service" &&
          ui.toolbarMode.subtype &&
          ui.toolbarMode.highlighting
        ) {
          toggleHighlightedMachines(id);
        }
      } else {
        if (ui.toolbarMode.type === "select") {
          deactivateMachine();
        }
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

    const onMouseDownGraph = (e: MouseEvent) => {
      const machineIds = intersectMachines(
        e,
        renderer,
        camera,
        sceneMachines,
        raycaster,
      );

      // Left button
      if (e.button === 0) {
        if (ui.toolbarMode.type === "select" && machineIds.length !== 0) {
          const targetMachineId = machineIds[0]!;
          const pos = machines().all[targetMachineId]!.data.position;
          // Disable controls to avoid conflict
          controls.enabled = false;

          // Change cursor to grabbing
          // LongPress, if not canceled, enters move mode
          mouseMoveData = {
            targetMachineId,
            startingPosition: pos,
            timer: window.setTimeout(() => {
              actionMachine.position.set(pos[0], 0, pos[1]);
              batch(() => {
                setIsDragging(true);
                setHighlightedMachines(targetMachineId);
                setToolbarMode({ type: "move" });
              });
              renderLoop.requestRender();
            }, 500),
          };
        }
      } else if (e.button === 2) {
        e.preventDefault();
        e.stopPropagation();
        if (machineIds.length === 0) return;
        setMenuIntersection(machineIds);
        setMenuPos({ x: e.clientX, y: e.clientY });
        setContextOpen(true);
      }
    };
    const onMouseUpGraph = (e: MouseEvent) => {
      if (e.button === 0) {
        // Always re-enable controls
        controls.enabled = true;
        if (mouseMoveData) {
          const data = mouseMoveData;
          window.clearTimeout(data.timer);
          if (ui.toolbarMode.type === "move") {
            actionMachine.visible = false;
            // Set machine as not flying
            batch(() => {
              updateMachineData(data.targetMachineId, {
                position: [actionMachine.position.x, actionMachine.position.z],
              });
              setIsDragging(false);
              unhighlightMachines();
              setToolbarMode({ type: "select" });
            });
            renderLoop.requestRender();
            mouseMoveData = undefined;
          }
        }
      }
    };
    const onMouseMoveGraph = (event: MouseEvent) => {
      if (!(ui.toolbarMode.type === "create" || ui.toolbarMode.type === "move"))
        return;

      const actionRepr =
        ui.toolbarMode.type === "create" ? actionBase : actionMachine;
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
      const intersect = intersects?.[0];
      if (intersect) {
        const { point } = intersect;

        const snapped = snapToGrid([point.x, point.z]);
        if (!snapped) return;
        if (
          Math.abs(actionRepr.position.x - snapped[0]) > 0.01 ||
          Math.abs(actionRepr.position.z - snapped[1]) > 0.01
        ) {
          // Only request render if the position actually changed
          actionRepr.position.set(snapped[0], 0, snapped[1]);
          snappedMousePosition = snapped; // Update next position for cube creation
          renderLoop.requestRender();
        }
      }
    };

    renderer.domElement.addEventListener("mousedown", onMouseDownGraph);
    renderer.domElement.addEventListener("mouseup", onMouseUpGraph);
    renderer.domElement.addEventListener("mousemove", onMouseMoveGraph);

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
      renderer.domElement.removeEventListener("mousemove", onMouseMoveGraph);
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

  const snapToGrid = (pos: readonly [number, number]) => {
    // Snap to grid
    const snapped = [
      Math.round(pos[0] / GRID_SIZE) * GRID_SIZE,
      Math.round(pos[1] / GRID_SIZE) * GRID_SIZE,
    ] as const;

    const intersects = Object.values(machines().all).some((machine) =>
      isPosition(machine.data.position, snapped),
    );

    // Skip snapping if there's already a machine at this position (excluding
    // the staring position if a machine is being moved)
    if (
      intersects &&
      !(mouseMoveData && isPosition(mouseMoveData.startingPosition, snapped))
    ) {
      return;
    }

    return snapped;
  };

  const onClickToolbarAdd = (event: MouseEvent) => {
    setToolbarMode({ type: "create" });
    renderLoop.requestRender();
  };
  const onMenuSelect = async (mode: "move" | "delete") => {
    const firstId = menuIntersection()[0];
    if (!firstId) {
      return;
    }

    if (mode === "delete") {
      await deleteMachine(firstId);
      setContextOpen(false);
      return;
    } else if (mode === "move") {
      controls.enabled = false;
      const machine = sceneMachines[firstId];
      const pos = [machine.group.position.x, machine.group.position.z] as const;
      actionMachine.position.set(pos[0], 0, pos[1]);
      batch(() => {
        setIsDragging(true);
        setHighlightedMachines(firstId);
        setToolbarMode({ type: "move" });
      });
      renderLoop.requestRender();
      mouseMoveData = {
        targetMachineId: firstId,
        startingPosition: pos,
      };
    }
  };

  return (
    <>
      <Show when={contextOpen()}>
        <Portal mount={document.body}>
          <Menu
            onSelect={onMenuSelect}
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
          (
            {
              select: "cursor-pointer",
              service: "cursor-pointer",
              create: "cursor-cell",
            } as Record<string, string>
          )[ui.toolbarMode.type] || "",
          isDragging() && "cursor-grabbing",
        )}
        ref={(el) => (container = el)}
      />
      <div class={styles.toolbarContainer}>
        <Show
          when={ui.toolbarMode.type === "service" && !ui.toolbarMode.subtype}
        >
          <div class="absolute bottom-full left-1/2 mb-2 -translate-x-1/2">
            <ServiceDialog />
          </div>
        </Show>
        <Show
          when={ui.toolbarMode.type === "service" && ui.toolbarMode.subtype}
        >
          <ServiceInstanceDialog />
        </Show>
        <Toolbar>
          <ToolbarButton
            description="Select machine"
            name="Select"
            icon="Cursor"
            onClick={() => setToolbarMode({ type: "select" })}
            selected={ui.toolbarMode.type === "select"}
          />
          <ToolbarButton
            description="Create new machine"
            name="new-machine"
            icon="NewMachine"
            onClick={onClickToolbarAdd}
            selected={ui.toolbarMode.type === "create"}
          />
          <Divider orientation="vertical" />
          <ToolbarButton
            description="Add new Service"
            name="modules"
            icon="Services"
            selected={ui.toolbarMode.type === "service"}
            onClick={() => {
              deactivateMachine();
              setToolbarMode({ type: "service" });
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
  const intersections = raycaster.intersectObjects(
    Object.values(sceneMachines).map((m) => m.group),
  );

  return intersections.map((i) => i.object.userData.id as string);
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
