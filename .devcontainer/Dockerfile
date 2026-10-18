FROM mcr.microsoft.com/devcontainers/python:3.11-bookworm

# Cache git credentials in-memory for 8 hours so pushes don't re-prompt each
# time. Run as the container's vscode user (the runtime user) so `--global`
# lands in /home/vscode/.gitconfig instead of root's.
RUN su - vscode -c "git config --global credential.helper 'cache --timeout=28800'"