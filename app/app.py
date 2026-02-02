import os
import yaml
import requests
from pathlib import Path
from flask import Flask, request, render_template, jsonify, redirect, url_for

app = Flask(__name__)

SUPERVISOR_TOKEN = os.environ.get('SUPERVISOR_TOKEN')
ZONE_FILE_PATH = os.environ.get('ZONE_FILE_PATH', '/config/octodns')
DNS_PROVIDER = os.environ.get('DNS_PROVIDER', '')


def get_user_info():
    """Extract user info from Ingress headers."""
    return {
        'id': request.headers.get('X-Remote-User-Id'),
        'name': request.headers.get('X-Remote-User-Display-Name')
               or request.headers.get('X-Remote-User-Name')
               or 'Unknown',
        'username': request.headers.get('X-Remote-User-Name'),
    }


def get_zone_files():
    """List all zone files in the configured directory."""
    zone_path = Path(ZONE_FILE_PATH)
    if not zone_path.exists():
        zone_path.mkdir(parents=True, exist_ok=True)
        return []

    zones = []
    for f in zone_path.glob('*.yaml'):
        try:
            with open(f) as file:
                data = yaml.safe_load(file)
                record_count = sum(len(v) if isinstance(v, list) else 1
                                   for v in data.values()) if data else 0
                zones.append({
                    'name': f.stem,
                    'file': f.name,
                    'records': record_count,
                })
        except Exception as e:
            zones.append({
                'name': f.stem,
                'file': f.name,
                'records': 0,
                'error': str(e),
            })
    return zones


def load_zone(zone_name):
    """Load a zone file and return its contents."""
    zone_file = Path(ZONE_FILE_PATH) / f"{zone_name}.yaml"
    if not zone_file.exists():
        return None

    with open(zone_file) as f:
        return yaml.safe_load(f) or {}


def save_zone(zone_name, data):
    """Save zone data to a YAML file."""
    zone_file = Path(ZONE_FILE_PATH) / f"{zone_name}.yaml"
    zone_file.parent.mkdir(parents=True, exist_ok=True)

    with open(zone_file, 'w') as f:
        yaml.dump(data, f, default_flow_style=False, allow_unicode=True)


@app.route('/')
def index():
    user = get_user_info()
    zones = get_zone_files()
    return render_template('index.html',
                           user=user,
                           zones=zones,
                           dns_provider=DNS_PROVIDER)


@app.route('/zone/<zone_name>')
def view_zone(zone_name):
    user = get_user_info()
    zone_data = load_zone(zone_name)
    if zone_data is None:
        return "Zone not found", 404

    return render_template('zone.html',
                           user=user,
                           zone_name=zone_name,
                           zone_data=zone_data)


@app.route('/zone/<zone_name>/edit', methods=['GET', 'POST'])
def edit_zone(zone_name):
    user = get_user_info()

    if request.method == 'POST':
        try:
            yaml_content = request.form.get('yaml_content', '')
            data = yaml.safe_load(yaml_content)
            save_zone(zone_name, data)
            return redirect(url_for('view_zone', zone_name=zone_name))
        except yaml.YAMLError as e:
            return render_template('edit_zone.html',
                                   user=user,
                                   zone_name=zone_name,
                                   yaml_content=yaml_content,
                                   error=f"YAML Error: {e}")

    zone_data = load_zone(zone_name)
    yaml_content = yaml.dump(zone_data, default_flow_style=False) if zone_data else ''

    return render_template('edit_zone.html',
                           user=user,
                           zone_name=zone_name,
                           yaml_content=yaml_content)


@app.route('/zone/new', methods=['GET', 'POST'])
def new_zone():
    user = get_user_info()

    if request.method == 'POST':
        zone_name = request.form.get('zone_name', '').strip()
        if not zone_name:
            return render_template('new_zone.html', user=user, error="Zone name required")

        # Sanitize zone name
        zone_name = zone_name.replace(' ', '-').lower()
        zone_file = Path(ZONE_FILE_PATH) / f"{zone_name}.yaml"

        if zone_file.exists():
            return render_template('new_zone.html', user=user,
                                   error=f"Zone '{zone_name}' already exists")

        # Create empty zone
        save_zone(zone_name, {'': {'type': 'A', 'value': ''}})
        return redirect(url_for('edit_zone', zone_name=zone_name))

    return render_template('new_zone.html', user=user)


@app.route('/api/zones')
def api_zones():
    """API endpoint to list all zones."""
    return jsonify(get_zone_files())


@app.route('/api/zone/<zone_name>')
def api_zone(zone_name):
    """API endpoint to get zone data."""
    data = load_zone(zone_name)
    if data is None:
        return jsonify({'error': 'Zone not found'}), 404
    return jsonify(data)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8100, debug=False)
