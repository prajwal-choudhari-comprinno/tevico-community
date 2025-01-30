set -e

echo -ne 'Setup in progress...\n'
echo -ne 'Cleaning up previous builds...\n'
cd /tmp
rm -rf tevico-community

# Read branch from argument (default to 'main' if not provided)
BRANCH=${1:-main}

echo -ne "Cloning the repository (branch: $BRANCH)...\n"
git clone -b "$BRANCH" https://github.com/comprinnotech/tevico-community.git > /dev/null 2> /dev/null
cd tevico-community

echo -ne 'Setting up virtual environment...\n'
python3 -m venv .venv
source .venv/bin/activate

echo 'Installing dependencies...\n'

echo -ne '#####                     (33%)\r'
pip3 install poetry > /dev/null 2> /dev/null

echo -ne '#############             (66%)\r'
poetry install > /dev/null 2> /dev/null

echo -ne '#######################   (100%)\r'
echo -ne '\n'

echo -ne 'Running the application...\n'
/tmp/tevico-community/main run
