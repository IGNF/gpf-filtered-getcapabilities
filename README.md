## gpf-filtered-getcapabilities
Fournit des getCapabilities filtrés par thématiques pour les services de la géoplateforme.

### Données en entrée
Se base sur le fichier "services.csv" disponible à cette adresse https://data.geopf.fr/annexes/ressources/capabilities/services.csv et sur les getCapabilities géoplateforme

### Données en sortie
1 fichier getCapabilities par service de diffusion (WMTS, WMS Raster, WMS Vecteur et WFS) et par thématique (ex "clef").

L'URL du getCapabilities filtré suit le schema suivant : `https://raw.githubusercontent.com/IGNF/gpf-filtered-getcapabilities/main/dist/<SERVICE>/<CLEF>.xml` (par exemple : https://raw.githubusercontent.com/IGNF/gpf-filtered-getcapabilities/main/dist/wmts/essentiels.xml)

## Fréquence de mise à jour
La génération se fait tous les dimanches, et peut se faire manuellement via le menu `Actions` du dépôt.
