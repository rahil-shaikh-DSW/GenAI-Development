

---

### ✅ Prerequisites
Make sure you’ve done the following first:
- Installed Git
- Initialized a git repo in your project folder (`git init`)
- Added the remote URL (`git remote add origin https://github.com/rahil-shaikh-DSW/GenAI-Development.git`)
- You have access rights to push to the repo

---

### 🚀 Git Commands to Push to `main` Branch

Open your terminal or command prompt and navigate to your project directory, then run:

```bash
# 1. Stage all changes
git add .

# 2. Commit changes
git commit -m "Your commit message here"

# 3. Set the main branch (if not already set)
git branch -M main

# 4. Add remote if not already added
git remote add origin https://github.com/rahil-shaikh-DSW/GenAI-Development.git

# 5. Push to the main branch
git push -u origin main
```

---

### 🧠 Notes
- If you've already added the remote before, skip step 4 (or you’ll get a remote already exists error).
- The `-u` flag in the push command links your local `main` to the remote `main`, so future pushes can just be `git push`.

---

Want help with setting this up for a specific folder? Or are you running into any errors?