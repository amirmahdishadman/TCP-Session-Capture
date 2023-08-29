#!/bin/bash
#./code savename prob_func_name

lttng create $1
lttng enable-event -k 
lttng enable-event -k sched_switch,sched_wak'*',irq_'*',net_'*',sock_'*',napi_poll,skb_'*'
#lttng enable-event -k --function=net_rx_action net_rx_action
lttng enable-event -k --probe=$2 $2
lttng add_context -k -t vtid -t vpid -t procname 
lttng start
sleep 10
lttng stop
lttng destroy
