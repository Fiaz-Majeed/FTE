"""
Odoo Community Edition Setup Guide and Docker Configuration
"""

# Docker Compose configuration for Odoo 19 Community Edition

DOCKER_COMPOSE_YAML = """version: '3.8'

services:
  odoo:
    image: odoo:19
    container_name: odoo19
    depends_on:
      - db
    ports:
      - "8069:8069"
    environment:
      - HOST=db
      - USER=odoo
      - PASSWORD=odoo
    volumes:
      - odoo-data:/var/lib/odoo
      - ./config:/etc/odoo
      - ./addons:/mnt/extra-addons
    restart: unless-stopped

  db:
    image: postgres:15
    container_name: odoo_postgres
    environment:
      - POSTGRES_DB=postgres
      - POSTGRES_USER=odoo
      - POSTGRES_PASSWORD=odoo
    volumes:
      - postgres-data:/var/lib/postgresql/data
    restart: unless-stopped

volumes:
  odoo-data:
  postgres-data:
"""

ODOO_CONF = """[options]
admin_passwd = admin
db_host = db
db_port = 5432
db_user = odoo
db_password = odoo
addons_path = /mnt/extra-addons
xmlrpc_port = 8069
"""

SETUP_INSTRUCTIONS = """# Odoo Community Edition Setup Guide

## Prerequisites

- Docker and Docker Compose installed
- At least 4GB RAM available
- Port 8069 available

## Installation Steps

### 1. Create Project Directory

```bash
mkdir -p odoo-fte
cd odoo-fte
mkdir -p config addons
```

### 2. Create docker-compose.yml

Save the Docker Compose configuration to `docker-compose.yml`

### 3. Create Odoo Configuration

Save the Odoo configuration to `config/odoo.conf`

### 4. Start Odoo

```bash
docker-compose up -d
```

### 5. Access Odoo

Open browser and navigate to: http://localhost:8069

### 6. Initial Setup

1. Create a new database:
   - Database Name: `odoo`
   - Email: `admin@example.com`
   - Password: `admin` (change this!)
   - Language: English
   - Country: Your country

2. Install Accounting Module:
   - Go to Apps
   - Search for "Accounting"
   - Click Install

### 7. Configure Accounting

1. Go to Accounting > Configuration > Settings
2. Set up:
   - Chart of Accounts
   - Fiscal Year
   - Journals
   - Payment Terms

### 8. Test JSON-RPC Connection

```python
import xmlrpc.client

url = "http://localhost:8069"
db = "odoo"
username = "admin@example.com"
password = "admin"

# Authenticate
common = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/common')
uid = common.authenticate(db, username, password, {})

print(f"Authenticated with UID: {uid}")

# Test connection
models = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/object')
partners = models.execute_kw(db, uid, password,
    'res.partner', 'search_read',
    [[]], {'fields': ['name'], 'limit': 5})

print(f"Found {len(partners)} partners")
```

## Troubleshooting

### Container won't start
```bash
docker-compose logs odoo
docker-compose logs db
```

### Reset database
```bash
docker-compose down -v
docker-compose up -d
```

### Access PostgreSQL directly
```bash
docker exec -it odoo_postgres psql -U odoo -d postgres
```

## Security Notes

1. Change default passwords in production
2. Use environment variables for credentials
3. Enable SSL/TLS for production
4. Restrict network access
5. Regular backups

## Integration with FTE

Once Odoo is running, the FTE Odoo MCP server will connect automatically:

```python
from fte.mcp.odoo_mcp_server import OdooClient

client = OdooClient(
    url="http://localhost:8069",
    db="odoo",
    username="admin@example.com",
    password="admin"
)

client.authenticate()
```

## Useful Commands

```bash
# Start Odoo
docker-compose up -d

# Stop Odoo
docker-compose stop

# View logs
docker-compose logs -f odoo

# Restart Odoo
docker-compose restart odoo

# Remove everything
docker-compose down -v
```

## Next Steps

1. Configure chart of accounts
2. Set up customers and vendors
3. Create product catalog
4. Configure payment methods
5. Set up bank accounts
6. Test invoice creation
7. Test payment recording
8. Generate financial reports

## Resources

- Odoo Documentation: https://www.odoo.com/documentation/19.0/
- Odoo Community: https://www.odoo.com/forum
- Docker Hub: https://hub.docker.com/_/odoo
"""

def create_setup_files(output_dir: str = "."):
    """Create Odoo setup files.

    Args:
        output_dir: Directory to create files in
    """
    from pathlib import Path

    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)

    # Create docker-compose.yml
    with open(output_path / "docker-compose.yml", "w") as f:
        f.write(DOCKER_COMPOSE_YAML)

    # Create config directory and odoo.conf
    config_dir = output_path / "config"
    config_dir.mkdir(exist_ok=True)
    with open(config_dir / "odoo.conf", "w") as f:
        f.write(ODOO_CONF)

    # Create addons directory
    addons_dir = output_path / "addons"
    addons_dir.mkdir(exist_ok=True)

    # Create README
    with open(output_path / "ODOO_SETUP.md", "w") as f:
        f.write(SETUP_INSTRUCTIONS)

    print(f"Odoo setup files created in {output_path}")
    print("\nNext steps:")
    print("1. cd to the output directory")
    print("2. Run: docker-compose up -d")
    print("3. Open http://localhost:8069")
    print("4. Follow the setup instructions in ODOO_SETUP.md")


if __name__ == "__main__":
    import sys
    output_dir = sys.argv[1] if len(sys.argv) > 1 else "odoo-fte"
    create_setup_files(output_dir)
