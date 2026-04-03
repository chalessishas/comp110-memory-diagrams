/** Tracks rendered elements and their positions for cross-referencing (arrows, highlights) */

export interface ElementEntry {
  id: string;
  type: "text" | "formula" | "graph";
  x: number;
  y: number;
  width: number;
  height: number;
}

export class ElementRegistry {
  private elements = new Map<string, ElementEntry>();
  private autoCounter = 0;

  /** Register an element after rendering */
  register(entry: ElementEntry): void {
    this.elements.set(entry.id, entry);
  }

  /** Look up element by id */
  get(id: string): ElementEntry | undefined {
    return this.elements.get(id);
  }

  /** Generate auto-id for elements without explicit id */
  autoId(type: string): string {
    return `_auto_${type}_${this.autoCounter++}`;
  }

  /** Clear all entries (used by erase "all") */
  clear(): void {
    this.elements.clear();
  }

  /** Remove a specific element */
  remove(id: string): void {
    this.elements.delete(id);
  }
}
