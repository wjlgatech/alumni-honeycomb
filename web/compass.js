/* The Calling Compass rule, in the browser. Same rule as companion/compass.py;
   both are held to the golden cases in data/compass.yml. Works in the page and in Node (tests). */
(function (root) {
  var DIM_ORDER = ["spirit", "mind", "heart", "strategy"];
  function levelFor(total, levels) {
    for (var i = 0; i < levels.length; i++) {
      if (levels[i].min <= total && total <= levels[i].max) return levels[i].id;
    }
    throw new Error("no level covers total " + total);
  }
  function score(answers, spec) {
    var qs = spec.questions;
    if (answers.length !== qs.length) throw new Error("expected " + qs.length + " answers");
    var totals = { spirit: 0, mind: 0, heart: 0, strategy: 0 };
    qs.forEach(function (q, i) {
      var a = answers[i];
      if ([0, 1, 2, 3].indexOf(a) < 0) throw new Error("each answer must be 0..3");
      totals[q.dim] += a;
    });
    var levels = {}, top = 0;
    spec.levels.forEach(function (b) { top = Math.max(top, b.max); });
    DIM_ORDER.forEach(function (d) { levels[d] = levelFor(totals[d], spec.levels); });
    var start = null;
    DIM_ORDER.forEach(function (d) {
      if (totals[d] < top && (start === null || totals[d] < totals[start])) start = d;
    });
    return { totals: totals, levels: levels, start: start };
  }
  var api = { score: score, DIM_ORDER: DIM_ORDER };
  if (typeof module !== "undefined" && module.exports) module.exports = api;
  else root.Compass = api;
})(this);
