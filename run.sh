echo 'Setup in progress...\n'

echo 'Cleaning up previous builds...\n'
cd /tmp
rm -rf tevico-community

echo 'Cloning the repository...\n'
git clone -b dev https://github.com/comprinnotech/tevico-community.git
cd tevico-community

echo 'Setting up virtual environment...\n'
python3 -m venv .venv
source .venv/bin/activate

echo 'Installing dependencies...'

echo -ne '#####                     (33%)\r'
sleep 1
pip3 install poetry > /dev/null
echo -ne '#############             (66%)\r'
sleep 1
poetry install > /dev/null
echo -ne '#######################   (100%)\r'
echo -ne '\n'

echo 'Running the application...\n'
/tmp/tevico-community/main run