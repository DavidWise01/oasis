# KET observation: the 03:00 "blink" (Dark City analogy)

Date: 2026-10-18.
Classification: **hypothesis / observation protocol**, not a verified global Internet event or a KET law.
Location in stack: separate observations, **outside** the accepted Z328–Z333 recovery baseline and frozen KET.

## Hypotheses
H1. Windows scheduled maintenance/wake at around 03:00 local. Historically Windows automatic maintenance had a 3 AM default in documented Microsoft configurations; modern laptops vary by sleep model, power and policy.
H2. Modern Standby intermittent software wake, network notifications or synchronization.
H3. Router/ISP lease, reconnect, outage, maintenance, or time-service event.
H4. Deferred app sync only after manually reopening the lid.

These are distinguishable, not interchangeable. No evidence of a synchronized worldwide Internet-wide 3 AM event; do not assert one.

## Inspect without modifying the system (Windows PowerShell)
```powershell
powercfg /a
powercfg /lastwake
powercfg /waketimers
powercfg /sleepstudy
Get-WinEvent -FilterHashtable @{LogName='System'; StartTime=(Get-Date).Date.AddDays(-2)} |
  Where-Object { $_.ProviderName -match 'Power-Troubleshooter|Kernel-Power|Kernel-General|Time-Service|Tcpip|Dhcp|WLAN' } |
  Select-Object TimeCreated, ProviderName, Id, Message |
  Sort-Object TimeCreated
```
Use only read-only commands; `powercfg /sleepstudy` may create a local report file. Narrow logs to 02:30–03:30 if examining the 3 AM hypothesis, but also compare the exact closed-lid and reopened timestamps. Correlate with router logs and network reconnection times. Record clock timezone, event timestamp, source and whether it is a wake, network down/up, or later catch-up.

## Evidence levels
Observed user report: laptop lid closed the prior night. Hypothesis: Internet "blink" at 03:00. Unverified until power and connectivity logs supplied.
External background: Microsoft's Modern Standby Wake Sources, System Power States, and Task Scheduler Automatic Maintenance documentation.

## Interpretation
The *Dark City* imagery is a narrative analogy for a hidden maintenance interval, not an evidentiary claim about worldwide synchronization.

No code, tests, or freeze flags in the accepted research baseline are changed.
