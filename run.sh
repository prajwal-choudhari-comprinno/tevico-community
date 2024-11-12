cd /tmp
rm -rf tevico-community
git clone -b dev https://github.com/comprinnotech/tevico-community.git
cd tevico-community
python3 -m venv .venv
source .venv/bin/activate
pip3 install poetry
poetry install