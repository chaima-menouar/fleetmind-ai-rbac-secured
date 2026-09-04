# GitHub upload

Recommended repository name: **fleetmind-ai**

Create an empty public repository with that name. Do not initialize it with a
README, .gitignore, or license because the project already contains them.

Open PowerShell inside the extracted fleetmind-ai folder and run:

~~~powershell
git init
git config user.name "Chaima Menouar"
git config user.email "YOUR_REAL_GITHUB_EMAIL"
git add .
git commit -m "Initial commit: FleetMind AI functional MVP"
git branch -M main
git remote add origin https://github.com/chaima-menouar/fleetmind-ai.git
git push -u origin main
~~~

Replace YOUR_REAL_GITHUB_EMAIL before committing. The .gitignore excludes
dependencies, generated builds, caches, and local environment files.

After the push, open the repository's **Actions** tab. All three CI jobs should
pass: backend, frontend, and infrastructure.
