import { defineStore } from "pinia";
import { ref } from "vue";
import type { AuditTask, AuditReport } from "../types";
import { auditService } from "../services/auditService";

export const useAuditStore = defineStore("audit", () => {
  const currentTask = ref<AuditTask | null>(null);
  const currentReport = ref<AuditReport | null>(null);
  const isPolling = ref<boolean>(false);

  let pollingTimer: ReturnType<typeof setInterval> | null = null;

  function stopPolling() {
    if (pollingTimer !== null) {
      clearInterval(pollingTimer);
      pollingTimer = null;
    }
    isPolling.value = false;
  }

  async function pollTaskStatus(taskId: string, onComplete?: (report: AuditReport) => void) {
    stopPolling();
    isPolling.value = true;
    pollingTimer = setInterval(async () => {
      try {
        const task = await auditService.getStatus(taskId);
        currentTask.value = task;

        if (task.status === "SUCCESS") {
          stopPolling();
          if (onComplete) {
            try {
              const report = await auditService.getReport(taskId);
              currentReport.value = report;
              onComplete(report);
            } catch {
              // Report fetch handler
            }
          }
        } else if (["FAILED", "CANCELLED", "REVOKED"].includes(task.status)) {
          stopPolling();
        }
      } catch {
        stopPolling();
      }
    }, 2000);
  }

  function reset() {
    stopPolling();
    currentTask.value = null;
    currentReport.value = null;
  }

  return {
    currentTask,
    currentReport,
    isPolling,
    pollTaskStatus,
    stopPolling,
    reset,
  };
});
