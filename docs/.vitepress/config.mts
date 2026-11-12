import { writeFileSync } from "node:fs";
import { join } from "node:path";
import { defineConfig } from "vitepress";
import release from "./release.json" with { type: "json" };
import { author } from "./theme/site.ts";

function githubSlug(heading: string): string {
  return heading
    .trim()
    .toLowerCase()
    .replace(/<[^>]*>/g, "")
    .replace(/[^\p{L}\p{N}\p{M}\- _]/gu, "")
    .replace(/ /g, "-");
}

const base = process.env.SITE_BASE ?? "/pytest-async-benchmark/";
const siteUrl = (
  process.env.SITE_URL || `https://mihailtd.github.io${base}`
).replace(/\/?$/, "/");

const description =
  "Modern pytest benchmarking for async Python. High-precision latency percentiles, concurrency under load, task leak detection, and statistically sound regression tests.";

const structuredData = {
  "@context": "https://schema.org",
  "@type": "SoftwareSourceCode",
  name: "pytest-async-benchmark",
  description,
  url: siteUrl,
  codeRepository: release.repo,
  programmingLanguage: ["Python"],
  runtimePlatform: "Python 3.10+",
  license: "https://opensource.org/licenses/MIT",
  version: release.version,
  author: {
    "@type": "Person",
    name: author.name,
    url: author.site,
    sameAs: [author.site, author.github, author.company.url],
    worksFor: {
      "@type": "Organization",
      name: author.company.name,
      url: author.company.url,
    },
  },
};

export default defineConfig({
  title: "pytest-async-benchmark",
  titleTemplate: ":title | pytest-async-benchmark",
  description,
  base,
  cleanUrls: true,
  lastUpdated: true,
  appearance: true,
  ignoreDeadLinks: "localhostLinks",
  head: [
    ["link", { rel: "icon", type: "image/svg+xml", href: `${base}logo.svg` }],
    ["meta", { name: "theme-color", content: "#0284c7" }],
    ["meta", { name: "author", content: author.name }],
    ["link", { rel: "author", href: author.site }],
    ["meta", { property: "og:type", content: "website" }],
    ["meta", { property: "og:site_name", content: "pytest-async-benchmark" }],
    ["meta", { property: "og:description", content: description }],
    ["meta", { name: "twitter:card", content: "summary_large_image" }],
    ["script", { type: "application/ld+json" }, JSON.stringify(structuredData)],
  ],
  sitemap: { hostname: siteUrl },
  buildEnd({ outDir }) {
    writeFileSync(
      join(outDir, "robots.txt"),
      `User-agent: *\nAllow: /\n\nSitemap: ${siteUrl}sitemap.xml\n`
    );
  },
  transformHead({ pageData, title, description: pageDescription }) {
    const path = pageData.relativePath
      .replace(/(^|\/)index\.md$/, "$1")
      .replace(/\.md$/, "");
    const url = `${siteUrl}${path}`;
    return [
      ["link", { rel: "canonical", href: url }],
      ["meta", { property: "og:url", content: url }],
      ["meta", { property: "og:title", content: title }],
      ["meta", { property: "og:description", content: pageDescription }],
      ["meta", { name: "twitter:title", content: title }],
      ["meta", { name: "twitter:description", content: pageDescription }],
    ];
  },
  markdown: {
    anchor: { slugify: githubSlug },
    theme: { light: "github-light", dark: "github-dark" },
    config(md) {
      const fence = md.renderer.rules.fence;
      md.renderer.rules.fence = (tokens, idx, options, env, self) => {
        const token = tokens[idx];
        if (token.info.trim() === "mermaid") {
          return `<Mermaid code="${encodeURIComponent(token.content)}" />`;
        }
        return fence
          ? fence(tokens, idx, options, env, self)
          : self.renderToken(tokens, idx, options);
      };
    },
  },
  themeConfig: {
    logo: "/logo.svg",
    nav: [
      { text: "Guide", link: "/guide/getting-started", activeMatch: "^/guide/" },
      { text: "Concurrency", link: "/guide/concurrency" },
      { text: "Pedantic", link: "/guide/pedantic-mode" },
      { text: "Regressions", link: "/guide/regression-detection" },
      { text: "Reference", link: "/reference/api", activeMatch: "^/reference/" },
      { text: "Changelog", link: "/changelog" },
      {
        text: `v${release.version}`,
        items: [
          { text: "PyPI Package", link: release.pypi },
          { text: "GitHub Releases", link: `${release.repo}/releases` },
          { text: "Changelog", link: "/changelog" },
        ],
      },
    ],
    sidebar: {
      "/": [
        {
          text: "Getting Started",
          items: [
            { text: "Quick Start & Setup", link: "/guide/getting-started" },
            { text: "How It Works", link: "/guide/how-it-works" },
            { text: "Dual Interface (Async vs Sync)", link: "/guide/dual-interface" },
          ],
        },
        {
          text: "Core Capabilities",
          items: [
            { text: "Concurrency & Load", link: "/guide/concurrency" },
            { text: "Pedantic Mode (Setup/Teardown)", link: "/guide/pedantic-mode" },
            { text: "Task Leak Detection", link: "/guide/leak-detection" },
            { text: "Regression Detection & CI Baselines", link: "/guide/regression-detection" },
            { text: "Comparative Benchmarking", link: "/guide/comparative-benchmarking" },
          ],
        },
        {
          text: "Framework Guides",
          items: [
            { text: "FastAPI & HTTP APIs", link: "/guide/frameworks-fastapi" },
            { text: "FastMCP & AI Tool Servers", link: "/guide/frameworks-fastmcp" },
            { text: "Quart & Aiohttp", link: "/guide/frameworks-quart-aiohttp" },
          ],
        },
        {
          text: "Reference",
          items: [
            { text: "API Reference", link: "/reference/api" },
            { text: "CLI Options & Configuration", link: "/reference/cli-and-config" },
            { text: "Migrating from pytest-benchmark", link: "/guide/migration" },
            { text: "Changelog", link: "/changelog" },
          ],
        },
      ],
    },
    outline: { level: [2, 3] },
    search: { provider: "local" },
    socialLinks: [
      { icon: "github", link: release.repo },
    ],
    editLink: {
      pattern: ({ filePath }) =>
        `https://github.com/mihailtd/pytest-async-benchmark/edit/main/docs/${filePath}`,
      text: "Edit this page on GitHub",
    },
  },
});
