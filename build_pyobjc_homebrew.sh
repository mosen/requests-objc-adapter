#!/usr/bin/env bash
LIBFFI_ROOT=$(brew --prefix libffi)
pip install \
    --install-option="-I${LIBFFI_ROOT}/lib/libffi-3.0.13/include" \
    --install-option="-L${LIBFFI_ROOT}/lib" \
    pyobjc-core

#     --global-option=build_ext \