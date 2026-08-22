---
title: "Debugging audio issues with RNNoise"
date: 2026-08-09T11:54:55+05:30
draft: true
---

I am working on a voice agent for smart glasses of major Indian eyewear retailer. This is a new form factor with it's own challenges but one of the challenge I encountered was around managing the noise and it's behaviour with Gemini live. 

The audio pipeline was very simple, glasses capture the audio, and send it to backend, the backend sends it to Gemini live which in turn returns tool call and audio, which is then forwarded back to the glasses for playback. Now ofcourse when we are capturing the audio on glasses, we capture the noise as well, the on device DSP lacks the capability to clean out or do noise suppresion and the Gemini behaves very weird with audio noise. Not weird to be precise but to an end user it looks weird, for example AI answering about things which user didn't ask or randomly invoking any tool call. 

To overcome this, we needed a noise suppresion which cleans the noise without adding any latency overhead. [RNNoise](https://jmvalin.ca/demo/rnnoise/) fits the bill. It is extremely fast and does the job ~90% of the time. But there were instances where it didn't and in this blog, I will go into details of those: 

# How does RNNoise work? 

> Noise suppression is pretty old topic, the idea is to take a noisy signal and remove as much noise as possible while causing minimum distortion to the speech of interest.<sup>1</sup>

RNNoise combines the idea of traditional signal processing with the ideas of deep learning. It is recurrent neural network. 

# TODO: 
1. Describe RNN briefly
  - how is it trained
  - what it predicts
  - what's its data
2. Issues encountered while working with it: 
  - Audio getting cleaned completely
  - Words getting stripped away
  - User plus by standers voice coming in (or not getting cleaned properly)
3. How did we overcome those challenges? 


1. https://jmvalin.ca/demo/rnnoise/
2. 
