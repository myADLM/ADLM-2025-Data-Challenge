# LabDocs RAG (starter)

## Quickstart
1) Create and activate environment:
   conda create -n labdocs python=3.11 -y
   conda activate labdocs

2) Install:
   pip install -r requirements.txt

3) Build a small test index:
   python index.py --data_dir ./data_raw --index_dir ./index --limit_files 5

4) Run the app:
   streamlit run app.py
