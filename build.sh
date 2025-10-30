#!/bin/bash
# Vercel build script to install Playwright browsers

echo "Installing Playwright browsers..."
playwright install chromium --with-deps

echo "Playwright installation complete!"
