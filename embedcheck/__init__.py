"""embedcheck: catch embedding regressions before you re-index.

Take a *snapshot* of a model in one environment, another snapshot after upgrading
libraries (or hardware, or dtype), then *compare* them. Exit code is non-zero on
regression, so it drops into CI.
"""
__version__ = "0.1.0"
