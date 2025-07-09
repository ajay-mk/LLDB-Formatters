#!/bin/bash
set -e

cd "$(dirname "$0")"

# Build the test program
g++ -g -O0 test_boost_small_vector.cpp -o test_boost_small_vector -lboost_container

# Run LLDB with the command script and capture output
lldb -b -s test_boost_small_vector.lldb ./test_boost_small_vector > test_boost_small_vector.out 2>&1

# Extract only the relevant output for comparison
grep -A 5 "frame variable vec" test_boost_small_vector.out | head -6 > test_boost_small_vector.actual

# Compare output
if diff -q test_boost_small_vector.actual expected_boost_small_vector.out; then
    echo "Boost small_vector test PASSED"
else
    echo "Boost small_vector test FAILED"
    diff test_boost_small_vector.actual expected_boost_small_vector.out
    exit 1
fi