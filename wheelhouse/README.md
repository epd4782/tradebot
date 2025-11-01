
Wheelhouse
Place pre-built Python wheel files for all production dependencies in this directory to enable fully offline installations. The
CI workflow and Docker builds will rely exclusively on the artifacts stored here when USE_OFFLINE_WHEELS is enabled.