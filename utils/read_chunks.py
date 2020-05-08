from XRootD import client

with client.File() as f:
  f.open('root://fermicloud157.fnal.gov:1094//100_values.bin')

  for chunk in f.readchunk(offset=0, chunksize=10):
    print(ord(chunk))
