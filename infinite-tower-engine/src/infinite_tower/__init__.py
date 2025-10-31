"""
Infinite Tower Engine package init.

Exposes package version for use in UI and logs.
"""

from __future__ import annotations

__all__ = ["__version__"]

# Attempt to read the installed package version; fall back to source version.
try:
	try:
		from importlib.metadata import version, PackageNotFoundError  # Python 3.8+
	except ImportError:  # pragma: no cover
		from importlib_metadata import version, PackageNotFoundError  # type: ignore

	__version__ = version("infinite-tower-engine")
except Exception:
	# Fallback when running from source without install
	__version__ = "0.1.0"
