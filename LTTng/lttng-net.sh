#!/bin/sh


lttng create $1
lttng enable-event -k --syscall --all
lttng enable-event -k sched_switch,sched_wak'*',irq_'*',net_'*',sock_'*',napi_poll,skb_'*',lttng_statedump_'*'
lttng add-context -k -t vtid -t vpid -t procname
lttng start
sleep 15
lttng stop
lttng destroy
