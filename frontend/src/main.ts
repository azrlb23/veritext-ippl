import { createApp } from "vue";
import { createPinia } from "pinia";
import App from "./App.vue";
import router from "./router";
import { registerAuthExpiredHandler, registerTokenRefreshedHandler } from "./services/api";
import { useAuthStore } from "./stores/auth";
import "./assets/main.css";

const app = createApp(App);
const pinia = createPinia();

app.use(pinia);
app.use(router);
registerAuthExpiredHandler(() => {
  useAuthStore(pinia).clearLocalSession();
});
registerTokenRefreshedHandler((nextToken) => {
  useAuthStore(pinia).setAccessToken(nextToken);
});

app.mount("#app");
