---
title: "Pronounciation"
date: 2026-09-19T17:35:01+05:30
draft: true
tags: ["ai", "gemini", "llm", "voice"]
canonicalUrl: https://montepy.in/posts/pronounciation
ShowBreadCrumbs: true
categories: ["engineering", "voice"]
---


Recently we encountered a nasty bug with our voice agent. To be precise it wasn't a bug as much as it was a finding of how the model behaves. With our latest release of voice agent, we started hearing users complain that the agent is mispronouncing certain words. And sometimes while speaking a sentence it completely derails (I am using the word derail loosely here, imagine having too many slip of tongue in a sentence). One concrete example of it was, instead of saying "photo", the model was saying "phono".

While solving this bug was important, but what seemed more interesting to me was, how do the labs even measure pronunciation? And not just pronunciation, all the other subjective features of voice like expressiveness, tone of the model, the loudness, the whispering etc. etc.

In this blog, I wanted to share some of my findings around this topic: 




References: 
1. https://elevenlabs.io/blog/what-is-prosody

