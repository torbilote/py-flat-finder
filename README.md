# py-template
py-template

py -m pip install poetry

poetry add <dependency>

black .

isort . --profile black

pylint --rcfile .pylintrc --output-format=colorized .

mypy --config-file mypy.ini --strict .

pytest -vv
