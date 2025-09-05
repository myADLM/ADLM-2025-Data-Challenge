FRONT_END_DIR=./app/frontend
BACK_END_DIR=./app/backend

download-pdfs:
	curl -L -C - -o ./resources/labdocs.zip \
    "https://zenodo.org/records/16328490/files/LabDocs.zip?download=1"
	unzip -o ./resources/labdocs.zip -d ./resources/

build-backend:
# Build the backend application
	@echo "Building backend application..."
	cd $(BACK_END_DIR) && uv sync

build-frontend:
# Build the frontend application
	@echo "Building frontend application..."
	cd $(FRONT_END_DIR) && npm install && npm run build

run-frontend:
# Run the frontend application in development mode
	@echo "Running frontend application in development mode..."
	$(MAKE) build-frontend
	cd $(FRONT_END_DIR) && npm run dev