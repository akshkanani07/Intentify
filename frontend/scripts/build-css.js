const fs = require("fs");
const path = require("path");
const { compile } = require("@tailwindcss/node");

function getFiles(dir) {
  let results = [];
  if (!fs.existsSync(dir)) return results;
  const list = fs.readdirSync(dir);
  for (const file of list) {
    const fullPath = path.join(dir, file);
    const stat = fs.statSync(fullPath);
    if (stat && stat.isDirectory()) {
      results = results.concat(getFiles(fullPath));
    } else if (/\.(tsx|ts|jsx|js|html)$/.test(file)) {
      results.push(fullPath);
    }
  }
  return results;
}

async function buildCss() {
  console.log("Compiling Tailwind CSS v4 assets...");
  const files = getFiles(path.join(__dirname, "../src"));
  const allCode = files.map((f) => fs.readFileSync(f, "utf8")).join(" ");

  // Extract all tokens that could be candidate classes
  const tokenRegex = /[\w\-/:[\]#%.,>+*!@]+/g;
  const matches = allCode.match(tokenRegex) || [];
  const candidateSet = new Set(matches);

  console.log(`Scanned ${files.length} source files, extracted ${candidateSet.size} candidate tokens.`);

  const baseCss = `
@import "tailwindcss";

:root {
  --background: #090d16;
  --foreground: #f1f5f9;
}

body {
  background-color: var(--background);
  color: var(--foreground);
  font-family: ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
  overflow-x: hidden;
}

/* Custom scrollbars */
::-webkit-scrollbar {
  width: 8px;
  height: 8px;
}
::-webkit-scrollbar-track {
  background: #0f172a;
}
::-webkit-scrollbar-thumb {
  background: #334155;
  border-radius: 4px;
}
::-webkit-scrollbar-thumb:hover {
  background: #475569;
}

@keyframes pulse-subtle {
  0%, 100% { opacity: 0.6; }
  50% { opacity: 0.9; }
}

.animate-pulse-subtle {
  animation: pulse-subtle 4s ease-in-out infinite;
}
`;

  const compiler = await compile(baseCss, {
    base: path.join(__dirname, ".."),
    onDependency: () => {},
  });

  const compiled = compiler.build(Array.from(candidateSet));
  const outputPath = path.join(__dirname, "../src/app/globals.css");
  fs.writeFileSync(outputPath, compiled, "utf8");

  console.log(`Successfully compiled Tailwind CSS into ${outputPath} (${compiled.length} bytes)!`);
}

buildCss().catch((err) => {
  console.error("CSS compilation error:", err);
  process.exit(1);
});
