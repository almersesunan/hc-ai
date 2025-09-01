# AI-Powered Human Capital System
**An AI-Powered Human Capital System represents the next generation of HR technology, \
moving beyond traditional administrative functions to a strategic, data-driven platform. \
By leveraging artificial intelligence and machine learning, this system provides unprecedented \
insights into workforce dynamics, automates complex processes, and empowers leaders to make fairer, \
faster, and more effective decisions.**

# Create virtual environment
python -m venv venv

# Activate virtual environment
venv\Scripts\activate

# open port 
sudo ufw allow <port>/tcp

# SSL Issue #1 on pip install (presumably only on venv):
pip install --trusted-host pypi.org --trusted-host files.pythonhosted.org <package to install>

# SSL Issue #2 certificate on SerpAPI:
pip install --trusted-host pypi.org --trusted-host files.pythonhosted.org pip-system-certs --use-feature=truststore

# SSL Issue #3 set param on GenAI Config
set transport='rest'

