#! /bin/bash

for i in `seq $2 $3`; do
  echo "solving $i..."
  time python sokosolver.py $1 $i > ,solution-$i
done 
