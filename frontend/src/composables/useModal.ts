import { ref } from "vue";

export function useModal(initialState = false) {
  const isOpen = ref(initialState);

  function open() {
    isOpen.value = true;
  }

  function close() {
    isOpen.value = false;
  }

  function toggle() {
    isOpen.value = !isOpen.value;
  }

  return {
    isOpen,
    open,
    close,
    toggle,
  };
}
