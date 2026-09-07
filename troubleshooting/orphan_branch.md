## Background

One of my friends which is me 😉, has messed up a project from all corners. Not that the project was giving any errors but somehow I myself couldn't figure out why something is happening; A classic case of using coding tools without understanding it 🙈. So, I decided to start everything from scratch in a new branch but not a new repo. The solution? an <u>***orphan branch***</u>.

An <u>***orphan branch***</u> is nothing but creating an empty branch even though you have main (or other) branch exists.

## Challenge

While this is possible but cannot be created in GitHub. Creating an orphan branch can be done locally with Git. Then push it to GitHub and it will appear on GitHub like a regular branch.

## Steps

1. Clone your repo locally:

```bash
git clone <your-github-repo>
```

2. Create a new orphan branch:

```bash
git checkout --orphan <branch-name>
```

3. Remove the files from `main` that are now in your working tree:

```bash
git rm -rf .
```

4. Add something on this newly created branch:

```bash
echo "dev from scratch" > README.md
git add README.md
git commit -m "initial commit on new branch"
```

5. Push it to GitHub:

```bash
git push -u origin <new-branch>
```

6. Go to GitHub and you'll see the new-branch in the branch-selector.