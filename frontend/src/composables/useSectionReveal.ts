import { onBeforeUnmount, onMounted, ref } from "vue";

export interface SectionRevealOptions {
  threshold?: number;
  rootMargin?: string;
  replay?: boolean;
}

export function useSectionReveal(options: SectionRevealOptions = {}) {
  const sectionRef = ref<HTMLElement | null>(null);
  const isVisible = ref(false);
  let observer: IntersectionObserver | null = null;
  let rafId: number | null = null;

  const enterThreshold = options.threshold ?? 0.12;
  const rootMargin = options.rootMargin ?? "0px 0px -32px 0px";
  const replay = options.replay ?? true;

  function cancelPendingReveal() {
    if (rafId !== null) { cancelAnimationFrame(rafId); rafId = null; }
  }

  onMounted(() => {
    const isReducedMotion =
      typeof window !== "undefined" &&
      window.matchMedia?.("(prefers-reduced-motion: reduce)").matches;

    if (typeof window === "undefined" || typeof IntersectionObserver === "undefined" || isReducedMotion) {
      isVisible.value = true;
      return;
    }
    if (!sectionRef.value) return;

    observer = new IntersectionObserver(
      (entries) => {
        for (const entry of entries) {
          const hit = entry.isIntersecting && (entry.intersectionRatio >= enterThreshold || entry.intersectionRect.height >= 72);
          if (hit) {
            if (!isVisible.value && rafId === null) {
              rafId = requestAnimationFrame(() => { rafId = null; isVisible.value = true; });
            }
          } else if (replay && !entry.isIntersecting && entry.intersectionRatio === 0) {
            cancelPendingReveal();
            isVisible.value = false;
          }
        }
      },
      { threshold: [0, enterThreshold], rootMargin }
    );

    observer.observe(sectionRef.value);
  });

  onBeforeUnmount(() => {
    cancelPendingReveal();
    observer?.disconnect();
    observer = null;
  });

  return { sectionRef, isVisible };
}
