import { createEffect, createSignal, onCleanup, onMount, Show } from "solid-js";
import * as THREE from "three";
import { Button } from "./components/button";
import Icon from "./components/icon";

function addCubesSpiral({
  scene,
  count,
  gap,
  selected,
}: {
  scene: THREE.Scene;
  count: number;
  gap: number;
  selected?: string;
}) {
  const cubeSize = 1;
  const baseSize = 1.4;

  const cubeGeometry = new THREE.BoxGeometry(cubeSize, cubeSize, cubeSize);
  const baseGeometry = new THREE.BoxGeometry(baseSize, 0.05, baseSize);

  const cubeMaterial = new THREE.MeshStandardMaterial({
    color: 0xe0e0e0,
    roughness: 0.6,
    metalness: 0.1,
  });

  const baseMaterial = new THREE.MeshStandardMaterial({
    color: 0xffffff,
    roughness: 0.8,
    metalness: 0,
  });

  let placed = 0;
  const visited = new Set<string>();

  let x = 0;
  let z = 0;

  let dx = 1;
  let dz = 0;

  let segmentLength = 1;
  let segmentPassed = 0;
  let stepsTaken = 0;
  let turnCounter = 0;

  while (placed < count) {
    const key = `${x},${z}`;
    if (!visited.has(key)) {
      if ((x + z) % 2 === 0) {
        // Place base
        const base = new THREE.Mesh(baseGeometry, baseMaterial);
        base.position.set(x * gap, 0, z * gap);
        base.receiveShadow = true;
        base.castShadow = true;
        scene.add(base);

        // Place cube
        const cube = new THREE.Mesh(cubeGeometry, cubeMaterial);
        if (selected && +selected === placed) {
          console.log("Selected", placed);
          cube.material = new THREE.MeshStandardMaterial({
            color: 0x99e0ff,
            roughness: 0.6,
            metalness: 0.1,
          });
          base.material = new THREE.MeshStandardMaterial({
            color: 0x99e0ff,
            roughness: 0.6,
            metalness: 0.1,
          });
        }
        // Store
        cube.userData = { id: placed };

        cube.position.set(x * gap, 0.55, z * gap);
        cube.castShadow = true;
        scene.add(cube);

        placed++;
      }
      visited.add(key);
    }

    x += dx;
    z += dz;
    segmentPassed++;
    stepsTaken++;

    if (segmentPassed === segmentLength) {
      segmentPassed = 0;

      // Turn right: [1,0] → [0,1] → [-1,0] → [0,-1]
      const temp = dx;
      dx = -dz;
      dz = temp;

      turnCounter++;
      if (turnCounter % 2 === 0) {
        segmentLength++;
      }
    }

    // Fail-safe to prevent infinite loops
    if (stepsTaken > count * 20) break;
  }

  // Clean up geometry
  cubeGeometry.dispose();
  baseGeometry.dispose();
}

