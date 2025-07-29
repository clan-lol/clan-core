import * as THREE from "three";

type ObjectEntry = {
  object: THREE.Object3D;
  type: string;
  id: string;
  dispose?: () => void;
};

export class ObjectRegistry {
  #objects = new Map<string, ObjectEntry>();

  add(entry: ObjectEntry) {
    const key = `${entry.type}:${entry.id}`;
    this.#objects.set(key, entry);
  }

  getById(type: string, id: string) {
    return this.#objects.get(`${type}:${id}`);
  }

  getAllByType(type: string) {
    return [...this.#objects.values()].filter((obj) => obj.type === type);
  }

  removeById(type: string, id: string, scene: THREE.Scene) {
    const key = `${type}:${id}`;
    const entry = this.#objects.get(key);
    if (entry) {
      scene.remove(entry.object);
      entry.dispose?.();
      this.#objects.delete(key);
    }
  }

  disposeAll(scene: THREE.Scene) {
    for (const entry of this.#objects.values()) {
      scene.remove(entry.object);
      entry.dispose?.();
    }
    this.#objects.clear();
  }
}
