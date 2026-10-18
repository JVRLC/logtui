import DefaultTheme from "vitepress/theme";
import type { App } from "vue";
import LandingPage from "./components/LandingPage.vue";
import TerminalShowcase from "./components/TerminalShowcase.vue";
import "./custom.css";

export default {
  extends: DefaultTheme,
  enhanceApp({ app }: { app: App }) {
    app.component("LandingPage", LandingPage);
    app.component("TerminalShowcase", TerminalShowcase);
  },
};