interface ViewProps {
  count: number;
  onCubeClick: (id: number) => void;
  selected?: string;
}
const View = (props: ViewProps) => {
  let container: HTMLDivElement | undefined;

  onMount(() => {
    const scene = new THREE.Scene();

    const camera = new THREE.PerspectiveCamera(
      75,
      container!.clientWidth / container!.clientHeight,
      0.1,
      1000,
    );

    // Transparent renderer
    const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
    renderer.setSize(container!.clientWidth, container!.clientHeight);
    renderer.setClearColor(0x000000, 0); // Transparent background
    renderer.shadowMap.enabled = true;
    renderer.shadowMap.type = THREE.PCFSoftShadowMap;
    container!.appendChild(renderer.domElement);

    // Cube (casts shadow)
    const cubeGeometry = new THREE.BoxGeometry();
    const cubeMaterial = new THREE.MeshStandardMaterial({
      color: 0xb0c0c2,
      roughness: 0.4,
      metalness: 0.1,
    });

    const cube = new THREE.Mesh(cubeGeometry, cubeMaterial);
    cube.castShadow = true;
    cube.position.y = 1;
    // scene.add(cube);
    addCubesSpiral({
      scene,
      count: props.count,
      gap: 1.5,
      selected: props.selected,
    });

    const factor = Math.log10(props.count) / 10 + 1;
    camera.position.set(5 * factor, 6 * factor, 5 * factor); // from above and to the side
    camera.lookAt(0, 0, 0);

    // Floor (receives shadow)
    const floorGeometry = new THREE.PlaneGeometry(100, 100);
    const floorMaterial = new THREE.ShadowMaterial({ opacity: 0.1 });
    const floor = new THREE.Mesh(floorGeometry, floorMaterial);
    floor.rotation.x = -Math.PI / 2;
    floor.position.y = -0.1;
    floor.receiveShadow = true;
    scene.add(floor);

    // Light (casts shadow)
    const directionalLight = new THREE.DirectionalLight(0xffffff, 1);
    directionalLight.position.set(-20, 30, 20); // above & behind the cube
    directionalLight.castShadow = true;
    directionalLight.shadow.mapSize.width = 2048; // higher res = smoother shadow
    directionalLight.shadow.mapSize.height = 2048;
    directionalLight.shadow.radius = 6;
    // directionalLight.shadow.radius

    scene.add(directionalLight);
    // Optional ambient light for slight scene illumination
    scene.add(new THREE.AmbientLight(0xffffff, 0.2));

    // Animate
    // const animate = () => {
    //   animationId = requestAnimationFrame(animate);
    // };

    const raycaster = new THREE.Raycaster();
    const mouse = new THREE.Vector2();

    const handleClick = (event: MouseEvent) => {
      const rect = renderer.domElement.getBoundingClientRect();
      mouse.x = ((event.clientX - rect.left) / rect.width) * 2 - 1;
      mouse.y = -((event.clientY - rect.top) / rect.height) * 2 + 1;

      raycaster.setFromCamera(mouse, camera);
      const intersects = raycaster.intersectObjects(scene.children, true);
      const cube = intersects.find((i) => i.object.userData?.id !== undefined);

      if (cube) {
        props.onCubeClick(cube.object.userData.id);
      }
    };

    renderer.domElement.addEventListener("click", handleClick);

    renderer.render(scene, camera);
    // let animationId = requestAnimationFrame(animate);

    onCleanup(() => {
      //   cancelAnimationFrame(animationId);
      renderer.dispose();
      cubeGeometry.dispose();
      cubeMaterial.dispose();
      floorGeometry.dispose();
      floorMaterial.dispose();
      container?.removeChild(renderer.domElement);
      renderer.domElement.removeEventListener("click", handleClick);
    });
  });

  return (
    <div
      ref={container}
      style={{ width: "100%", height: "100%", overflow: "hidden" }}
    />
  );
};

export const ThreePlayground = () => {
  const [count, setCount] = createSignal(1);
  const [selected, setSelected] = createSignal<string>("");

  const onCubeClick = (id: number) => {
    console.log(`Cube ${id} clicked`);
    setSelected(`${id}`);
  };

  return (
    <div class="relative size-full">
      <Show when={selected() || !selected()} keyed>
        <Show when={count()} keyed>
          {(c) => (
            <View count={c} onCubeClick={onCubeClick} selected={selected()} />
          )}
        </Show>
      </Show>
      <div class="absolute bottom-4 right-0 z-10 flex w-full items-center justify-center">
        <div class="flex w-fit items-center justify-between gap-4 rounded-xl border px-8 py-2 text-white shadow-2xl bg-inv-1 border-inv-1">
          <Button startIcon={<Icon icon="Edit" />}></Button>
          <Button startIcon={<Icon icon="Grid" />}></Button>
          <Button
            startIcon={<Icon icon="Plus" />}
            onClick={() => {
              setCount((c) => c + 1);
            }}
          ></Button>
          <Button
            startIcon={<Icon icon="Trash" />}
            onClick={() => {
              setCount((c) => c - 1);
            }}
          ></Button>
        </div>
      </div>
    </div>
  );
};
