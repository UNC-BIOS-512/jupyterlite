#!/bin/bash
set -euo pipefail

export DISABLE_AUTOBREW=1
R CMD INSTALL --build .
