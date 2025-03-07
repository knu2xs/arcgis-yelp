.PHONY: data clean docs env env_remove jupyter env_build create_kernel test black

#################################################################################
# GLOBALS                                                                       #
#################################################################################

PROJECT_DIR := $(shell dirname $(realpath $(lastword $(MAKEFILE_LIST))))
PROJECT_NAME = arcgis-yelp
ENV = $(PROJECT_DIR)/env

#################################################################################
# COMMANDS                                                                      #
#################################################################################

## Make Dataset
data:
	conda run -p $(ENV) python scripts/make_data.py

## Delete all compiled Python files
clean:
	find . -type f -name "*.py[co]" -delete
	find . -type d -name "__pycache__" -delete

## Build the docs
docs:
	conda run -p $(ENV) sphinx-build -a -b html docsrc docs
	@echo ">>> Documents successfully built and saved to ./docs!"

## Build the local environment from the environment file
env:
	conda env create -p $(ENV) -f environment.yml
	conda run -p $(ENV) pip install -e .
	@echo ">>> New conda environment created. Activate with:\n- conda activate -p $(ENV)"

## Make it easier to clean up the project when finished
env_remove:
	conda env remove -p $(ENV)

## Run jupyter without having to explicitly activate the environment
jupyter:
	conda run -p $(ENV) jupyter lab

## If working in an EC2 environment, set everything up - BETA FEATURE
ec2:

	# get install and configure miniconda
	wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh -O ~/miniconda.sh
	~/miniconda.sh -b -p $(HOME)/miniconda
	~/miniconda/bin/conda init
	sed -i '1 i\export PATH=/home/ubuntu/miniconda/bin:$PATH' ~/.bashrc

	# create and activate the project conda environment
	~/miniconda/bin/conda env create -f ./environment.yml
	~/miniconda/bin/conda activate $(ENV_NAME)

	# install the local package
	python -m pip install -e .

	# configure jupyter for remote access with password "jovyan"
	jupyter notebook --generate-config
	sed -i '1 i\c.NotebookApp.port = 8888' ~/.jupyter/jupyter_notebook_config.py
	sed -i '1 i\c.NotebookApp.password = u"sha1:b37cb398255d:3f676cfe9b00e0c485385b435584ae5518bd14a4"' ~/.jupyter/jupyter_notebook_config.py
	sed -i '1 i\c.NotebookApp.ip = "0.0.0.0"' ~/.jupyter/jupyter_notebook_config.py

## create a new kernel
create_kernel:
	conda run -p $(ENV) python -m ipykernel install --user --name $(ENV_NAME) --display-name "$(PROJECT_NAME)"

## Run all tests in module
test:
	conda run -p $(ENV) python -m pytest

## Black formatting
black:
	conda run -p $(ENV) python -m black /src

#################################################################################
# PROJECT RULES                                                                 #
#################################################################################



#################################################################################
# Self Documenting Commands                                                     #
#################################################################################

.DEFAULT_GOAL := help

# Inspired by <http://marmelab.com/blog/2016/02/29/auto-documented-makefile.html>
# sed script explained:
# /^##/:
# 	* save line in hold space
# 	* purge line
# 	* Loop:
# 		* append newline + line to hold space
# 		* go to next line
# 		* if line starts with doc comment, strip comment character off and loop
# 	* remove target prerequisites
# 	* append hold space (+ newline) to line
# 	* replace newline plus comments by `---`
# 	* print line
# Separate expressions are necessary because labels cannot be delimited by
# semicolon; see <http://stackoverflow.com/a/11799865/1968>
.PHONY: help
help:
	@echo "$$(tput bold)Available rules:$$(tput sgr0)"
	@echo
	@sed -n -e "/^## / { \
		h; \
		s/.*//; \
		:doc" \
		-e "H; \
		n; \
		s/^## //; \
		t doc" \
		-e "s/:.*//; \
		G; \
		s/\\n## /---/; \
		s/\\n/ /g; \
		p; \
	}" ${MAKEFILE_LIST} \
	| LC_ALL='C' sort --ignore-case \
	| awk -F '---' \
		-v ncol=$$(tput cols) \
		-v indent=19 \
		-v col_on="$$(tput setaf 6)" \
		-v col_off="$$(tput sgr0)" \
	'{ \
		printf "%s%*s%s ", col_on, -indent, $$1, col_off; \
		n = split($$2, words, " "); \
		line_length = ncol - indent; \
		for (i = 1; i <= n; i++) { \
			line_length -= length(words[i]) + 1; \
			if (line_length <= 0) { \
				line_length = ncol - indent - length(words[i]) - 1; \
				printf "\n%*s ", -indent, " "; \
			} \
			printf "%s ", words[i]; \
		} \
		printf "\n"; \
	}' \
	| more $(shell test $(shell uname) = Darwin && echo '--no-init --raw-control-chars')
