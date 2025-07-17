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

import { Toolbar } from "../components/Toolbar/Toolbar";
import { ToolbarButton } from "../components/Toolbar/ToolbarButton";
import { Divider } from "../components/Divider/Divider";
import { UseQueryResult } from "@tanstack/solid-query";
import { ListMachines } from "../routes/Clan/Clan";
import { callApi } from "../hooks/api";

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
  camera: THREE.PerspectiveCamera,
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

export function CubeScene(props: { cubesQuery: UseQueryResult<ListMachines> }) {
  // sceneData.cubesQuer
  let container: HTMLDivElement;
  let scene: THREE.Scene;
  let camera: THREE.PerspectiveCamera;
  let renderer: THREE.WebGLRenderer;
  let floor: THREE.Mesh;

  // Create background scene
  const bgScene = new THREE.Scene();
  const bgCamera = new THREE.OrthographicCamera(-1, 1, 1, -1, 0, 1);

  let raycaster: THREE.Raycaster;

  const groupMap = new Map<string, THREE.Group>();
  const positionMap = new Map<string, THREE.Vector3>();

  let sharedCubeGeometry: THREE.BoxGeometry;
  let sharedBaseGeometry: THREE.BoxGeometry;

  // Used for development purposes
  // Vite does hot-reload but we need to ensure the animation loop doesn't run multiple times
  // This flag prevents multiple animation loops from running simultaneously
  // It is set to true when the component mounts and false when it unmounts
  let isAnimating = false; // Flag to prevent multiple loops
  let frameCount = 0;

  const [ids, setIds] = createSignal<string[]>([]);
  const [positionMode, setPositionMode] = createSignal<"grid" | "circle">(
    "grid",
  );
  const [nextBasePosition, setNextPosition] =
    createSignal<THREE.Vector3 | null>(null);
  const [worldMode, setWorldMode] = createSignal<"view" | "create">("view");

  // Backed camera position for restoring after switching mode
  const [backedCameraPosition, setBackedCameraPosition] = createSignal<{
    pos: THREE.Vector3;
    dir: THREE.Vector3;
  }>();

  const [selectedIds, setSelectedIds] = createSignal<Set<string>>(new Set());
  const [deletingIds, setDeletingIds] = createSignal<Set<string>>(new Set());
  const [creatingIds, setCreatingIds] = createSignal<Set<string>>(new Set());
  const [cameraInfo, setCameraInfo] = createSignal({
    position: { x: 0, y: 0, z: 0 },
    spherical: { radius: 0, theta: 0, phi: 0 },
  });

  // Animation configuration
  const ANIMATION_DURATION = 800; // milliseconds
  const DELETE_ANIMATION_DURATION = 400; // milliseconds
  const CREATE_ANIMATION_DURATION = 600; // milliseconds

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

  function getDefaultPosition(): [number, number, number] {
    return [0, 0, 0];
  }

  function getGridPosition(
    id: string,
    index: number,
    total: number,
  ): [number, number, number] {
    // TODO: Detect collision with other cubes
    const pos = positionMap.get(id);
    if (pos) {
      return pos.toArray() as [number, number, number];
    }
    const nextPos = nextBasePosition();
    if (!nextPos) {
      // Use next position if available
      throw new Error("Next position is not set");
    }

    const next = nextPos.toArray() as [number, number, number];
    positionMap.set(id, new THREE.Vector3(...next));
    return next;
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

  // Reactive cubes memo - this recalculates whenever ids() changes
  const cubes = createMemo(() => {
    const currentIds = ids();
    const deleting = deletingIds();
    const creating = creatingIds();

    // Include both active and deleting cubes for smooth transitions
    const allIds = [...new Set([...currentIds, ...Array.from(deleting)])];

    let cameraTarget = [0, 0, 0] as [number, number, number];
    if (camera && floor) {
      cameraTarget = getFloorPosition(camera, floor);
    }
    const getCubePosition =
      positionMode() === "grid"
        ? getGridPosition
        : getCirclePosition(cameraTarget);

    return allIds.map((id, index) => {
      const isDeleting = deleting.has(id);
      const isCreating = creating.has(id);
      const activeIndex = currentIds.indexOf(id);

      const position = getCubePosition(
        id,
        isDeleting ? -1 : activeIndex >= 0 ? activeIndex : index,
        currentIds.length,
      );

      const targetPosition =
        activeIndex >= 0
          ? getCubePosition(id, activeIndex, currentIds.length)
          : getCubePosition(id, index, currentIds.length);

      return {
        id,
        position,
        isDeleting,
        isCreating,
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
      }
    }

    animate();
  }

  // Create animation helper
  function animateCreate(
    mesh: THREE.Mesh,
    baseMesh: THREE.Mesh,
    onComplete: () => void,
  ) {
    const startTime = Date.now();

    // Start with zero scale and full opacity
    mesh.scale.setScalar(0);
    baseMesh.scale.setScalar(0);

    // Ensure materials are fully opaque
    // if (Array.isArray(mesh.material)) {
    //   mesh.material.forEach((material) => {
    //     (material as THREE.MeshBasicMaterial).opacity = 1;
    //     material.transparent = false;
    //   });
    // } else {
    //   (mesh.material as THREE.MeshBasicMaterial).opacity = 1;
    //   mesh.material.transparent = false;
    // }

    // if (Array.isArray(baseMesh.material)) {
    //   baseMesh.material.forEach((material) => {
    //     (material as THREE.MeshBasicMaterial).opacity = 1;
    //     material.transparent = false;
    //   });
    // } else {
    //   (baseMesh.material as THREE.MeshBasicMaterial).opacity = 1;
    //   baseMesh.material.transparent = false;
    // }

    function animate() {
      const elapsed = Date.now() - startTime;
      const progress = Math.min(elapsed / CREATE_ANIMATION_DURATION, 1);

      // Smooth easing function with slight overshoot effect
      let easeProgress;
      if (progress < 0.8) {
        // First 80% - smooth scale up
        easeProgress = 1 - Math.pow(1 - progress / 0.8, 3);
      } else {
        // Last 20% - slight overshoot and settle
        const overshootProgress = (progress - 0.8) / 0.2;
        const overshoot = Math.sin(overshootProgress * Math.PI) * 0.1;
        easeProgress = 1 + overshoot;
      }

      const scale = easeProgress;
      mesh.scale.setScalar(scale);
      baseMesh.scale.setScalar(scale);

      if (progress >= 1) {
        // Ensure final scale is exactly 1
        mesh.scale.setScalar(1);
        baseMesh.scale.setScalar(1);
        onComplete();
      } else {
        requestAnimationFrame(animate);
      }
    }

    animate();
  }

  // Delete animation helper
  function animateDelete(group: THREE.Group, onComplete: () => void) {
    const startTime = Date.now();
    // const startScale = group.scale.clone();
    // const startOpacity = 1;

    function animate() {
      const elapsed = Date.now() - startTime;
      const progress = Math.min(elapsed / DELETE_ANIMATION_DURATION, 1);

      // Smooth easing function
      const easeProgress = 1 - Math.pow(1 - progress, 3);
      const scale = 1 - easeProgress;
      // const opacity = startOpacity * (1 - easeProgress);

      group.scale.setScalar(scale);

      if (progress >= 1) {
        onComplete();
      } else {
        requestAnimationFrame(animate);
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

  // === Add/Delete Cube API ===
  function addCube(id: string | undefined = undefined) {
    if (!id) {
      id = crypto.randomUUID();
    }

    // Add to creating set first
    setCreatingIds((prev) => new Set([...prev, id]));

    // Add to ids
    setIds((prev) => [...prev, id]);

    // Remove from creating set after animation completes
    setTimeout(() => {
      setCreatingIds((prev) => {
        const next = new Set(prev);
        next.delete(id);
        return next;
      });
    }, CREATE_ANIMATION_DURATION);
  }

  function deleteSelectedCubes(selectedSet: Set<string>) {
    if (selectedSet.size === 0) return;

    // Add to deleting set to start animation
    setDeletingIds(selectedSet);
    console.log("Deleting cubes:", selectedSet);

    // Start delete animations
    selectedSet.forEach((id) => {
      const group = groupMap.get(id);

      if (group) {
        groupMap.delete(id); // Remove from group map

        const base = group.children.find((child) => child.name === "base");
        const cube = group.children.find((child) => child.name === "cube");

        if (!base || !cube) {
          console.warn(`DELETE: Base mesh not found for id: ${id}`);
          return;
        }

        animateDelete(group, () => {
          // Remove from deleting set when animation completes
          setDeletingIds((prev) => {
            const next = new Set(prev);
            next.delete(id);
            return next;
          });
          setSelectedIds(new Set<string>()); // Clear selection after deletion
          garbageCollectGroup(group); // Clean up geometries and materials
          setIds((prev) => prev.filter((existingId) => existingId !== id));

          console.log("Done deleting", id, ids());
        });
      } else {
        console.warn(`DELETE: Group not found for id: ${id}`);
      }
    });
  }

  function toggleSelection(id: string) {
    setSelectedIds((curr) => {
      const next = new Set(curr);
      if (next.has(id)) {
        next.delete(id);
      } else {
        next.add(id);
      }
      return next;
    });
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
  }

  function logMemoryUsage() {
    if (renderer && renderer.info) {
      console.log("Three.js Memory:", {
        geometries: renderer.info.memory.geometries,
        textures: renderer.info.memory.textures,
        programs: renderer.info.programs?.length || 0,
        calls: renderer.info.render.calls,
        triangles: renderer.info.render.triangles,
      });
    }
  }

  const initialCameraPosition = { x: 2.8, y: 4, z: -2 };
  const initialSphericalCameraPosition = new THREE.Spherical();
  initialSphericalCameraPosition.setFromVector3(
    new THREE.Vector3(
      initialCameraPosition.x,
      initialCameraPosition.y,
      initialCameraPosition.z,
    ),
  );

  let initBase: THREE.Mesh;

  const grid = new THREE.GridHelper(1000, 1000 / 1, 0xe1edef, 0xe1edef);

  createEffect(() => {
    if (props.cubesQuery.data) {
      for (const machineId of Object.keys(props.cubesQuery.data)) {
        console.log("Received: ", machineId);
        setNextPosition(new THREE.Vector3(...getDefaultPosition()));
        addCube(machineId);
      }
    }
  });

  onMount(() => {
    // Scene setup
    scene = new THREE.Scene();
    scene.fog = new THREE.Fog(0xffffff, 10, 50); //
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
    camera = new THREE.PerspectiveCamera(
      75,
      container!.clientWidth / container!.clientHeight,
      0.1,
      1000,
    );
    camera.position.setFromSpherical(initialSphericalCameraPosition);
    camera.lookAt(0, 0, 0);

    // Renderer setup
    renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
    renderer.setSize(container.clientWidth, container.clientHeight);
    renderer.shadowMap.enabled = true;
    renderer.shadowMap.type = THREE.PCFSoftShadowMap;
    container.appendChild(renderer.domElement);

    // Lighting
    const ambientLight = new THREE.AmbientLight(0xffffff, 1.5);
    scene.add(ambientLight);

    const directionalLight = new THREE.DirectionalLight(0xffffff, 2);

    // scene.add(new THREE.DirectionalLightHelper(directionalLight));
    // scene.add(new THREE.CameraHelper(directionalLight.shadow.camera));
    // scene.add(new THREE.CameraHelper(camera));
    const lightPos = new THREE.Spherical(
      100,
      initialSphericalCameraPosition.phi,
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
    directionalLight.shadow.camera.far = 200;
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

    // Basic OrbitControls implementation (simplified)
    let isDragging = false;
    let previousMousePosition = { x: 0, y: 0 };
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

    const onMouseDown = (event: MouseEvent) => {
      isDragging = true;
      previousMousePosition = { x: event.clientX, y: event.clientY };
    };

    const onMouseUp = () => {
      isDragging = false;
    };

    const onMouseMove = (event: MouseEvent) => {
      if (worldMode() === "create") {
        if (isDragging) return;

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
          if (!initBase) {
            // Create initial base mesh if it doesn't exist
            initBase = createCubeBase(
              [snapped.x, 0, snapped.z],
              1,
              CREATE_BASE_COLOR,
              CREATE_BASE_EMISSIVE, // Emissive color
            );
          } else {
            initBase.position.set(snapped.x, 0, snapped.z);
          }
          scene.remove(initBase); // Remove any existing base mesh
          scene.add(initBase);
          setNextPosition(snapped); // Update next position for cube creation
        }
        // If in create mode, don't allow camera movement
        return;
      }

      if (!isDragging) return;

      const deltaX = event.clientX - previousMousePosition.x;
      const deltaY = event.clientY - previousMousePosition.y;
      // const deltaY = event.clientY - previousMousePosition.y;
      if (positionMode() === "circle") {
        const spherical = new THREE.Spherical();
        spherical.setFromVector3(camera.position);
        spherical.theta -= deltaX * 0.01;
        // spherical.phi += deltaY * 0.01;
        // spherical.phi = Math.max(0.1, Math.min(Math.PI - 0.1, spherical.phi));

        // const lightPos = new THREE.Spherical();
        // lightPos.setFromVector3(directionalLight.position);
        // lightPos.theta = spherical.theta - Math.PI / 2; // 90 degrees offset
        // directionalLight.position.setFromSpherical(lightPos);

        // directionalLight.lookAt(0, 0, 0);

        camera.position.setFromSpherical(spherical);
        camera.lookAt(0, 0, 0);
      } else {
        const movementSpeed = 0.015;

        // Get camera direction vectors
        const cameraDirection = new THREE.Vector3();
        camera.getWorldDirection(cameraDirection);
        cameraDirection.y = 0; // Ignore vertical direction

        const cameraRight = new THREE.Vector3();
        cameraRight.crossVectors(camera.up, cameraDirection).normalize(); // Get right vector

        // Move camera based on mouse deltas
        camera.position.addScaledVector(cameraRight, deltaX * movementSpeed); // horizontal drag
        camera.position.addScaledVector(
          cameraDirection,
          deltaY * movementSpeed,
        ); // vertical drag (forward/back)

        setBackedCameraPosition({
          pos: camera.position.clone(),
          dir: camera.getWorldDirection(new THREE.Vector3()).clone(),
        });
      }
      updateCameraInfo();

      previousMousePosition = { x: event.clientX, y: event.clientY };
    };

    const onWheel = (event: WheelEvent) => {
      const spherical = new THREE.Spherical();
      spherical.setFromVector3(camera.position);
      event.preventDefault();
      spherical.radius += event.deltaY * 0.01;
      spherical.radius = Math.max(3, Math.min(10, spherical.radius)); // Clamp radius between 5 and 50
      camera.position.setFromSpherical(spherical);
      // camera.lookAt(0, 0, 0);
      updateCameraInfo();
    };

    // Event listeners
    renderer.domElement.addEventListener("mousedown", onMouseDown);
    renderer.domElement.addEventListener("mouseup", onMouseUp);
    renderer.domElement.addEventListener("mousemove", onMouseMove);
    renderer.domElement.addEventListener("wheel", onWheel);

    // Raycaster for clicking
    raycaster = new THREE.Raycaster();

    // Click handler:
    // - Select/deselects a cube in "view" mode
    // - Creates a new cube in "create" mode
    const onClick = (event: MouseEvent) => {
      if (worldMode() === "create") {
        if (initBase) {
          scene.remove(initBase); // Remove the base mesh after adding cube
          setWorldMode("view");
          const res = callApi("create_machine", {
            opts: {
              clan_dir: {
                identifier: "/home/johannes/git/tmp/my-clan",
              },
              machine: {
                name: "sara",
              },
            },
          });
          res.result.then(() => {
            props.cubesQuery.refetch();
            const pos = nextBasePosition();

            if (!pos) {
              console.error("No next position set for new cube");
              return;
            }

            positionMap.set("sara", pos);
            addCube("sara");
          });
        }
        return;
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
        setSelectedIds(new Set<string>()); // Clear selection if clicked outside cubes
      }
    };

    renderer.domElement.addEventListener("click", onClick);

    const animate = () => {
      if (!isAnimating) return; // Exit if component is unmounted

      requestAnimationFrame(animate);

      frameCount++;
      renderer.autoClear = false;
      renderer.render(bgScene, bgCamera); // Render background scene

      renderer.render(scene, camera);

      // Uncomment for memory debugging:
      if (frameCount % 300 === 0) logMemoryUsage(); // Log every 60 frames
    };
    isAnimating = true;
    animate();

    // Handle window resize
    const handleResize = () => {
      camera.aspect = container.clientWidth / container.clientHeight;
      camera.updateProjectionMatrix();
      renderer.setSize(container.clientWidth, container.clientHeight);
    };
    window.addEventListener("resize", handleResize);

    // Cleanup function
    onCleanup(() => {
      // Stop animation loop
      isAnimating = false;
      renderer.domElement.removeEventListener("mousedown", onMouseDown);
      renderer.domElement.removeEventListener("mouseup", onMouseUp);
      renderer.domElement.removeEventListener("mousemove", onMouseMove);
      renderer.domElement.removeEventListener("wheel", onWheel);
      renderer.domElement.removeEventListener("click", onClick);
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

  createEffect(() => {
    if (!container) return;
    if (worldMode() === "create") {
      // Show the plus button when in create mode
      container.style.cursor = "crosshair";
    } else {
      container.style.cursor = "pointer";
    }
  });
  createEffect(
    // Fly back and forth between circle and grid positions
    // ? Do we want to do this.
    // We could shift the center of the circle to the camera look at position
    on(positionMode, (mode) => {
      if (mode === "circle") {
        grid.visible = false; // Hide grid when in circle mode
      } else if (mode === "grid") {
        grid.visible = true; // Show grid when in grid mode
      }
    }),
  );

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
    const deleting = deletingIds();
    const creating = creatingIds();

    // Update existing cubes and create new ones
    currentCubes.forEach((cube) => {
      const existingGroup = groupMap.get(cube.id);

      if (!existingGroup) {
        const group = createCube([cube.position[0], cube.position[2]], {
          id: cube.id,
        });
        scene.add(group);
        groupMap.set(cube.id, group);

        // Start create animation if this cube is being created
        if (creating.has(cube.id)) {
          const mesh = group.children[0] as THREE.Mesh;
          const base = group.children[1] as THREE.Mesh;
          animateCreate(mesh, base, () => {
            // Animation complete callback - could add additional logic here
          });
        }
      } else if (!deleting.has(cube.id)) {
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
      if (!deleting.has(id)) {
        const group = groupMap.get(id);
        if (group) {
          garbageCollectGroup(group);
        }
      }
    });
  });

  createEffect(
    on(selectedIds, (curr, prev) => {
      console.log("Selected cubes:", curr);
      // Update colors of selected cubes
      updateMeshColors(curr, prev);
    }),
  );

  // Effect to clean up deleted cubes after animation
  createEffect(() => {
    const deleting = deletingIds();
    const currentIds = ids();

    // Clean up cubes that finished their delete animation
    deleting.forEach((id) => {
      if (!currentIds.includes(id)) {
        const group = groupMap.get(id);
        if (group) {
          scene.remove(group);
          group.children.forEach((child) => {
            // Child is finished with its destroy animation
            if (child instanceof THREE.Mesh && child.scale.x <= 0.01) {
              child.geometry.dispose();
              if (Array.isArray(child.material)) {
                child.material.forEach((material) => material.dispose());
              } else {
                child.material.dispose();
              }
            }
          });
          groupMap.delete(id);
        }
      }
    });
  });

  createEffect(() => {
    selectedIds(); // Track the signal
    // updateMeshColors();
  });

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
    // Hover over the plus button, shows a preview of the base mesh
    const currentCubes = cubes();
    if (currentCubes.length > 0) {
      return;
    }

    if (!initBase) {
      // Create initial base mesh if it doesn't exist
      initBase = createCubeBase(
        [0, BASE_HEIGHT / 2, 0],
        1,
        CREATE_BASE_COLOR,
        CREATE_BASE_EMISSIVE,
      ); // Emissive color
    }
    if (inside) {
      scene.add(initBase);
    } else {
      scene.remove(initBase);
    }
  };

  const onAddClick = (event: MouseEvent) => {
    setPositionMode("grid");
    setWorldMode("create");
  };

  return (
    <>
      <div class="cubes-scene-container" ref={(el) => (container = el)} />
      <div class="toolbar-container">
        <Toolbar>
          <ToolbarButton
            name="new-machine"
            icon="NewMachine"
            onMouseEnter={onHover(true)}
            onMouseLeave={onHover(false)}
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
              } else {
                setPositionMode("grid");
              }
            }}
          />
          <ToolbarButton
            name="delete"
            icon="Trash"
            onClick={() => deleteSelectedCubes(selectedIds())}
          />
        </Toolbar>
      </div>
    </>
  );
}
