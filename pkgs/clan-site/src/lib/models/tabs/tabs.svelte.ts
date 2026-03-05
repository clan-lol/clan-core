import { createContext } from "svelte";

export class Tabs {
  public activeTabIndex = $state(-1);
  public get activeTab(): Tab | undefined {
    return this.all[this.activeTabIndex];
  }
  #all: readonly Tab[] = $state.raw([]);
  public get all(): readonly Tab[] {
    return this.#all;
  }

  public addTab(title: () => string): Tab {
    const tab = new Tab(title, this);
    this.#all = [...this.#all, tab];
    if (this.activeTabIndex === -1) {
      this.activeTabIndex = 0;
    }
    return tab;
  }
}

export class Tab {
  public readonly title: string;
  #tabs: Tabs;
  public constructor(title: () => string, tabs: Tabs) {
    this.title = $derived(title());
    this.#tabs = tabs;
  }
  public get isActive(): boolean {
    return this.#tabs.activeTab === this;
  }
  public get index(): number {
    return this.#tabs.all.indexOf(this);
  }
  public activate(): void {
    if (this.isActive) {
      return;
    }
    this.#tabs.activeTabIndex = this.index;
  }
}

export const [getTabsContext, setTabsContext] = createContext<Tabs>();
