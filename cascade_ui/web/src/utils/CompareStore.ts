import { ref, watch } from "vue";

const STORAGE_KEY = "cascade_ui.compare_items";

function load(): string[] {
  try {
    const stored = localStorage.getItem(STORAGE_KEY);
    if (!stored) return [];
    const parsed = JSON.parse(stored);
    return Array.isArray(parsed) ? parsed.filter(item => typeof item === "string") : [];
  } catch (error) {
    console.log(error);
    return [];
  }
}

const items = ref<string[]>(load());

watch(items, value => {
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(value));
  } catch (error) {
    console.log(error);
  }
}, { deep: true });

function has(id: string): boolean {
  return items.value.includes(id);
}

function add(id: string): void {
  if (id && !has(id)) {
    items.value = items.value.concat([id]);
  }
}

function remove(id: string): void {
  items.value = items.value.filter(item => item !== id);
}

function replaceAll(ids: string[]): void {
  items.value = Array.from(new Set(ids));
}

function clear(): void {
  items.value = [];
}

export function useCompareStore() {
  return { items, has, add, remove, replaceAll, clear };
}
