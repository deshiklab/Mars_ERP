# mars_constech package init.
# NOTE: `api` is intentionally shadowed with the callable `index` endpoint.
# Frappe resolves /api/method/mars_constech.mars_constech.api by doing
# getattr(module, "api") — which would return this submodule and 500
# ("module has no attribute __module__"). Shadowing makes the bare base URL
# resolve to the whitelisted index() function (endpoint map + health).
# All real endpoints (mars_constech.mars_constech.api.<fn>) still resolve via
# importlib on the submodule and are unaffected.
from mars_constech.mars_constech.api import index as api  # noqa: F401
