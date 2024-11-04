---
title: "How to parse json in terminal using jq"
date: 2024-04-01T22:43:39+05:30
draft: false
canonicalUrl: https://montepy.in/posts/jq
tags: ["bash", "shell"]
ShowBreadCrumbs: true
categories: ["tools"]
---

## A practical tutorial on `jq`

So here's the problem statement: _**Find the repository on github in which you have made most number of commits? And you need to do this on terminal (no python)**_

Ofcourse, one can use python to find the answer, and it might be probably easy for you, if you have been using python for last many years. But let's see if I can do this in terminal with `jq` and while doing so, let's learn about it.

For installation steps, refer this [link](https://jqlang.github.io/jq/download/)

- The endpoint to get all the repos is: [`https://api.github.com/users/{username}/repos`](https://api.github.com/users/{username}/repos). Let's try that:

```bash
curl 'https://api.github.com/users/mohit2152sharma/repos'
# [{"id":347381136,"node_id":"MDEwOlJlcG9zaXRvcnkzNDczODExMzY=","name":"aqad-utilities","full_name":"mohit2152sharma/aqad-utilities","private":false,"owner":{"login":"mohit2152sharma","id":26904579,"node_id":"MDQ6VXNlcjI2OTA0NTc5","avatar_url":"https://avatars.githubusercontent.com/u/26904579?v=4","gravatar_id":"","url":"https://api.github.com/users/mohit2152sharma","html_url":"https://github.com/mohit2152sharma","followers_url":"https://api.github.com/users/mohit2152sharma/followers","following_url":"https://api.github.com/users/mohit2152sharma/following{/other_user}","gists_url":"https://api.github.com/users/mohit2152sharma/gists{/gist_id}","starred_url":"https://api.github.com/users/mohit2152sharma/starred{/owner}{/repo}",
# ...
...
```

- If you happen to get an output like above (not pretty), you can easily make it pretty with `jq .`. The `.` is also called the _**identity filter**_. It takes the input and produces the same value as output. By default it `jq` pretty prints, so identity filter can be used to pretty print a json output from a command like curl or from a json file (e.g. `cat file.json | jq .`)

```bash
curl 'https://api.github.com/users/mohit2152sharma/repos' | jq .
# [
#   {
#     "id": 347381136,
#     "node_id": "MDEwOlJlcG9zaXRvcnkzNDczODExMzY=",
#     "name": "aqad-utilities",
# ...
# ...
# ]
```

- Let me quickly check what all repositories I have by printing just their name. But let me first check, what all keys are available in the output dictionary. For that, I will use the command `jq '.[1] | keys'`
  - `.[]` is the array value iterator, it returns all the values in the array. If you use an integer like `.[1]` it return the value at index 1.
  - `|` is a pipe operator. It compbines two filters by taking the output from the filter on left and passing it to the filter on right.
  - `keys` is a function which returns all the keys of an object (aka dictionary) in an array. There are more builtin functions in [jq](https://jqlang.github.io/jq/manual/#builtin-operators-and-functions)

```bash
# output truncated because there are too many keys
curl 'https://api.github.com/users/mohit2152sharma/repos' | jq '.[1] | keys'
# [
#   ...
#   ...
#   "name",
#   "node_id",
#   ...
#   ...
# ]
```

- The following command `.... | jq '.[].name'` will return all the names of the repositories.
  - As highlighted above `.[]` is an array iterator. It iterates over all the values in the array, since each element is an object, I use `.name` to get the value of key named `name`.
  - `.key_name` is an object identifier. When a json object is passed `.key_name` returns the value at the key `"key_name"`. You can also do `.["key_name"]`.
  - You can also chain the filters `.key_name1.key_name2`, this is equivalent to `.key_name1 | .key_name2`.

```bash

curl 'https://api.github.com/users/mohit2152sharma/repos' | jq '.[].name'
# "bash-exmpls"
# "codesnipper"
# "cookiecutter-ml"
# "emwv"
# ...
# ...
```

- Let me quickly check, how many public and privte repositories I have.
  - `map(f)` is a builtin function in `jq`. It applies the filter `f` to each element in the array and returns an array.
  - `length` is also a builtin function, it returns the length (or number of elements) in the array. One can also use it with json objects or string, in those cases, it returns total number of keys and length of string respectively.

```bash
curl 'https://api.github.com/users/mohit2152sharma/repos' | jq 'map(select(.visibility=="public")) | length'
# 30

curl 'https://api.github.com/users/mohit2152sharma/repos' | jq 'map(select(.visibility=="private")) | length'
# 0
# it looks like the response doesn't include private repos
```

- Now let's get back to original question, the repository, in which I have made most number of commits. This more tricky than I expected, because, the url to get the number of commits is different. It is of the form `https://api.github.com/users/{user_name}/{repo_name}/commits`. So basically, I need to loop through each repo, hit this url, count the number of commits. _This became more of bash programming task than that of `jq` programming task._

```bash
USER_NAME=mohit2152sharma

# get all the repositories
getRepoUrl=https://api.github.com/users/${USER_NAME}/repos
allRepoNames=""
j=1
while true; do
    repoInfo=$(curl --url "$getRepoUrl"?page="$j" --header "Authorization: Bearer $GITHUB_TOKEN")
    repoInfoLength=$(echo "$repoInfo" | jq '. | length')
    if [ "$repoInfoLength" -eq 0 ]; then # the length of the empty array will be zero
        break
    else
        names=$(echo "$repoInfo" | jq '.[].name')
        allRepoNames="$allRepoNames $names"
        j=$(( j + 1 ))
    fi
done;

# now loop through all repo names and find the commit counts
maxCommits=0
repoNameWithMaxCommits=""
for repoName in "$allRepoNames"; do
    i=1
    totalCommits=0
    getCommitUrl=https://api.github.com/repos/${USER_NAME}/${repoName}/commits
    while true; do
        ncommits=$(curl --url "$getCommitUrl"?page="$i" --header "Authorization: Bearer $GITHUB_TOKEN" | jq 'map(select(.author.login=="mohit2152sharma")) | length')
        if [ "$ncommits" -eq 0 ]; then
            break
        else
            totalCommits=$(( totalCommits + ncommits ))
            i=$(( i + 1 ))
        fi
    done

    if [ "$totalCommits" -gt "$maxCommits" ]; then
        maxCommits=$totalCommits
        repoNameWithMaxCommits=$repoName
    fi
done

echo "Repository with most number of commits: ${repoNameWithMaxCommits} with ${maxCommits} commits"
```

- The above script prints the following output:

```
# Repository with most number of commits: rcoronavirus with 192 commits
```
