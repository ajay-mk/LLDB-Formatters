#!/bin/bash
set -e

cd "$(dirname "$0")"

# Build the test program
g++ -g -O0 test_boost_small_vector.cpp -o test_boost_small_vector -lboost_container

# Run LLDB with the command script and capture output
lldb -b -s test_boost_small_vector.lldb ./test_boost_small_vector > test_boost_small_vector.out 2>&1

# Extract only the relevant output for comparison
grep -A 5 "frame variable vec" test_boost_small_vector.out | head -6 > test_boost_small_vector.actual

# Compare output (fixed: compare actual vs expected, not actual vs out)
if diff -q test_boost_small_vector.actual test_boost_small_vector.expected; then
    echo "Boost small_vector test PASSED"
else
    echo "Boost small_vector test FAILED"
    echo "Expected:"
    cat test_boost_small_vector.expected
    echo "Actual:"
    cat test_boost_small_vector.actual
    exit 1
fi