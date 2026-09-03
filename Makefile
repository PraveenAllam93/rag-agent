DEV_CONTEXT  := desktop-linux
PROD_CONTEXT := allamh

DEV_ENV  := .env.dev
PROD_ENV := .env.prod

.PHONY: dev-services-up dev-services-down dev-services-logs dev-services-ps \
        dev-api-up dev-api-down dev-api-logs dev-api-ps \
        prod-services-up prod-services-down prod-services-logs prod-services-ps \
        prod-api-up prod-api-down prod-api-logs prod-api-ps

# --- dev (local Docker Desktop, context: desktop-linux, env: .env.dev) ---

dev-services-up:
	docker --context $(DEV_CONTEXT) compose --env-file $(DEV_ENV) -f docker-compose.yml -f docker-compose.dev.yml up -d

dev-services-down:
	docker --context $(DEV_CONTEXT) compose --env-file $(DEV_ENV) -f docker-compose.yml -f docker-compose.dev.yml down

dev-services-logs:
	docker --context $(DEV_CONTEXT) compose --env-file $(DEV_ENV) -f docker-compose.yml -f docker-compose.dev.yml logs -f

dev-services-ps:
	docker --context $(DEV_CONTEXT) compose --env-file $(DEV_ENV) -f docker-compose.yml -f docker-compose.dev.yml ps

dev-api-up:
	docker --context $(DEV_CONTEXT) compose --env-file $(DEV_ENV) -f docker-compose.api.yml up -d --build

dev-api-down:
	docker --context $(DEV_CONTEXT) compose --env-file $(DEV_ENV) -f docker-compose.api.yml down

dev-api-logs:
	docker --context $(DEV_CONTEXT) compose --env-file $(DEV_ENV) -f docker-compose.api.yml logs -f

dev-api-ps:
	docker --context $(DEV_CONTEXT) compose --env-file $(DEV_ENV) -f docker-compose.api.yml ps

# --- prod (remote homelab over SSH, context: allamh, env: .env.prod) ---

prod-services-up:
	docker --context $(PROD_CONTEXT) compose --env-file $(PROD_ENV) -f docker-compose.yml up -d

prod-services-down:
	docker --context $(PROD_CONTEXT) compose --env-file $(PROD_ENV) -f docker-compose.yml down

prod-services-logs:
	docker --context $(PROD_CONTEXT) compose --env-file $(PROD_ENV) -f docker-compose.yml logs -f

prod-services-ps:
	docker --context $(PROD_CONTEXT) compose --env-file $(PROD_ENV) -f docker-compose.yml ps

prod-api-up:
	docker --context $(PROD_CONTEXT) compose --env-file $(PROD_ENV) -f docker-compose.api.yml up -d --build

prod-api-down:
	docker --context $(PROD_CONTEXT) compose --env-file $(PROD_ENV) -f docker-compose.api.yml down

prod-api-logs:
	docker --context $(PROD_CONTEXT) compose --env-file $(PROD_ENV) -f docker-compose.api.yml logs -f

prod-api-ps:
	docker --context $(PROD_CONTEXT) compose --env-file $(PROD_ENV) -f docker-compose.api.yml ps
