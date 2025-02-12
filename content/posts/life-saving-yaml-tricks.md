---
title: "Time Saving Yaml Tricks"
date: 2025-02-12T17:35:54+05:30
draft: true
tags: ["yaml", "shell"]
ShowBreadCrumbs: true
categories: ["tools"]
---

# Time Saving Yaml Tricks

### DRY: Don't Repeat Yourself

If you have a section that's being repeated multiple times, you can create an anchor and then reference it. You use `&name` to create an anchor, and then `*name` to reference it. One example of it is defining environment variables for different services in `docker-compose.yaml`.

```yaml
env_vars: &env
  ENVIRONMENT: production
  LOGLEVEL: info
  AWS_REGION_NAME: us-east-1

services:
  api:
    environment: *env
    ...
    ...

  backend:
    ...
    ...
    environment: *env
```

### Reading environment variables

While yaml doesn't read environment variables, but if you pair it with parser, you can read the environment variables. The syntax depends on the parser you are using. The most common places, where I have a need for reading environment variables (or context variables) in yaml file is, cicd pipeline namely github action or circleci and docker-compose.

```yaml
# github action uses ${{ }}
run: echo running with secrets ${{ secrets.MY_SECRET }}

# circleci uses bash style syntax, you have to have these variables in circleci context
run: echo running with secrets $MY_SECRET

# docker-compose uses interpolation and will read MY_SECRET from your shell or .env file
environment:
  - MY_SECRET=${MY_SECRET}
```

### Multiline strings

- Use `>` to convert line breaks into spaces. This will fold new lines into a single line until the line ends with a new line

```yaml
description: >
  This is a long string
  that I want to break into multiple lines.

  But this will be second
  new line.

# the above will actually be parsed like this
description: |
  This is a long string that I want to break into multiple lines

  But this will be second new line.
```

- Use `|` if you want to preserve structure, like line breaks and indentation, useful for writing code blocks.

```yaml
run: |
  if [[ "$MY_ENV" == "test" ]]; then
    echo running in test environment
  fi
```
