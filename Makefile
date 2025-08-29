download-pdfs:
	curl -L -C - -o ./resources/labdocs.zip \
    "https://zenodo.org/records/16328490/files/LabDocs.zip?download=1"
	unzip -o ./resources/labdocs.zip -d ./resources/