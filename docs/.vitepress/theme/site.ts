// Who builds pytest-async-benchmark and articles written by the author.
// The footer, home page, and structured data in config.mts read these.
export const author = {
  name: "Mihai Farcas",
  site: "https://mihai.ltd",
  github: "https://github.com/mihailtd",
  githubHandle: "mihailtd",
  company: {
    name: "innovi.pro",
    url: "https://innovi.pro",
    description: "AI automation, agents and software architecture consultancy",
  },
};

export const articles = [
  {
    title:
      "Why I Built pytest-async-benchmark: Real Latency Distributions for Async Python",
    description:
      "Why measuring coroutines with synchronous benchmark harnesses yields false medians, how per-call timer calibration prevents event-loop distortion, and what true percentiles reveal under load.",
    url: "https://mihai.ltd/blog/why-i-built-pytest-async-benchmark/",
  },
  {
    title:
      'How end-to-end type safety turns "change it everywhere" into a list your AI agent can finish',
    description:
      "Why SQL, a generated contract and a type checker let an agent change something everywhere without missing a place.",
    url: "https://mihai.ltd/blog/end-to-end-type-safety-ai-coding-agents",
  },
  {
    title: "Why Row-Level Security Is the Only Reliable Auth for AI-Built Apps",
    description:
      "Why AI coding agents routinely introduce data leaks in application-layer authorization, and how PostgreSQL RLS turns authorization into an auditable data-layer barrier.",
    url: "https://mihai.ltd/blog/row-level-security-ai-coding-agents",
  },
];
