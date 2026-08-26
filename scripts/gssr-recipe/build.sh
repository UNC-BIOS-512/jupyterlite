#!/bin/bash
set -euo pipefail

export DISABLE_AUTOBREW=1

# Strip the curl-dependent live-download functions (gss_get_yr/gss_get_years'
# internals use curl::curl_download, and r-curl isn't available for the
# emscripten-wasm32 target). All bundled datasets and gss_which_years() are
# unaffected. See README.md for details.
sed -i.bak '/^    curl,$/d' DESCRIPTION
sed -i.bak '/^importFrom(curl,curl_download)$/d;/^export(gss_get_yr)$/d' NAMESPACE
sed -i.bak '/@importFrom curl curl_download/,+2d' R/gssr-package.R
sed -i.bak '/^gss_get_yr <- function/,/^}/d' R/gssr-package.R
rm -f DESCRIPTION.bak NAMESPACE.bak R/gssr-package.R.bak

R CMD INSTALL --build .
