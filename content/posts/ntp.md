---
title: "Synchronising Clocks"
date: 2025-05-06T14:57:08+05:30
draft: true
tags: [bash, shell]
---

Few days back, I encountered the following error on my website [saral.club](https://saral.club).

```
botocore.exceptions.ClientError: An error occurred (SignatureDoesNotMatch) when calling the SendEmail operation:
Signature not yet current: 20250505T152002Z is still later than 20250505T151830Z (20250505T151330Z + 5 min.)
```

By the looks of it, the error message is descriptive enough to guide you that there is some kind of time mismatch in the signature. Before sending a request to aws, the botocore library signs the request using your access keys. The signature also includes a timestamp. And the error message is saying that the request I am sending is probably 5 minutes later (in future) then the current time (time on aws servers). Of course, the two clocks (one on my server and the other on aws's server) cannot have the same exact time, so aws allows for some time skew (5 minutes).

It makes to sign the request with timestamp, to avoid the reuse of the signature. Imagine if a hacker gets hold of your signature then they can reuse it send the same signature again and again, if there is no timestamp. This is known as "replay attacks".

### How do we fix this?

First step is to check the status of your clocks. On your linux machine you can do the following:

```
> timedatectl status
               Local time: Mon 2025-05-05 17:11:21 UTC
           Universal time: Mon 2025-05-05 17:11:21 UTC
                 RTC time: Mon 2025-05-05 17:04:51
                Time zone: Etc/UTC (UTC, +0000)
System clock synchronized: no
              NTP service: active
          RTC in local TZ: no
```

The command's output shows that the local time is out of sync with RTC time. RTC time refers to the Real Time Clock and it is maintained by the hardware clock. So basically the hardware clock is out of sync with the system clock. The system clock is a software clock maintained by the operating system. It starts when the system boots up and then it is independently maintained by CPU ticks. Overtime the two clocks drift apart. To fix the issue, you can run the following command. This will synchronize the two clocks.

```
hwclock --systohc
```

There is one more issue. If you look at the output of `timedatectl status`, it shows that though `NTP service` is active, the `System clock synchronized` is set to `no`. Meaning the system clock is not synchronized to the npt service. This is required, otherwise you will run into the issue of unsynchronized clocks again after some time. `NTP service` allows the system clock to synchronize its clocks using a centralized server. The synchronization happens over network and the full form of `NTP` is `Network time protocol`. To ensure, your server is communicating with the NTP service, keep the port `123` open in the firewall and allow outbound and inbound traffic through it (this would depend on your firewall configuration).

To check the logs of the ntp service, you can run the following command:

```
journalctl -u systemd-timesyncd --since "10 minutes ago"
```
