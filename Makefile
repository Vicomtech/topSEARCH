default:
	@printf "$$HELP"

help:
	@printf "$$HELP"

docker-run:
	docker build -t <image_name> .
	docker run [-e <PARAM_NAME>=<param_value>] <image_name> python <main_script_path>

docker-tests:
	docker build -t <image_name> .
	docker run [-e <PARAM_NAME>=<param_value>] <image_name> python -m pytest

define HELP
Please execute "make <command>". Example: make help
Available commands
        - make docker-run\t Generate the docker image , install the requirements and run it
        - make docker-tests\t Generate the docker image , install the requirements and run the tests

endef

export HELP
