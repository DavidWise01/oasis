#!/usr/bin/env python3
def step(s):
  if s=='|||': return '||||'
  if s=='||||': return 'DECOHERENCE_OUTSIDE_KERNEL'
  return None
assert step('|||')=='||||'
assert step('||||')=='DECOHERENCE_OUTSIDE_KERNEL'
assert step('DECOHERENCE_OUTSIDE_KERNEL') is None
print('0e / KERNEL TERMINAL BOUNDARY CLOSED')
print('next scope: DECOHERENCE_OUTSIDE_KERNEL')
