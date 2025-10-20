# Root Makefile

SHELL := /usr/bin/env bash
.SHELLFLAGS := -o pipefail -c

NETSTACK := bootstrap/linux/netstack.sh
SETUP    := bootstrap/linux/setup.sh
RUNAPP   := bootstrap/linux/run_app.sh

define ensure_exec
	@chmod +x "$(1)" 2>/dev/null || true
endef

define run_or_fail
	@NETSTACK_DEBUG=$${DEBUG:-0} $(1) || { code=$$?; echo "[FAIL] $(2) (exit $$code)"; exit $$code; }
endef

.PHONY: help \
        setup-machine update-local-env update-server-env \
        start-server stop-server show-server-status show-server-logs \
        restart-server rotate-keys-and-restart-server \
        rotate-jwt rotate-api-key \
        start-admin stop-admin

help:
	@echo "==================== Commands ===================="
	@echo "setup-machine                  Install system deps + Python 3.11 + venv + pip + models + Ollama   [Run this first]"
	@echo "update-local-env               Create/merge .env for LOCAL dev (Gateway/API/Web)"
	@echo "update-server-env              Create/merge .env for SERVER/production (Requires DOMAIN=https://actual.domain)"
	@echo "start-server                   Start the stack (FastAPI (8000), Node.js (3000), Next.js (4000))"
	@echo "stop-server                    Stop the stack"
	@echo "show-server-status             Show tmux/background status"
	@echo "show-server-logs               Tail logs of the stack"
	@echo "restart-server                 Stop then start the stack"
	@echo "rotate-jwt                     Rotate JWT secret (forces all users to re-login)"
	@echo "rotate-api-key                 Rotate Gateway and API shared key (restart both services)"
	@echo "rotate-keys-and-restart-server Rotate BOTH JWT and Gateway/API keys, then restart (requires CONFIRM=YES)"
	@echo "start-admin                    Launch local Streamlit admin console"
	@echo "stop-admin                     Stop Streamlit admin"
	@echo "=================================================="

# 1) Machine setup (system + project resources)
setup-machine:
	$(call ensure_exec,$(SETUP))
	$(call run_or_fail,bash $(SETUP),setup-machine)

# 2) Environment configuration (.env only)
update-local-env:
	$(call ensure_exec,$(NETSTACK))
	$(call run_or_fail,bash $(NETSTACK) bootstrap,update-local-env)

# Usage: make update-server-env DOMAIN=https://actual.domain
update-server-env:
	$(call ensure_exec,$(NETSTACK))
	@if [ -z "$$DOMAIN" ]; then echo "Usage: make update-server-env DOMAIN=https://actual.domain"; exit 1; fi
	$(call run_or_fail,bash $(NETSTACK) bootstrap --prod $$DOMAIN,update-server-env)

# 3) Run stack
start-server:
	$(call ensure_exec,$(NETSTACK))
	$(call run_or_fail,bash $(NETSTACK) up,start-server)

stop-server:
	$(call ensure_exec,$(NETSTACK))
	$(call run_or_fail,bash $(NETSTACK) down,stop-server)

show-server-status:
	$(call ensure_exec,$(NETSTACK))
	$(call run_or_fail,bash $(NETSTACK) status,show-server-status)

show-server-logs:
	$(call ensure_exec,$(NETSTACK))
	$(call run_or_fail,bash $(NETSTACK) logs,show-server-logs)

# Convenience: restart = stop + start
restart-server:
	@$(MAKE) stop-server
	@$(MAKE) start-server

# 4) Keys maintenance
rotate-jwt:
	$(call ensure_exec,$(NETSTACK))
	$(call run_or_fail,bash $(NETSTACK) bootstrap --rotate-jwt,rotate-jwt)

rotate-api-key:
	$(call ensure_exec,$(NETSTACK))
	$(call run_or_fail,bash $(NETSTACK) bootstrap --rotate-api-key,rotate-api-key)

# Rotate BOTH keys, then restart. Require explicit confirmation.
# Usage: make rotate-keys-and-restart-server CONFIRM=YES
rotate-keys-and-restart-server:
	@if [ "$$CONFIRM" != "YES" ]; then \
		echo "Refusing to rotate keys without confirmation."; \
		echo "Usage: make rotate-keys-and-restart-server CONFIRM=YES"; \
		exit 1; \
	fi
	$(call ensure_exec,$(NETSTACK))
	$(call run_or_fail,bash $(NETSTACK) bootstrap --rotate-jwt --rotate-api-key,rotate-keys)
	@$(MAKE) restart-server

# 5) Admin console (Streamlit)
start-admin:
	$(call ensure_exec,$(RUNAPP))
	$(call run_or_fail,bash $(RUNAPP),start-admin)

stop-admin:
	@pkill -f "streamlit run" || true
	@echo "[OK] attempted to stop Streamlit"
