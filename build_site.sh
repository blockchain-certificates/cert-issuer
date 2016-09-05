#!/bin/bash
######################################################################################
#
# This script regenerates the repo site documentation to be published by github pages. 
#
# We use jekyll to convert markdown-formatted documentation to html. This script 
# automates some workarounds we're making to avoid the following nuisances:
# - site files cluttering the codebase
# - maintaining a separate gh-pages branch
#
# This script uses the site_config information, along with the documentation in 
# docs_md, to create the site. It then places the updated site in the docs/
# folder, where it can be seen by github pages.
#
# Structure: 
# - site_config folder contains the web site templates. It only needs to be updated
#   when you want to make changes to the web site layout, template data, etc
# - docs_md is where you should place your documentation, in markdown format, with a
#   special header required by jekyll (see below)
# - docs is regenerated when you run this script. Never directly edit files in that
#   folder -- they'll be discarded
#
# Jekyll header for .md files:
#
# Jekyll requires a header like the following to process the file. The header 
# specification allows additional info like tags, but this is the minimum set we 
# need.
#
# ---
# layout: page
# title: Page Title
# ---
######################################################################################

cd site_config
bundle install
cp ../docs_md/* .
bundle exec jekyll build --verbose

cd ..
# docs folder is generated; delete old one first
if [ -d docs ]; then
    rm -rf docs
fi

cp -R site_config/_site docs
git add .

echo ""
echo "Site documentation is updated. You still need to add, commit, and push these changes"

