# Deploy pages workflows

When you update the `mkdocs.yml` file or any file in the `docs` folder, you trigger one of two GitHub Actions workflows. These workflows keep the deployed version of the documentation site up to date with the documents in the `main` branch.

Both workflows triggers a workflow called `deploy-pages.yml`. This workflow runs the `mkdocs gh-deploy` command. To make sure that the command only pushes the most recent documentation, the workflow has a concurrency lock. The lock cancels any running actions and launches a new one when it's triggered.

## auto-deploy-pages

This workflow runs when a pull request has met the following criteria:

* It has been merged into the `main` branch.
* It includes changes to the `mkdocs.yml` file or any file in the `docs` directory.

## man-deploy-pages

This workflow runs when a direct push meets the following criteria:

* It is to the `main` branch.
* It includes changes to the `mkdocs.yml` file or any file in the `docs` directory.

To trigger this flow manually, use the [GitHub Actions extension][1] in VS Code.

[1]: https://marketplace.visualstudio.com/items?itemName=GitHub.vscode-github-actions
