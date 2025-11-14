#!/bin/bash

# Ask for commit message
read -p "Enter commit message: " msg

# Run git commands
git add .
git commit -m "$msg"
git push -u origin main
