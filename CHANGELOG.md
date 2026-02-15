# Changelog

All notable changes to ClawCareer will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Changed
- Updated repository URLs from placeholder to `https://github.com/Aubrey-M-ops/ClawCareer.git`
- Improved job ID extraction logic to properly parse numeric IDs from LinkedIn URLs
- Enhanced HTTP headers for better LinkedIn compatibility and reduced blocking
- Increased request delays from 1s to 2s for more polite scraping

### Added
- Retry logic with exponential backoff for failed job description fetches
- Job ID validation before attempting to fetch descriptions
- More detailed debug output showing job IDs and description lengths
- Update documentation for users to pull latest changes

### Fixed
- LinkedIn 400 Bad Request errors when fetching job descriptions
- Job ID extraction now properly extracts only numeric IDs instead of full URL slugs
- Removed non-existent filter.py references from update documentation

## [1.0.0] - 2026-02-15

### Added
- Initial release
- LinkedIn job fetching with keyword-based search
- Country and location-based filtering
- Experience level filtering
- Province/state exclusion
- Location keyword exclusion
- Telegram notification support
- Daily scheduled runs via heartbeat
- Memory-based state tracking to avoid duplicate notifications
- Configuration via `config.json`
- Secure credential storage in `secrets.json`
- Manual run support with `--heartbeat` flag
- Dry-run mode for testing filters

### Security
- `secrets.json` automatically set to `chmod 600`
- Credentials gitignored by default

---

## Version History

- **v1.0.0** (2026-02-15): Initial release with LinkedIn → Telegram support
- **Unreleased**: Bug fixes and improvements for job scraping

---

## Upgrade Guide

When updating between versions, always:
1. Backup your `config.json` and `secrets.json`
2. Read the changelog for breaking changes
3. Test with `--dry-run` before running with `--send`

See [Update.md](docs/Update.md) for detailed update instructions.
