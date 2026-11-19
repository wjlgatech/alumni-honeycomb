// The browser compass (web/compass.js) must agree with every golden case in data/compass.yml,
// read through the generated web/data.json (the same data the page reads).
import { readFileSync } from "node:fs";
import { createRequire } from "node:module";
const require = createRequire(import.meta.url);
const Compass = require("../web/compass.js");
const data = JSON.parse(readFileSync(new URL("../web/data.json", import.meta.url), "utf8"));
let failed = 0;
for (const c of data.compass.golden) {
  const r = Compass.score(c.answers, data.compass);
  const ok = JSON.stringify(r.levels) === JSON.stringify(Object.fromEntries(Compass.DIM_ORDER.map(d => [d, c.levels[d]]))) && r.start === c.start;
  if (!ok) { failed++; console.log("FAIL", c.answers, r); }
}
console.log(failed ? `${failed} golden case(s) failed` : `ok: ${data.compass.golden.length} golden cases`);
process.exit(failed ? 1 : 0);
