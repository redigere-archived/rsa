#!/bin/bash
FAILED=0
for SHA in $(git log --pretty=format:"%H" origin/main..HEAD); do
  MSG=$(git log -1 --pretty=format:"%B" "$SHA")
  if ! echo "$MSG" | grep -q "Signed-off-by:"; then
    echo "MISSING signoff: $SHA $(git log -1 --pretty=format:'%s' "$SHA")"
    FAILED=1
  fi
done
if [ "$FAILED" -eq 1 ]; then
  echo "All commits must include Signed-off-by"
  exit 1
fi
echo "All commits have Signed-off-by."
