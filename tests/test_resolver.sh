#!/usr/bin/env bash
# Tiny test for the script-path resolver used in skills/junior-dev/SKILL.md.
#
# The skill invokes helper scripts with:
#   command -v <name> 2>/dev/null || find ~/.claude/plugins/cache -name <name> 2>/dev/null | head -1
# This test checks that expression is (1) valid shell, (2) resolves a script that
# is on PATH, and (3) still matches what SKILL.md actually ships.
#
# Run:  bash tests/test_resolver.sh
set -u

HERE="$(cd "$(dirname "$0")" && pwd)"
ROOT="$(cd "$HERE/.." && pwd)"
SKILL="$ROOT/skills/junior-dev/SKILL.md"
RESOLVER='command -v junior-delegate.py 2>/dev/null || find ~/.claude/plugins/cache -name junior-delegate.py 2>/dev/null | head -1'

fail=0
check() { # <description> <test-exit-status>
  if [ "$2" -eq 0 ]; then echo "  ok   $1"; else echo "  FAIL $1"; fail=1; fi
}

# 1. The resolver expression is syntactically valid shell.
printf '%s\n' "$RESOLVER" | bash -n 2>/dev/null
check "resolver is valid shell syntax" $?

# 2. With bin/ on PATH, the resolver finds the real script (command -v branch).
resolved="$(PATH="$ROOT/bin:$PATH" bash -c "$RESOLVER")"
[ "$resolved" = "$ROOT/bin/junior-delegate.py" ]
check "resolves junior-delegate.py via PATH" $?

# 3. The resolved file is the real delegate script: empty stdin hits its
#    empty-spec guard (exit 2) BEFORE any network call — no Ollama needed.
python3 "$resolved" </dev/null >/dev/null 2>&1
[ "$?" -eq 2 ]
check "resolved script runs to its empty-spec guard (exit 2)" $?

# 4. SKILL.md still ships the resolver pattern (doc <-> test drift guard).
grep -q 'command -v junior-delegate.py' "$SKILL"
check "SKILL.md references command -v resolver" $?
grep -q 'command -v junior-preflight.py' "$SKILL"
check "SKILL.md references preflight resolver" $?
grep -q 'find ~/.claude/plugins/cache' "$SKILL"
check "SKILL.md references cache fallback" $?

echo
if [ "$fail" -eq 0 ]; then echo "RESULT: PASS"; else echo "RESULT: FAIL"; fi
exit "$fail"
