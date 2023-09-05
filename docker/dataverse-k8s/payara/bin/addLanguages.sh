#!/bin/bash

# Check if at least one language is provided
if [ $# -lt 1 ]; then
    echo "Usage: $0 <language1> <language2> ..."
    exit 1
fi

# Store the passed arguments as an array
languages=("$@")

# Titles for languages
declare -A titles=(
    ["en"]="English"
    ["de"]="Deutsch"
    ["fr"]="Français"
    ["at"]="Deutsch - Österreich"
    ["us"]="English - United States"
    ["es"]="Español - España"
    ["ca"]="Français - Canada"
    ["hu"]="Magyar - Magyarország"
    ["it"]="Italiano - Italia"
    ["pl"]="Polski - Polska"
    ["br"]="Português - Brasil"
    ["pt"]="Português - Portugal"
    ["ru"]="Русский - Россия"
    ["se"]="Svenska - Sverige"
    ["sl"]="Slovenščina - Slovenija"
    ["ua"]="Українська - Україна"
)

# Clear directory and setting before adding languages
rm -rf /opt/docroot/langBundles
curl -X DELETE http://localhost:8080/api/admin/settings/:Languages
curl -X DELETE http://localhost:8080/api/admin/settings/:MetadataLanguages
asadmin --user=admin --passwordfile=/secrets/asadmin/passwordFile delete-jvm-options "-Ddataverse.lang.directory=/opt/docroot/langBundles"

# Create directories
mkdir -p /opt/docroot/langBundles/tmp/languages
mkdir -p /opt/docroot/languages

# Safe file with enabled languages for persistence
echo ${languages[@]} > /opt/docroot/languages/languages

# Enable languages
dropdown='['
for lang in "${languages[@]}"; do
    locale="${lang%%_*}"
    title="${titles[$locale]}"
    dropdown+='{"locale":"'${locale}'","title":"'${title}'"},'
done
dropdown=${dropdown%,}  # Remove trailing comma
dropdown+=']'

curl http://localhost:8080/api/admin/settings/:Languages -X PUT -d "$dropdown"
curl http://localhost:8080/api/admin/settings/:MetadataLanguages -X PUT -d "$dropdown"

asadmin --user=admin --passwordfile=/secrets/asadmin/passwordFile create-jvm-options "-Ddataverse.lang.directory=/opt/docroot/langBundles"
git clone -b dataverse-v5.13 https://github.com/GlobalDataverseCommunityConsortium/dataverse-language-packs.git /opt/docroot/langBundles/data

# Rename directories (change - to _)
for lang_dir in /opt/docroot/langBundles/data/*; do
    if [[ "$lang_dir" == *-* ]]; then
        new_lang_dir="${lang_dir//-/_}"
        mv "$lang_dir" "$new_lang_dir"
    fi
done

# Copy language packages and create zip
for lang in "${languages[@]}"; do
    cp -R /opt/docroot/langBundles/data/$lang/*.properties /opt/docroot/langBundles/tmp/languages
done
cd /opt/docroot/langBundles/tmp/languages && zip languages.zip *.properties

# Move languages.zip in langBundles for restarting
mv /opt/docroot/langBundles/tmp/languages/languages.zip /opt/docroot/langBundles/languages.zip

# Load property files
curl http://localhost:8080/api/admin/datasetfield/loadpropertyfiles -X POST --upload-file /opt/docroot/langBundles/languages.zip -H "Content-Type: application/zip"

# Clean up
rm -rf /opt/docroot/langBundles/data
rm -rf /opt/docroot/langBundles/tmp