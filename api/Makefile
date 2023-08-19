DOCKER_IMAGE = lablabai_executor
DOCKER_PORT = 80:80
DOCKER_ENV_FILE = .env

SERVICE = code
SECRETS_LOCATION = ./.env
PROJECT_ID = voicing-391015
REGION = europe-central2


# Targets
.PHONY: build run

build:
	docker build . -t $(DOCKER_IMAGE)
run:
	docker run --privileged -p $(DOCKER_PORT) -it --env-file $(DOCKER_ENV_FILE) -v /var/run/docker.sock:/var/run/docker.sock $(DOCKER_IMAGE)
clean:
	autoflake --remove-all-unused-imports -i src/*
	black src/
	isort src/

update_secrets:
	@ENV_VARS=$$(awk -F "=" '{print $$1"="substr($$0, index($$0, $$2))}' .env | tr '\n' ',') ;\
	echo "Environment variables to update: $$ENV_VARS" ;\
	gcloud run services update $(SERVICE) --project $(PROJECT_ID) --region $(REGION) --update-env-vars $$ENV_VARS
