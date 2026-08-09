---
title: "Websocket"
date: 2026-06-27T19:00:29+05:30
draft: false
---

If you go through [weboscket.org](https://websocket.org), you will see the essential events are `onopen`, `onmessage`, `onerror`, `onclose`. Naively I assumed that authentication should happen in `onopen` event. But this resulted in an unanticipated security breach. 

But first the normal web requests. In a normal requests, I can send custom headers like `Authorization: Bearer token`. This works, because the browser makes the preflight request, asking the server `"I am about to make this request with this header and this method, do you allow it?"`. At this stage the server can reject this request, if either the method or the header doesn't exist. 

But for websockets, the handshake request is like a preflight request. The handshake request consists of `GET` request with headers `Upgrade: websocket` and `Connection: upgrade`. No custom headers. Since I can't send the `Authorization` header with the request. I added the access token as a query parameter i.e. my url looked like `wss://app.com?access_token=sdgbscsf`. This all is fine. The issue came on what event I was doing the authentication. 

> NOTE:
There is a difference between Authentication and Authorization. Authentication is "Who are you?" and authorization is "What you are allowed to do?". 

I used the `onopen` event of websocket to parse the query parameters and run the authentication check. If the user is authenticated, proceed otherwise close the connection. 

```typescript

ws.on('connection', async (ws, req) => {
  const params = new URL(req.url, `http://${req.headers.host}`).searchParams 
  const token = params.get('access_token')
  const authorized = checkAuthentication(token)
})

```

I assumed as the `connection` function block is executing the websocket is in `connecting` state. It's only after it has finished executing that the connection is established between server and client and both are free to send messages. But since I am using `async`, even while the `connection` block hasn't finished, the client is allowed to send messages to server. 
So essentially, before I could authenticate the client, the client can send payload and this payload could be any malformed payload.

As a remedy of the above, either I make this function `synchronous` or move the authentication from `connection` to `upgrade` event. 

```typescript

ws.on('upgrade', async (ws, req) => {
  const params = new URL(req.url, `http://${req.headers.host}`).searchParams 
  const token = params.get('access_token')
  const authorized = checkAuthentication(token)
})

```

This is much secure, as I am rejecting the request before the connection is even open. The earlier style was following the `open-then-close` approach. But with this, I don't open the connection unless the user is authenticated completely.
