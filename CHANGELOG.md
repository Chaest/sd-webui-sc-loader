# Changelog

## [5.3.1] - 2023/09/26
### Fixed
 - Fixed page example

## [5.3.0] - 2023/09/26
### Added
 - Added presets to save and load configurations
 - Added a page example

### Fixed
 - Fixed page not working with styles

## [5.2.0] - 2023/09/20
### Added
 - Can now now more than one style

### Fixed
 - Fixed next together example scenario

## [5.1.1] - 2023/09/14
### Added
 - An empty style field

### Fixed
 - Fixed page not working anymore
 - Fixed no style error

## [5.1.0] - 2023/09/11
### Added
 - Handle faces and hands in both JSON and SC poses
 - Handle packages

### Fixed
 - Fixed expanders not working with batches on txt2img/img2img
 - Should remove the error "negative.yaml invalid" error message
 - Fixed some db problems (please please do tell me if you have errors with the installation)

## [5.0.2] - 2023/09/08
### Added
 - Handle user defined path to models

## [5.0.1] - 2023/09/08
### Fixed
 - Fix db loading error on first installation

## [5.0.0] - 2023/09/08
### Added
 - A prompt blacklist
 - A DB file edit tab
 - Sc Loader can now create pages
 - Better handling of the expander dicts
 - Batch system
 - Character prompts added in sc loader tab
 - Expander download URL added in DB
 - SC Tool tab added
 - Download base model added
 - Download wildcards added
 - Download openposes added
 - Create db file added
 - Create db added
 - Download batch added
 - JSON poses handled
 - SC Poses
 - JSON pose to SC Pose added
 - Sc Latent Couple merged in Sc Loader
 - Json/Sc pose to mask
 - Negative prompt in expander creation

### Changed
 - Expander can now be used in txt2img/img2img
 - Prefixes: world_morph: wm_ -> worlmorp_
 - Weight slider in expander creation: now -7 to 7
 - Prompt creation tab renamed Expander creation
 - Embedding weight prettier
