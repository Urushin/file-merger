
# File Merger

## Description

**File Merger** est une application graphique (GUI) développée en Python qui permet de fusionner facilement des fichiers texte et PDF. Avec une interface conviviale, vous pouvez ajouter des fichiers ou des dossiers, réorganiser l'ordre des fichiers, prévisualiser leur contenu, générer une table des matières, compresser le fichier de sortie en ZIP, et même planifier des fusions automatiques.

## Fonctionnalités

- **Ajout de Fichiers et Dossiers** : Ajoutez individuellement des fichiers ou sélectionnez un dossier pour ajouter tous ses fichiers.
- **Drag-and-Drop** : Glissez-déposez des fichiers ou des dossiers directement dans l'application.
- **Réorganisation des Fichiers** : Déplacez les fichiers vers le haut ou vers le bas dans la liste pour définir l'ordre de fusion.
- **Prévisualisation** : Affichez le contenu des fichiers texte ou PDF avant la fusion.
- **Génération de Table des Matières** : Incluez une table des matières dans le fichier fusionné (texte uniquement).
- **Compression ZIP** : Compressez le fichier de sortie en format ZIP.
- **Planification de Fusion** : Programmez des fusions automatiques à des heures spécifiques chaque jour.
- **Sauvegarde et Chargement de Configurations** : Exportez et importez les configurations de fusion via des fichiers JSON.
- **Support des Fichiers PDF** : Fusionnez efficacement des fichiers PDF en utilisant PyPDF2.

## Installation

### Prérequis

Assurez-vous d'avoir Python 3.6 ou une version ultérieure installée sur votre système. Vous pouvez télécharger Python [ici](https://www.python.org/downloads/).

### Cloner le Répertoire

Clonez ce dépôt GitHub sur votre machine locale :

```bash
git clone https://github.com/urushin/file-merger.git
cd file-merger
```

### Installer les Dépendances

Utilisez `pip` pour installer toutes les dépendances nécessaires :

```bash
pip install -r requirements.txt
```

### Modules Requis

Les principales bibliothèques utilisées dans ce projet sont :

- `PyPDF2` : Pour la manipulation et la fusion de fichiers PDF.
- `tkPDFViewer` : Pour la prévisualisation des fichiers PDF dans l'application GUI.
- `schedule` : Pour la planification des tâches de fusion.
- `tkinterdnd2` : Pour la fonctionnalité de drag-and-drop.

### Utilisation d'un Environnement Virtuel (Recommandé)

Il est recommandé d'utiliser un environnement virtuel pour gérer les dépendances du projet :

```bash
python -m venv env
source env/bin/activate  # Sur Windows : env\Scripts\activate
pip install -r requirements.txt
```

## Utilisation

Lancez l'application en exécutant le fichier Python :

```bash
python file_merger.py
```

### Étapes de Base

1. **Ajouter des Fichiers ou Dossiers** :
   - Cliquez sur **Ajouter Fichiers** pour sélectionner des fichiers individuels.
   - Cliquez sur **Ajouter Dossier** pour sélectionner un dossier entier dont tous les fichiers seront ajoutés.
   - Vous pouvez également glisser-déposer des fichiers ou des dossiers directement dans la liste.

2. **Gérer la Liste des Fichiers** :
   - **Supprimer Sélection** : Retirez un fichier de la liste.
   - **Monter/Descendre** : Changez l'ordre des fichiers pour définir l'ordre de fusion.
   - **Prévisualiser** : Visualisez le contenu d'un fichier avant la fusion.

3. **Configurer les Options de Fusion** :
   - **Encodage des Fichiers** : Sélectionnez l'encodage approprié.
   - **Type de Fusion** : Choisissez entre **Text** et **PDF**.
   - **Générer une Table des Matières** : Cochez si vous souhaitez inclure une table des matières (texte uniquement).
   - **Compresser le Fichier de Sortie** : Cochez pour compresser le fichier fusionné en ZIP.
   - **Planifier une Fusion** : Cochez pour planifier une fusion quotidienne à une heure spécifique.

4. **Fusionner les Fichiers** :
   - Cliquez sur **Fusionner les Fichiers**.
   - Choisissez l'emplacement et le nom du fichier de sortie (nom par défaut : `merged_files`).
   - Si la compression est activée, choisissez également l'emplacement et le nom du fichier ZIP.
