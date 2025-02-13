---
title: "All the ways to `git add`"
date: 2024-10-24T20:26:20+05:30
draft: false
tags: ["git"]
canonicalUrl: https://aqademic.substack.com/p/all-the-ways-to-git-add
ShowBreadCrumbs: true
categories: ["tools"]
---

I always get confused with, should I run `git add .`, or should I run `git add --all`, or should I run `git add -A`? Given all these commands, do a similar thing, confusion is bound to happen. Thankfully, it's not just [me](https://stackoverflow.com/questions/23003118/any-difference-between-git-add-and-git-add-all#:~:text=git%20add%20%2D%2Dall%20will,git%20add%20.). So I decided to take a deep dive into `add` command of `git`, to end this confusion once and for all.

## What does `add` even do?

The `add` command adds your changes to staging area. Staging area is a buffer zone where you place your files before committing them. This buffer zone allows you to be selective with your commits, there are some files that you want to commit now and some files that you want to commit later. Staging area is also known as `index`.

`git` maintains the `index` in a file located at `.git/index` in a binary format. We can use `git ls-files --stage` command which interprets the binary data of `index` file and presents it in a human-readable format.

```bash
❯ git ls-files --stage
100644 4d0056ce61ad17b3fec9e285b5c41d5cb405040a 0       .github/workflows/gh-pages.yml
100644 89af1b0cdcdba0b5457d5bb4375ca4ca5f6116f9 0       .gitmodules
100644 e69de29bb2d1d6434b8b29ae775ad8c2e48c5391 0       .hugo_build.lock
...
...
...
```

- The first column describes the file `<mode>`, indicating the type and permission of file. `100644` means a regular non-executable file. Other valid values are: `100755` which means an executable file, `120000` which means a symbolic link.
- The second column is the `SHA-1` hash of the file's content, referencing the corresponding blob object.
- The third column is `<stage>` number which is used during merging.
- The fourth column is the relative path of the file within the repository.

When you run `git add <filename>`, `git` computes the `SHA-1` hash of the file's content, creates a blob object and stores it in `.git/objects/`. The blob objects are identified by their SHA-1 hash. It then updates the `index` file by adding or modifying the entry for the file.

## All the ways to `git add`

- Running `git add .` adds the changes from your current working directory to staging area.
- Running `git add --all` adds the changes from the repository to the staging area. This is irrespective of your working directory.
  - Working directory and repository means different things in git. Working directory is where you make changes and repository is where git records the history of those changes.
  - Your project can have multiple directories, and this command will stage changes from all of them.
- `git add -A` is same as `git add --all`.
- Running `git add *` can have the same effect as `git add .`. But note that `*` is not a git feature but shells' feature. The `*` globbing pattern will match all the files inside the working directory and add them, including even the dot files.
- You can also add changes interactively, using `git add -i`.
- You can also add changes selectively, using `git add -p <filename>`. This will open an interactive window, allowing you to select which edits within the `<filename>` you want to stage.

## How do you undo the `add`?

You can undo the `add` by running `git reset HEAD -- <filename>`. By default, the `reset` command runs with `--mixed` option, which means it will reset the staging area to match the specified `HEAD`, but leaves the working directory unchanged.

Running `git reset` will undo `git add -A`. That is, if you have added all the changes in your repository, running `git reset` will undo that.
