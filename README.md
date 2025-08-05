Personal note for Almer
SSL issue on pip install (presumably only on venv):
pip install --trusted-host pypi.org --trusted-host files.pythonhosted.org <package to install>

SSL issue certificate on serpapi:
pip install --trusted-host pypi.org --trusted-host files.pythonhosted.org pip-system-cert --use-feature=truststore