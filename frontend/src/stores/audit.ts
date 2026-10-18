import { defineStore } from "pinia";
import { ref } from "vue";
import type { AuditTask, AuditReport } from "../types";
import { auditService } from "../services/auditService";

export const useAuditStore = defineStore("audit", () => {
  const currentTask = ref<AuditTask | null>(null);
  const currentReport = ref<AuditReport | null>(null);
  const isPolling = ref<boolean>(false);

  async function pollTaskStatus(taskId: string, onComplete?: (report: AuditReport) => void) {
    isPolling.value = true;
    const interval = setInterval(async () => {
      try {
        const task = await auditService.getStatus(taskId);
        currentTask.value = task;

        if (task.status === "SUCCESS") {
          clearInterval(interval);
          isPolling.value = false;
          // Fetch report
          if (onComplete) {
            // Note: report id can be fetched by task id
          }
        } else if (["FAILED", "CANCELLED", "REVOKED"].includes(task.status)) {
          clearInterval(interval);
          isPolling.value = false;
        }
      } catch {
        clearInterval(interval);
        isPolling.value = false;
      }
    }, 2000);
  }

  return {
    currentTask,
    currentReport,
    isPolling,
    pollTaskStatus,
  };
});
