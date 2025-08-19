import { Scene, Camera, WebGLRenderer } from "three";
import { MapControls } from "three/examples/jsm/controls/MapControls.js";
import { CSS2DRenderer } from "three/examples/jsm/renderers/CSS2DRenderer.js";

/**
 * Private class to manage the render loop
 * @internal
 */
class RenderLoop {
  // Track if a render is already requested
  // This prevents multiple requests in the same frame
  // and ensures only one render per frame
  // This is important for performance and to avoid flickering
  private renderRequested = false;

  // References to the scene, camera, renderer, controls, and label renderer
  // These will be set during initialization
  private scene!: Scene;
  private bgScene!: Scene;
  private camera!: Camera;
  private bgCamera!: Camera;
  private renderer!: WebGLRenderer;
  private controls!: MapControls;
  private labelRenderer!: CSS2DRenderer;

  // Flag to prevent multiple initializations
  private initialized = false;

  init(
    scene: Scene,
    camera: Camera,
    renderer: WebGLRenderer,
    labelRenderer: CSS2DRenderer,
    controls: MapControls,
    bgScene: Scene,
    bgCamera: Camera,
  ) {
    if (this.initialized) {
      console.error("RenderLoop already initialized.");
      return;
    }
    this.scene = scene;
    this.camera = camera;
    this.renderer = renderer;
    this.controls = controls;
    this.bgScene = bgScene;
    this.bgCamera = bgCamera;
    this.labelRenderer = labelRenderer;
    this.initialized = true;
  }

  requestRender() {
    // If not initialized, log an error and return
    if (!this.initialized) {
      console.error(
        "RenderLoop not initialized yet. Make sure to call init() once before usage.",
      );
      return;
    }
    // If a render is already requested, do nothing
    if (this.renderRequested) return;

    this.renderRequested = true;
    requestAnimationFrame(() => {
      if (!this.initialized) {
        console.log("RenderLoop not initialized, skipping render.");
        return;
      }

      this.updateTweens();

      const needsUpdate = this.controls.update(); // returns true if damping is ongoing

      this.render();
      this.renderRequested = false;

      // Controls smoothing may require another render
      if (needsUpdate) {
        this.requestRender();
      }
    });
  }

  private updateTweens() {
    // TODO: TWEEN.update() for tween animations in the future
  }

  private render() {
    // TODO: Disable console.debug in production
    // console.debug("Rendering scene...", this);

    this.renderer.clear();

    this.renderer.render(this.bgScene, this.bgCamera);
    this.renderer.render(this.scene, this.camera);
    this.labelRenderer.render(this.scene, this.camera);
  }

  dispose() {
    // Dispose controls, renderer, remove listeners if any
    this.controls.dispose();
    this.renderer.dispose();
    // clear refs, this prevents memory leaks by allowing garbage collection
    this.scene = null!;
    this.bgScene = null!;
    this.camera = null!;
    this.bgCamera = null!;
    this.renderer = null!;
    this.controls = null!;
    this.labelRenderer = null!;
    this.initialized = false;
  }
}

/**
 * Singleton instance of RenderLoop
 * This is used to manage the re-rendering
 *
 * It can only be initialized once then passed to individual components
 * they can use the renderLoop to request re-renders as needed.
 *
 *
 * Usage:
 * ```typescript
 * import { renderLoop } from "./RenderLoop";
 *
 * // Somewhere initialize the render loop:
 * renderLoop.init(scene, camera, renderer, labelRenderer, controls, bgScene, bgCamera);
 *
 * // To request a render:
 * renderLoop.requestRender();
 *
 * // To dispose:
 * onCleanup(() => {
 *  renderLoop.dispose();
 * })
 *
 */
export const renderLoop = new RenderLoop();
