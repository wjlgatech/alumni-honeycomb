.PHONY: build check test score score-bump demo deploy live-check

build:        ## data/*.yml -> web/data.json, and the icons
	python3 -m honeycomb build
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
	$(MAKE) test score

demo:         ## open the site locally at http://127.0.0.1:8799
	cd web && python3 -m http.server 8799

deploy: check ## publish web/ to Vercel production, then check the live site
	vercel --prod --yes
	$(MAKE) live-check

live-check:   ## every asset the live page needs returns 200
	python3 scripts/live_check.py
