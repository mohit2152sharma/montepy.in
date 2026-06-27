---
title: "Cognitive Load"
date: 2026-02-22T21:24:25+05:30
draft: false
tags: ["ai", "llm"]
ShowBreadCrumbs: true
canonicalUrl: https://montepy.in/posts/cognitive-load
categories: ["ai", "engineering"]
---

With the recent update of `claude` (which is a significant improvement), like many, my programming style has also changed. Unlike the old days (it's just been a few weeks, and it's already old), I don't write code **"manually"**, like laboriously typing `def` before every function — I simply ask `claude` to do it. Even for the smallest of tasks, I would much rather type `"please commit the recent changes and push to remote"` instead of `git add . && git commit -m "(wip)" && git push`. In other words, I have completely shifted to **"Agentic Coding"**. The advantages are clear: I am certainly writing more code and shipping faster, plus while `claude` is thinking and writing the code, I get mini breaks to scroll through Instagram slop.

The disadvantages? More and more, I feel I am offloading my thinking to `claude`. There is a certain joy associated with programming — the joy of solving problems and figuring things out — which seems to fade away as I adopt `claude` more and more. For example, when I was new to `python` and was asked to log how much time each function was taking, the very first approach someone new to Python would come up with is the following:

```python
def some_complicated_function():
  print(f"starting function: some_complicated_function")
  t0 = time.time()
  ...
  ...
  ...
  print(f"Time taken by function: some_complicated_function, {time.time() - t0}")
```

There is nothing wrong with it, but soon you will realise that this is cumbersome when you have to make these changes to 20+ functions. This cumbersomeness led me to discover the concept of `decorators` in Python, and like it, many other concepts. But with `claude`, it's not cumbersome at all — I can just ask `claude` to do it, and it is more than happy to implement this across all the functions. Of course, it can implement decorators as well, but only when I ask it to (for anything advanced, I have to nudge it, and I can only nudge about things I am already aware of).

Up until now, people used to write code with foresight: I am the one who has to type it and I am the one who has to maintain it, so what's the best way? Which approach lets me type less and which makes it more maintainable? This has led to many design patterns we see today, but with `claude` I feel this will become an afterthought, only to come back and bite us later. If `claude` is writing most of the code, will it be able to maintain it as well? I certainly cannot — it can generate so much code in one shot, which is very difficult to understand, at least when an issue comes up in production. And oh boy, it certainly does. At that point, either I can sit through and read what `claude` has done, or just dump the error and let it figure it out. I almost always choose the latter, but I have had instances where it reached its context limit and went in the wrong direction. Things have certainly improved with the latest `claude`, and that is the only hope — as the codebase keeps getting bigger and bigger, `claude` should also get better, because I am dreading the day when I have to sit through the entire mess to debug a production issue in an hour or so.
