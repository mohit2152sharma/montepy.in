---
title: "Hotfix 1: Redirect or Rewrite"
date: 2026-09-27T12:26:23+05:30
draft: false
tags: ["hotfix", "networking", "devops"]
canonicalUrl: https://montepy.in/posts/hotfix-1
ShowBreadCrumbs: true
---
_This is the first edition of the [Hotfix](https://montepy.in/tags/hotfix/) series, in which I document an issue I encountered in production and how I fixed it._

We were in the midst of cleanup activities aimed at removing technical debt. Part of this effort focused on removing APIs that were no longer in use. It was silly of us not to properly define __"no longer in use."__ A proper definition should account for backward compatibility, especially when dealing with mobile apps rather than websites. Websites always fetch the latest version, so backward compatibility is not an issue, but there is no such guarantee with mobile apps because it depends on when users update the app.

As it happened, we removed an endpoint that we thought was no longer in use, only to discover after deployment that it was still being used and to receive complaints from customers. (Of course, we could have taken the Git revert route, but at the time, the following seemed like the fastest option.)

We needed a quick fix, so the first thing we tried was redirecting the old endpoint to the new one. Fortunately, this was possible because we hadn't changed the API contract for this particular endpoint, only its name. (Why, you may ask? It was part of standardizing our API endpoint naming scheme.) We were also using Istio's VirtualService to route external traffic to our internal services and pods. Below is an example of an Istio VirtualService.


```yaml
# public-api.yaml
apiVersion: networking.istio.io/v1
kind: Gateway
metadata:
  name: public-api
  namespace: default
spec:
  selector:
    istio: ingressgateway # match your ingress gateway pod label
  servers:
    - port:
        number: 80
        name: http
        protocol: HTTP
      hosts:
        - api.example.com

---
apiVersion: networking.istio.io/v1
kind: VirtualService
metadata:
  name: login-api
  namespace: default
spec:
  hosts:
    - api.example.com
  gateways:
    - public-api
  http:
    - match:
        - uri:
            prefix: /login
      route:
        - destination:
            host: login-service.default.svc.cluster.local
            port:
              number: 8080
```

Istio allows you to add a redirect clause.

```yaml
...
spec:
  http:
    - match:
        - uri:
            exact: /login
      redirect:
        uri: /new-login
        redirectCode: 308
    - match:
        - uri:
            prefix: /new-login
      route:
        - destination:
            host: login-service.default.svc.cluster.local
            port:
              number: 8080
```

A redirect occurs when a server tells the client, "Don't handle this request here; make another request at this location." The server does not internally forward the original request. Instead, it returns a `3xx` response with a `Location` header, and the client decides whether to follow it. `308` (or `307`) is better for APIs because both preserve the request body and method, while with `301` and `302`, the client may change the method of the follow-up request to `GET`.

Apart from adding a hop (another network round trip), we observed another drawback that seemed far more serious. Some clients may remove sensitive headers. As far as I knew, however, this happened only when the origin changed, which wasn't the case for us.

While testing on Android, it seemed to work, but on iOS, our service started returning `401` errors. As it turned out, iOS was stripping the `Authorization` header.

> The safer choice here was to use `rewrite` instead of `redirect`.

```yaml

spec:
  http:
    - match:
        - uri:
            exact: /login
      rewrite:
        uri: /new-login
      route:
        - destination:
            host: login-service.default.svc.cluster.local
            port:
              number: 8080
```

A redirect asks the client to send a new request. A rewrite changes the request inside Istio and forwards it immediately. The client still believes that it requested `/login`. The HTTP method, body, and headers all remain on the request.

> Changed the `redirect` to `rewrite` and both Android and iOS were happy.
