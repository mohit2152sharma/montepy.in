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

While solving this bug was important, but what seemed more interesting to me was, how do the labs even measure pronunciation? And not just pronunciation, all the other subjective features of voice like expressiveness, tone, likability etc. To explain it concretely, imagine saying a single word "What?". It can be a normal question or an expression of excitement or an expression of anger depending on the intensity of how you pronounce it.

In this blog, I wanted to share some of my findings around this topic:

# Terminologies:

Prosody: 

Is a measure of intonation, rhythm, stress and phrasing. These are the patterns which give meaning to our words beyond their literal meaning.



References: 
1. https://elevenlabs.io/blog/what-is-prosody

