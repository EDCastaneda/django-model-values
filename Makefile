all: check html

clean:
	make -C docs $@
	hg st -in | xargs rm
	rm -rf dist django_model_values.egg-info .tox

html:
	make -C docs $@ SPHINXOPTS=-W
	rst2$@.py README.rst docs/_build/README.$@

dist: html
	python setup.py sdist
	cd docs/_build/html && zip -r ../../../$@/docs.zip .

check:
	python setup.py $@ -mrs
	flake8
	py.test-2.7 --cov
	py.test-3.5 --cov --cov-append --cov-fail-under=100