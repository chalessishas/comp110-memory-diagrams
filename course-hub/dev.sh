#!/bin/bash
export PATH="/usr/local/bin:$PATH"
cd "$(dirname "$0")"
exec npx next dev --port 3849
