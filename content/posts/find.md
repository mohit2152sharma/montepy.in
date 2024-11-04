---
title: "How to `find` files in terminal?"
date: 2024-02-21T20:26:20+05:30
draft: false
tags: ["bash", "shell"]
ShowBreadCrumbs: true
canonicalUrl: https://montepy.in/posts/find
categories: ["tools"]
---

_**Manager**_: Hey, I need your help, I have couple of images that are taking a lot of space on my PC, I want to delete them. How can I do that?

_**Developer**_: Well that should be simple. Here, you go. This looks for all files with `.png` extension in the current directory and its subdirectories (using `-R` flag), then pipes those file names to `rm` command to delete them.

```bash
ls -R | grep ".png$" | xargs rm
```

_**Manager**_: Nice, but wait. This will delete all the `png` files in the current directory and its subdirectories. I only want to delete in specific directories.

_**Developer**_: Okay, that should be easy as well.

```bash
ls -R dir1 dir2 | grep ".png$" | xargs rm
```

_**Manager**_: This only selects `.png` but I also have image of `.jpg` and `.jpeg` files. I want to delete them too.

_**Developer**_: Okaay, this getting complicated a little bit. I think I can do that with `find` command, think that is much safer.

```bash
# command 1
# {} is a placeholder for matched file
# {} \; means execute rm command for each matched file
# the -o flag means OR operator and \( means brackets are escaped
# and used to club together the expression using or operator
find dir1 dir2 -type f \( -name "*.png" -o -name "*.jpg" -o -name "*.jpeg" \) -exec rm {} \;

# command 2
# -E enables extended regex
# rm {} + means rm file1 file2 file3 ....
find -E dir1 dir2 -type f -regex ".*/.*(png|jpg|jpeg)" -exec rm {} +
```

_**Manager**_: Much better, now narrow down the files to only those files which were created in last 7 days.

_**Developer**_: Okay, is that it? Or are there any more conditions?

_**Manager**_: Yeah, and one more condition, files should be at least 5 MB in size.

_**Developer**_: I see, is that it?

_**Manager**_: Yeah, think so. Can you do that?

_**Developer**_: Sure. This should do the trick.

```bash
find -E dir1 dir2 -type f -regex ".*/.*(png|jpg|jpeg)" -ctime -7 -size +5M -exec rm {} +
```

_**Developer**_: To explain in more detail, `find` command is of the form: `find [flags] [path(s) to search in] [expression(s) or filter(s)] [actions]`.
