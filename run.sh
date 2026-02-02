#!/usr/bin/with-contenv bashio

bashio::log.info "Starting OctoDNS GUI Add-on..."

# Read configuration
DNS_PROVIDER=$(bashio::config 'dns_provider')
ZONE_FILE_PATH=$(bashio::config 'zone_file_path')

bashio::log.info "DNS Provider: ${DNS_PROVIDER:-not configured}"
bashio::log.info "Zone File Path: ${ZONE_FILE_PATH}"

# Create zone directory if it doesn't exist
if [ ! -d "$ZONE_FILE_PATH" ]; then
    bashio::log.info "Creating zone directory: ${ZONE_FILE_PATH}"
    mkdir -p "$ZONE_FILE_PATH"
fi

# Export config as environment variables for the app
export DNS_PROVIDER
export ZONE_FILE_PATH

# Check if SUPERVISOR_TOKEN is present
if [ -z "$SUPERVISOR_TOKEN" ]; then
    bashio::log.warning "SUPERVISOR_TOKEN not found. API calls will fail."
else
    bashio::log.info "SUPERVISOR_TOKEN found."
fi

bashio::log.info "Starting Flask server on port 8100..."

# Start the Python application
exec python3 /app/app.py
