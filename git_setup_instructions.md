# GitHub Authentication Setup for Tenxsom AI

## Problem
GitHub no longer supports password authentication for git operations over HTTPS as of August 13, 2021.

## Solutions

### Option 1: Personal Access Token (Recommended)
1. Go to GitHub.com → Settings → Developer settings → Personal access tokens → Tokens (classic)
2. Click "Generate new token (classic)"
3. Give it a descriptive name (e.g., "Tenxsom AI Development")
4. Select scopes (at minimum, select "repo" for full repository access)
5. Generate the token and copy it immediately (you won't see it again)

Then clone using:
```bash
git clone https://<your-token>@github.com/nsfwhubinfo/tenxsom_ai.git
```

Or configure git to use the token:
```bash
git config --global credential.helper store
git clone https://github.com/nsfwhubinfo/tenxsom_ai.git
# When prompted for password, use your personal access token
```

### Option 2: SSH Key Authentication
1. Generate an SSH key if you don't have one:
```bash
ssh-keygen -t ed25519 -C "your_email@example.com"
```

2. Add the SSH key to ssh-agent:
```bash
eval "$(ssh-agent -s)"
ssh-add ~/.ssh/id_ed25519
```

3. Copy your public key:
```bash
cat ~/.ssh/id_ed25519.pub
```

4. Add it to GitHub: Settings → SSH and GPG keys → New SSH key

5. Clone using SSH:
```bash
git clone git@github.com:nsfwhubinfo/tenxsom_ai.git
```

### Option 3: GitHub CLI
1. Install GitHub CLI:
```bash
# For Ubuntu/Debian
curl -fsSL https://cli.github.com/packages/githubcli-archive-keyring.gpg | sudo dd of=/usr/share/keyrings/githubcli-archive-keyring.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main" | sudo tee /etc/apt/sources.list.d/github-cli.list > /dev/null
sudo apt update
sudo apt install gh
```

2. Authenticate:
```bash
gh auth login
```

3. Clone with gh:
```bash
gh repo clone nsfwhubinfo/tenxsom_ai
```

## Current Directory Structure
You're already in the Tenxsom_AI directory. If this is your existing project and you want to:

### Push existing code to the new repository:
```bash
git remote add origin https://github.com/nsfwhubinfo/tenxsom_ai.git
git branch -M main
git push -u origin main
```

### Or if you want to sync with the remote repository:
```bash
# After setting up authentication
git remote add origin https://github.com/nsfwhubinfo/tenxsom_ai.git
git fetch origin
git pull origin main --allow-unrelated-histories
```

## Note
The repository name appears to be "tenxsom_ai" (lowercase) in the URL. Make sure this matches the actual repository name on GitHub.