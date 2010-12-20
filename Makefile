MODULE=scss

clean:
	sudo rm -rf build dist $(MODULE).egg-info/
	find . -name "*.pyc" -delete

install: remove _install clean

remove:
	sudo pip uninstall $(MODULE)

_install:
	sudo pip install -U .

test:
	python tests/test_$(MODULE).py
