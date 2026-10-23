FROM mcr.microsoft.com/devcontainers/python:3.11-bookworm

# The Dev Containers extension populates /etc/gitconfig with a host-keychain
# credential helper that stores secrets in the host keychain (non-ephemeral)
# and can intercept the terminal PAT prompt. Ignore the system gitconfig so
# git relies solely on the in-memory cache helper configured below.
ENV GIT_CONFIG_NOSYSTEM=1

# Cache git credentials in-memory for 8 hours so pushes don't re-prompt each
# time. Run as the container's vscode user (the runtime user) so `--global`
# lands in /home/vscode/.gitconfig instead of root's.
RUN su - vscode -c "git config --global credential.helper 'cache --timeout=28800'"

# Project Python dependencies (phase 1: Wikipedia extraction + tests).
RUN pip install --no-cache-dir \
    'mwparserfromhell>=0.6' \
    'PyYAML>=6.0' \
    'requests>=2.31' \
    'pytest>=8.0'

RUN mkdir -p /home/vscode/.vscode-server/data/User/globalStorage \
    && chown -R vscode:vscode /home/vscode/.vscode-server
    