.PHONY:
	build
	build-src
	build-wheel
	ci
	clean
	dry-pypi
	git-undo
	git-update
	isort
	lint
	lint-docs
	pip-update
	precommit
	pypi-upload
	readme-check
	readme-desc
	test
	test-local
	testpypi-upload

build:
	python setup.py sdist bdist_wheel

build-src:
	python setup.py sdist

build-wheel:
	python setup.py bdist_wheel

ci:
	$(MAKE) isort
	$(MAKE) lint
	$(MAKE) lint-docs
	$(MAKE) test

clean:
	rm -rf .cache
	rm -rf .coverage
	rm -rf *.egg-info build dist
	rm -rf docs/_build
	rm -rf tmp

dry-pypi:
	python setup.py --dry-run sdist bdist_wheel upload -s -r https://test.pypi.org/legacy/

git-undo:
	git reset --soft

git-update:
	git add -A

isort:
	isort -rc simple_webpack django_simple_webpack docs tests --atomic --check-only --diff

lint:
	-flake8 simple_webpack django_simple_webpack docs tests
	-pylint simple_webpack django_simple_webpack docs/ tests

lint-docs:
	doc8 docs/ README.rst CHANGELOG --ignore D005 --ignore-path docs/_build

pip-update:
	$(eval UPDATED := $(shell pip list --outdated --pre --format=freeze | cut -d = -f 1))
	@pip list --outdated --pre --format=freeze | cut -d = -f 1 | xargs -n1 pip install -U --pre
	@printf "\n%s\n" "******************************************"
	@printf "%s\n" "PYTHON PACKAGES UPDATED"
	@printf "%s\n" "------------------------------------------"
	@$(foreach UPDATE,$(UPDATED),pip list --format=freeze | grep -E '$(UPDATE)==[[:digit:]]+\.[[:digit:]]+\.?[[:digit:]]*[\.-]?(a|b|c|pre|preview|rc)?[\.-]?[[:digit:]]*[\.-]?(dev)?[\.-]?[[:digit:]]*' | xargs -n1 -I {} echo "{}";)
	@printf "%s\n\n" "******************************************"

precommit:
	$(MAKE) pip-update
	$(MAKE) clean
	$(MAKE) isort
	$(MAKE) lint
	$(MAKE) lint-docs
	$(MAKE) test-local
	$(MAKE) readme-check

pypi-upload:
	python setup.py sdist bdist_wheel upload -s

readme-check:
	python setup.py check -r -s

readme-desc:
	python setup.py check -r -s
	@[ -d tmp ] || mkdir tmp; cd tmp; [ -d rst ] || mkdir rst
	python setup.py --long-description | rst2html.py > tmp/rst/README.html

# FIXME: Fix tox!!
test:
	tox -e

test-local:
	tox -e

testpypi-upload:
	python setup.py sdist bdist_wheel upload -s -r https://test.pypi.org/legacy/
