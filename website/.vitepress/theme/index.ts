import DefaultTheme from "vitepress/theme";
import type { App } from "vue";
import TerminalShowcase from "./components/TerminalShowcase.vue";
import "./custom.css";

export default {
  extends: DefaultTheme,
  enhanceApp({ app }: { app: App }) {
    app.component("TerminalShowcase", TerminalShowcase);
  },
};
