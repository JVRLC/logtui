import { defineConfig } from "vitepress";

export default defineConfig({
  lang: "en-US",
  title: "LogTUI",
  description: "A fast terminal UI for exploring and filtering logs.",
  base: "/logtui/",
  cleanUrls: true,
  lastUpdated: true,
  head: [
    ["link", { rel: "icon", type: "image/svg+xml", href: "/logtui/logo.svg" }],
    ["meta", { name: "theme-color", content: "#0f766e" }],
    ["meta", { property: "og:title", content: "LogTUI" }],
    [
      "meta",
      {
        property: "og:description",
        content: "Explore live logs without leaving your terminal.",
      },
    ],
  ],
  themeConfig: {
    logo: "/logo.svg",
    siteTitle: "LogTUI",
    search: { provider: "local" },
    nav: [
      { text: "Documentation", link: "/getting-started/" },
      { text: "Keybindings", link: "/keybindings/" },
      { text: "Roadmap", link: "/roadmap/" },
    ],
    sidebar: [
      {
        text: "Introduction",
        items: [
          { text: "What is LogTUI?", link: "/what-is-logtui/" },
          { text: "Getting started", link: "/getting-started/" },
          { text: "Keybindings", link: "/keybindings/" },
        ],
      },
      {
        text: "Guides",
        items: [
          { text: "Log formats", link: "/log-formats/" },
          { text: "Multiple sources", link: "/multiple-sources/" },
        ],
      },
      {
        text: "Project",
        items: [{ text: "Roadmap", link: "/roadmap/" }],
      },
    ],
    socialLinks: [{ icon: "github", link: "https://github.com/JVRLC/logtui" }],
    editLink: {
      pattern: "https://github.com/JVRLC/logtui/edit/main/website/:path",
      text: "Edit this page on GitHub",
    },
    footer: {
      message: "Released under the MIT License.",
      copyright: "Copyright © 2026 LogTUI contributors",
    },
  },
});
