#!/usr/bin/env bash
# Publish web/ to the gh-pages branch: the GitHub Pages mirror that mainland China can reach.
# (*.vercel.app is DNS-poisoned in mainland China; *.github.io was reachable from 6/6 mainland probes on 2026-11-19.)
set -euo pipefail
cd "$(dirname "$0")/.."
sha=$(git subtree split --prefix web HEAD)
git push --force origin "$sha:refs/heads/gh-pages"
echo "pushed web/ ($sha) to gh-pages"
