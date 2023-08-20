DOCKER_IMAGE = executor
DOCKER_PORT = 80:80
DOCKER_ENV_FILE = .env

SERVICE = code
SECRETS_LOCATION = ./.env
PROJECT_ID = voicing-391015
REGION = europe-central2


# Targets
.PHONY: build run

build:
	docker build . -t $(DOCKER_IMAGE):latest
run:
	docker run -p $(DOCKER_PORT) -it --env-file $(DOCKER_ENV_FILE) $(DOCKER_IMAGE):latest
clean:
	autoflake --remove-all-unused-imports -i src/*
	black src/
	isort src/

cloud_run:
	gcloud run deploy $(DOCKER_IMAGE) --source . --region europe-central2 --allow-unauthenticated

update_secrets:
	@ENV_VARS=$$(awk -F "=" '{print $$1"="substr($$0, index($$0, $$2))}' .env | tr '\n' ',') ;\
	echo "Environment variables to update: $$ENV_VARS" ;\
	gcloud run services update $(SERVICE) --project $(PROJECT_ID) --region $(REGION) --update-env-vars $$ENV_VARS
