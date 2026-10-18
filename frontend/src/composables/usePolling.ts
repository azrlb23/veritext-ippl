import { ref, onUnmounted, getCurrentInstance } from "vue";

export interface PollingOptions {
  intervalMs?: number;
  immediate?: boolean;
}

export function usePolling(
  callback: () => Promise<boolean | void> | boolean | void,
  options: PollingOptions = {}
) {
  const { intervalMs = 2000, immediate = true } = options;
  const isPolling = ref(false);
  let timerId: ReturnType<typeof setInterval> | null = null;

  async function executeStep() {
    try {
      const shouldStop = await callback();
      if (shouldStop === true) {
        stop();
      }
    } catch {
      // Allow caller error handling
    }
  }

  function start() {
    if (isPolling.value) return;
    isPolling.value = true;
    if (immediate) {
      void executeStep();
    }
    timerId = setInterval(() => {
      void executeStep();
    }, intervalMs);
  }

  function stop() {
    if (timerId !== null) {
      clearInterval(timerId);
      timerId = null;
    }
    isPolling.value = false;
  }

  if (getCurrentInstance()) {
    onUnmounted(() => {
      stop();
    });
  }

  return {
    isPolling,
    start,
    stop,
  };
}
