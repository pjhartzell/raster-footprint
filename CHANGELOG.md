# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/). This
project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- Added a CLI ([#27](https://github.com/pjhartzell/raster-footprint/issues/27))
- Added a `precision` option to the densify functions
  ([#25](https://github.com/pjhartzell/raster-footprint/issues/25))

### Changed

- Changed default behavior in mask and footprint creation to not include holes
  ([#26](https://github.com/pjhartzell/raster-footprint/pull/26))
- Moved `geometry` argument to first position in `reproject_geometry`
  ([#24](https://github.com/pjhartzell/raster-footprint/pull/24))

## [0.1.0] - 2023-08-13

Initial release.

[unreleased]: https://github.com/pjhartzell/raster-footprint/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/pjhartzell/raster-footprint/releases/tag/v0.1.0
