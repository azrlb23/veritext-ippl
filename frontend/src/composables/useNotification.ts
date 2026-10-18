import { ref } from "vue";

export type NotificationType = "info" | "success" | "warning" | "error";

export interface NotificationItem {
  id: string;
  type: NotificationType;
  title?: string;
  message: string;
  duration?: number;
}

const notifications = ref<NotificationItem[]>([]);
const timers = new Map<string, ReturnType<typeof setTimeout>>();

export function useNotification() {
  function showNotification(
    message: string,
    type: NotificationType = "info",
    title?: string,
    duration = 4000
  ) {
    const id = `notif-${Date.now()}-${Math.random().toString(36).slice(2, 6)}`;
    const item: NotificationItem = {
      id,
      type,
      title,
      message,
      duration,
    };
    notifications.value.push(item);

    if (duration > 0) {
      const timer = setTimeout(() => {
        dismissNotification(id);
      }, duration);
      timers.set(id, timer);
    }

    return id;
  }

  function dismissNotification(id: string) {
    const timer = timers.get(id);
    if (timer) {
      clearTimeout(timer);
      timers.delete(id);
    }

    const idx = notifications.value.findIndex((n) => n.id === id);
    if (idx !== -1) {
      notifications.value.splice(idx, 1);
    }
  }

  function clearAll() {
    timers.forEach((t) => clearTimeout(t));
    timers.clear();
    notifications.value = [];
  }

  return {
    notifications,
    showNotification,
    dismissNotification,
    clearAll,
  };
}
