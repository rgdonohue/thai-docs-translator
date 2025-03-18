#!/bin/bash
# Script to search for vessel names in translated files

# Make sure script is executable
chmod +x search_vessels.sh

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Run the search script
python src/search_vessels.py "$@"

# Print summary of results
echo ""
echo "Search complete. Check output_data/fishing-vessels-updated.csv for results."
echo "Logs are available in logs/search.log" 