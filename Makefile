.PHONY: build check test score score-bump demo deploy live-check discover

build:        ## feeds -> federation/index.json -> web/data.json, and the icons
	python3 -m honeycomb publish hives/example/hive.yml
	python3 -m honeycomb publish hives/example-b/hive.yml
	python3 -m honeycomb federation pull
	python3 -m honeycomb build
	python3 -m honeycomb discovery card
	python3 scripts/icons.py web >/dev/null

test:         ## unit + golden + browser-compass + page tests
	python3 -m pytest -q tests

score:        ## quality ratchet: gate on data/quality-floor.json
	python3 scripts/score.py --no-write

score-bump:   ## raise the floor, only after a real gain
	python3 scripts/score.py --bump

check:        ## the finish line: drift + charter + federation + tests + quality floor
	python3 -m honeycomb build --check
	python3 -m honeycomb check hives/example/hive.yml
	python3 -m honeycomb federation check
	python3 -m honeycomb publish hives/example/hive.yml --check
	python3 -m honeycomb publish hives/example-b/hive.yml --check
	python3 -m honeycomb federation pull --check
	python3 -m honeycomb discovery card --check
	python3 -m honeycomb member check hives/example/members/lin.yml
	$(MAKE) test score

demo:         ## open the site locally at http://127.0.0.1:8799
	cd web && python3 -m http.server 8799

deploy: check ## publish web/ to Vercel production, then check the live site
	vercel --prod --yes
	python3 scripts/live_check.py https://alumni-honeycomb.vercel.app
	$(MAKE) live-check

live-check:   ## every asset the page needs returns 200 at the public address (futuremake.io/honeycomb)
	python3 scripts/live_check.py

mirror:       ## publish web/ to GitHub Pages (the mainland-China-reachable mirror), then check it
	./scripts/publish_mirror.sh
	python3 scripts/live_check.py https://wjlgatech.github.io/alumni-honeycomb

china:        ## measure the live URL and the mirror from mainland China probes (Globalping, free)
	python3 scripts/china_probe.py

discover:     ## pre-launch 1:1s on the PRIVATE files: whom to meet, then the tally
	python3 -m honeycomb discovery plan hives-private/discovery/people.yml
	python3 -m honeycomb discovery tally hives-private/discovery/interviews.yml
