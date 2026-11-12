<script setup lang="ts">
import { useData } from "vitepress";
import { onMounted, ref, watch } from "vue";

const props = defineProps<{ code: string }>();
const { isDark } = useData();
const svg = ref("");
let count = 0;

async function render() {
  const { default: mermaid } = await import("mermaid");
  mermaid.initialize({
    startOnLoad: false,
    theme: isDark.value ? "dark" : "default",
    securityLevel: "strict",
    htmlLabels: false,
    flowchart: { htmlLabels: false },
  });
  await document.fonts?.ready;
  const id = `mermaid-${Math.random().toString(36).slice(2)}-${count++}`;
  try {
    svg.value = (await mermaid.render(id, decodeURIComponent(props.code))).svg;
  } catch (err) {
    console.error("Failed to render Mermaid diagram:", err);
  }
}

onMounted(render);
watch(isDark, render);
</script>

<template>
  <div class="mermaid-diagram" v-html="svg" />
</template>

<style scoped>
.mermaid-diagram {
  display: flex;
  justify-content: center;
  margin: 20px 0;
  overflow-x: auto;
}
</style>
