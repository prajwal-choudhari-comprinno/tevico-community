# Project Setup

The Tevico Community project is designed to run seamlessly on cloud service providers like AWS CloudShell. To get started quickly, copy and execute the following command in your CloudShell terminal:

```bash title="Execute this in your Cloudshell"
curl https://raw.githubusercontent.com/comprinnotech/tevico-community/refs/heads/main/run.sh?ts=$(date +%s) | bash
```

This command will download and execute the setup script, allowing you to get up and running with minimal effort.

For more customization options, you can use various CLI parameters. To take full advantage of these options, you will need to **set up the project** locally.

---

**TLDR;** You just want to copy paste and setup the project here's a snippet for you! Once you execute these commands, you can skip the **Project Setup** section.

```bash title="TLDR; Project Setup"
git clone https://github.com/comprinnotech/tevico-community.git
cd tevico-community

python3 -m venv .venv
source .venv/bin/activate

pip3 install poetry
poetry install
```

---

## Project Setup

Setting up the project involves a few simple steps. Follow the instructions below to get your environment ready.

**Step 1**: Clone the repository to your local machine. This will download all the necessary files for the project.

```bash title="Clone repo"
git clone https://github.com/comprinnotech/tevico-community.git

cd tevico-community
```

**Step 2**: Create a Python virtual environment and activate it. This ensures that all dependencies are installed in an isolated environment, preventing conflicts with other projects.

```bash title="Initialise Virtual Environment"
python3 -m venv .venv

source .venv/bin/activate
```

**Step 3**: Install Poetry, a dependency management tool for Python. Poetry will help you manage the project's dependencies and virtual environments more efficiently.

```bash title="Setup Poetry"
pip3 install poetry
```

**Step 4**: Use Poetry to install all the project dependencies. This will download and install all the required packages specified in the `pyproject.toml` file.

```bash title="Install Dependencies"
poetry install
```

The project setup is now complete! For information on how to run the project using various command-line parameters, please refer to the [CLI Parameters](cli-params.md) page.