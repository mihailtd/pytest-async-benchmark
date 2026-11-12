import { mkdirSync, readFileSync, writeFileSync } from "node:fs";
import { dirname, join, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const here = dirname(fileURLToPath(import.meta.url));
const root = resolve(here, "..");
const docsDir = join(root, "docs");
const vitepressDir = join(docsDir, ".vitepress");
const repo = "https://github.com/mihailtd/pytest-async-benchmark";
const pypi = "https://pypi.org/project/pytest-async-benchmark/";

// Read pyproject.toml for package version
const pyproject = readFileSync(join(root, "pyproject.toml"), "utf8");
const version = pyproject.match(/version\s*=\s*"([^"]+)"/)?.[1] || "0.4.0";

// Read CHANGELOG.md
const changelog = readFileSync(join(root, "CHANGELOG.md"), "utf8");
const releases = [
  ...changelog.matchAll(
    /^## \[(\S+)\] - (\d{4}-\d{2}-\d{2})\n([\s\S]*?)(?=^## |(?![\s\S]))/gm
  ),
].map(([, release, date, body]) => ({
  version: release,
  date,
  highlights: [...body.matchAll(/^- \*\*([^*]+?)\*\*/gm)]
    .map(([, title]) => title.replace(/[.:]$/, "").replace(/`/g, ""))
    .filter((title) => !/^(fix|fixed|breaking|docs)\b/i.test(title)),
}));

mkdirSync(vitepressDir, { recursive: true });
writeFileSync(
  join(vitepressDir, "release.json"),
  `${JSON.stringify({ version, repo, pypi, releases }, null, 2)}\n`
);

// Copy CHANGELOG.md to docs/changelog.md with frontmatter
const changelogPage = `---
title: Changelog
description: Release history, new features, and breaking changes for pytest-async-benchmark.
---

${changelog}
`;
writeFileSync(join(docsDir, "changelog.md"), changelogPage);

console.log(
  `sync-docs: version ${version}, ${releases.length} releases, changelog.md synced`
);
