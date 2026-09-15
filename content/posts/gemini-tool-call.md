---
title: "Gemini Tool Call"
date: 2026-09-15T21:09:49+05:30
draft: false
---

Working with `gemini-live-2.5-flash-native-audio` (of course, naming things is not Google's strongest suit—remember Bard?) has its own ups and downs. No doubt, the liveliness, expressiveness, and language capabilities are really good, but tool (function) calling had me thinking otherwise.

> Reducing unintentional tool calls is especially important for our use case, as it involves taking images via voice commands. A photo taken unintentionally makes it look like the device is taking photos by itself.

My first iteration was heavily influenced by how other LLMs behave, but the Gemini Live model is different. It is a full-duplex model, i.e., a voice-to-voice model, unlike previous versions, which were cascading models (speech to text -> text to speech). The previous models behaved well and in a controlled way because noise (or gibberish), when transcribed, produces a gibberish transcript that can be ignored before making tool calls. Voice models are different: noise may also trigger a tool call.  
The only way to control voice models is through system instructions, and that was our first solution. We put all the rules regarding noise, gibberish, or the user not speaking clearly into the system instruction. It looked like this:

```
You are acting in a noisy environment. Do not invoke a tool call until the user has explicitly asked you to do so. The user may sound like gibberish in a noisy environment. If the user's request is unclear, ask for clarification.
```

Additionally, we introduced a confirm-then-act protocol. It looks fancy in writing, but it simply means asking the user for confirmation before invoking the tool call. This made sense because, even if the tool call was unintentional, the user could stop it from executing by denying the request. Of course, the complete system instruction was much bigger than this (roughly 6,000 tokens, which was another issue to tackle), with similar lines written for each tool. We realised pretty soon that this was not going to scale as we added more tool calls. Tool-call adherence is inversely proportional to the number of tokens in the system instruction. Beyond 8,000 tokens, adherence drops rapidly, even though the model's context length is quite large.

Our next solution was to offload some of the system instruction and its logic to the tool definitions. The confirm-then-act protocol was shifted to the tool definition: `If the user confirms, invoke this tool again with confirmed=true`. This improved tool-call adherence, but it gave rise to another issue. Since the tool call was invoking itself, it often entered a loop or invoked the same tool multiple times. Overall tool-call adherence was good, but there were instances in which users experienced the same tool call more than five times after requesting it only once. While the numbers looked good overall, the experience was so bad for some users that we had to try something else. The issue with this solution was that it tried to manage tool-call execution state with a probabilistic model. Of course, there is a chance that the model will invoke the tool again if the tool response is not supplied within a given time frame. This became apparent when we realised that the model often makes the same tool call again if its loop is not closed. When the model sends a tool call, it expects us to send back a tool response. If the response to that tool call (tracked via `call_id`) is not sent back, the model may invoke the tool again, thinking that the user has not provided the result yet and that it should ask again. This is amplified if the system instruction includes phrases such as `Ask the user for confirmation`.

The final solution we settled on was moving the tool-call execution state out of the model and periodically nudging it toward the next step. This also helped us reduce the number of tokens in the system instruction. In other LLM parlance, this may be known as prompt chaining.

The idea was essentially to introduce a new primitive called `ToolRun` and use it to chain together multiple tool calls. The SI dictates which tool should be called first, and that tool's response guides the model on what to do next. For example, we can include `"Invoke take_photo when the user asks to take a photo"` in the SI. When `take_photo` is invoked, we perform some prewarming activities and send back this tool response: `"Now ask for confirmation and invoke is_confirmed(confirmed=true) if the user said yes; otherwise, invoke is_confirmed(confirmed=false)"`. If the user says yes, we continue the tool execution and take the photo. The intermediate tool, `is_confirmed`, can be made even more generic to handle multi-step tool calls: first ask this, then that, and then another thing; ask all three at once; or ask two at a time and the other at a different time.

This last method really improved our tool-call adherence: it went from 52% to 84%, all because the state was no longer part of the system instruction or tool-call definition.

