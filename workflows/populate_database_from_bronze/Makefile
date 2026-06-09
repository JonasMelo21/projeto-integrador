.PHONY: help install run test build push deploy clean

# Colors
GREEN  := \033[0;32m
YELLOW := \033[0;33m
RED    := \033[0;31m
NC     := \033[0m

help:
	@echo "$(GREEN)Populate Database from Bronze - Make Targets$(NC)"
	@echo ""
	@echo "$(YELLOW)Development:$(NC)"
	@echo "  make install        Install dependencies"
	@echo "  make run            Run pipeline locally"
	@echo "  make run-debug      Run with DEBUG logging"
	@echo "  make test           Test Azure connection"
	@echo ""
	@echo "$(YELLOW)Docker:$(NC)"
	@echo "  make build          Build Docker image"
	@echo "  make run-docker     Run in Docker container"
	@echo ""
	@echo "$(YELLOW)Azure Deployment:$(NC)"
	@echo "  make push           Push to Azure Container Registry"
	@echo "  make deploy         Deploy to Container Apps"
	@echo "  make deploy-all     Build, push, and deploy"
	@echo ""
	@echo "$(YELLOW)Maintenance:$(NC)"
	@echo "  make clean          Remove temporary files"
	@echo "  make logs           Show last logs"
	@echo "  make db-check       Check database status"

install:
	$(info $(GREEN)📦 Installing dependencies...$(NC))
	pip install -r requirements.txt

run:
	$(info $(GREEN)🚀 Running pipeline...$(NC))
	python main.py

run-debug:
	$(info $(GREEN)🐛 Running with DEBUG logging...$(NC))
	LOG_LEVEL=DEBUG python main.py

test:
	$(info $(GREEN)🧪 Testing Azure Storage connection...$(NC))
	python -c "from azure.identity import DefaultAzureCredential; from azure.storage.blob import BlobServiceClient; client = BlobServiceClient('https://rentmasterstorageaccount.blob.core.windows.net', DefaultAzureCredential()); print('✅ Connection OK')"

build:
	$(info $(GREEN)🐳 Building Docker image...$(NC))
	docker build -t populate-db:latest .
	$(info $(GREEN)✅ Image built$(NC))

run-docker:
	$(info $(GREEN)🚀 Running in Docker...$(NC))
	docker run \
		--env-file .env \
		-v $(PWD)/data:/data \
		populate-db:latest

push:
	$(info $(GREEN)📤 Pushing to Azure Container Registry...$(NC))
	az acr build \
		--registry rentmasteracr \
		--image populate-db:latest \
		.
	$(info $(GREEN)✅ Image pushed$(NC))

deploy:
	$(info $(GREEN)🚀 Deploying to Container Apps...$(NC))
	bash deploy.sh deploy

deploy-all:
	$(info $(GREEN)🚀 Build → Push → Deploy$(NC))
	make build
	make push
	make deploy

logs:
	$(info $(GREEN)📋 Showing Container App logs...$(NC))
	az containerapp logs show \
		--name populate-db \
		--resource-group rg_rent_master_dev

db-check:
	$(info $(GREEN)📊 Checking database...$(NC))
	@if [ -f "$(DB_PATH)" ]; then \
		echo "✅ Database exists: $(DB_PATH)"; \
		sqlite3 "$(DB_PATH)" "SELECT COUNT(*) as total_properties FROM imoveis;" 2>/dev/null || echo "⚠️  Table not found yet"; \
	else \
		echo "❌ Database not found: $(DB_PATH)"; \
	fi

clean:
	$(info $(GREEN)🧹 Cleaning...$(NC))
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	$(info $(GREEN)✅ Cleaned$(NC))

.DEFAULT_GOAL := help
