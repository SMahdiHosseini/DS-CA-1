graph [
  node [
    id 0
    label "1"
    host_bandwidth_up "10 Mbit"
    host_bandwidth_down "10 Mbit"
  ]
  node [
    id 1
    label "2"
    host_bandwidth_up "10 Mbit"
    host_bandwidth_down "10 Mbit"
  ]
  node [
    id 2
    label "3"
    host_bandwidth_up "10 Mbit"
    host_bandwidth_down "10 Mbit"
  ]
  node [
    id 3
    label "4"
    host_bandwidth_up "10 Mbit"
    host_bandwidth_down "10 Mbit"
  ]
  node [
    id 4
    label "5"
    host_bandwidth_up "10 Mbit"
    host_bandwidth_down "10 Mbit"
  ]
  edge [
    source 0
    target 0
    weight 0
    latency "10 ms"
    packet_loss 0.0
  ]
  edge [
    source 0
    target 1
    weight 1
    latency "10 ms"
    packet_loss 0.0
  ]
  edge [
    source 0
    target 4
    weight 1
    latency "10 ms"
    packet_loss 0.0
  ]
  edge [
    source 1
    target 1
    weight 0
    latency "10 ms"
    packet_loss 0.0
  ]
  edge [
    source 1
    target 2
    weight 1
    latency "10 ms"
    packet_loss 0.0
  ]
  edge [
    source 2
    target 2
    weight 0
    latency "10 ms"
    packet_loss 0.0
  ]
  edge [
    source 2
    target 3
    weight 1
    latency "10 ms"
    packet_loss 0.0
  ]
  edge [
    source 3
    target 3
    weight 0
    latency "10 ms"
    packet_loss 0.0
  ]
  edge [
    source 3
    target 4
    weight 1
    latency "10 ms"
    packet_loss 0.0
  ]
  edge [
    source 4
    target 4
    weight 0
    latency "10 ms"
    packet_loss 0.0
  ]
]
