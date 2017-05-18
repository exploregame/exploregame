# Changelog
## 0.0.1.alpha-1.rc1
* Initial release
## 0.0.1.alpha-1.1
* Added pigs
* Added Basic AI
* Bug fixes
## 0.0.2.rc2
* Menus
* Game menu
* Inventory
* Changing things into classes
* Better pigs
* Bug fixes
## 0.0.2.rc3
* Added `README.md`
* Added `MANUAL.md`
## 0.0.2.rc4
* Added `CHANGELOG.md`
## 0.0.3
* Changed Pig HP from 5 to 10
* Added entity indicators
* Added `noise` to the list of dependencies in `README.md`
* Created `dependencies`
* Bug fixes
### 0.0.4
* Added new Animal AI that makes them slower
* Moved old Animal Entity class with old AI to a new class called `FastAnimalEntity`
* Moved config into multiple different files located in the `config` directory
* Changed color of menu title
* Changed color of menu background
* Changed color of entity indicators
* Changed menu margins
* Changed *health indicators* to *entity indicators* in last versions changelog
* Changed the rendering system so it only renders things the player can see
* Changed grass texture
* Changed `indicators.color` to `indicators.background` in `config/indicators.json`
* Changed `targetSurface` to `target_surface` in `__main__.py`
* Changed `defaultFont` to `default_font` in `__main__.py`
* Changed `defaultTileset` to `default_tileset` in `__main__.py`
* Moved menu background color into config file
* Switched from `noise` to `opensimplex`
* Added seeds
* Added the Help Browser
* Added stairwells
* Added dungeons
* Changed from 2D maps to 3D maps
* Fixes to do with the 2D to 3D transition
* Changed version system for pre-releases from `X.X.X.alpha-X` to `X.X.X-alpha.X`