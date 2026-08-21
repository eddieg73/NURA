import { defineConfig } from "deepsec/config";
import { generatedMatchersPlugin } from "./generated-matchers.js";

export default defineConfig({
  projects: [
    { id: "nura_medical", root: ".." },
    // <deepsec:projects-insert-above>
  ],
  plugins: [generatedMatchersPlugin],
});
