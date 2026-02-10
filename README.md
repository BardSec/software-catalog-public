# Software Catalog

A searchable, filterable software catalog for school district staff. Provides SSO authentication via Microsoft 365 and Google Workspace, with an admin panel for managing entries.

## Features

- **Search & Filter**: Real-time search by name/tagline, filter by DPA status, cost/school, rostering method, and more
- **Category Badges**: Color-coded badges for DPA status (green/yellow/red), cost (blue), rostering (purple), and access (orange)
- **SSO Authentication**: Microsoft 365 (Azure AD) and Google Workspace sign-in
- **Domain Restriction**: Only users from allowed email domains can access the catalog
- **Admin Panel**: Add, edit, and delete software entries; manage categories
- **Responsive Design**: Works on desktop and mobile devices
- **Dark Mode**: Automatic dark mode based on system preference
- **Docker Deployment**: Single container with SQLite, ready for Cloudflare tunnel

## Quick Start

### 1. Clone and Configure

```bash
git clone <repo-url>
cd software-catalog
cp .env.example .env
```

Edit `.env` with your values (see [Configuration](#configuration) below).

### 2. Build and Run

```bash
docker compose up -d --build
```

The app will:
1. Build the container
2. Auto-seed the database from `software_directory.json` on first run
3. Start on port 5000 (configurable via `PORT` in `.env`)

### 3. Access

- Catalog: `http://localhost:5000`
- Admin: `http://localhost:5000/admin` (requires admin email)

## Configuration

All configuration is via environment variables in `.env`:

| Variable | Description | Example |
|---|---|---|
| `SECRET_KEY` | Flask secret key (generate a random string) | `openssl rand -hex 32` |
| `MICROSOFT_CLIENT_ID` | Azure AD App Registration client ID | `xxxxxxxx-xxxx-...` |
| `MICROSOFT_CLIENT_SECRET` | Azure AD App Registration client secret | `xxxxxxxx` |
| `MICROSOFT_TENANT_ID` | Azure AD tenant ID (your org) | `xxxxxxxx-xxxx-...` |
| `GOOGLE_CLIENT_ID` | Google OAuth 2.0 client ID | `xxxxx.apps.googleusercontent.com` |
| `GOOGLE_CLIENT_SECRET` | Google OAuth 2.0 client secret | `GOCSPX-xxxxx` |
| `ADMIN_EMAILS` | Comma-separated admin emails | `admin@district.org,tech@district.org` |
| `ALLOWED_DOMAINS` | Comma-separated allowed email domains | `district.org` |
| `PORT` | Host port to expose (default: 5000) | `5000` |

## Setting Up Authentication

### Microsoft 365 (Azure AD)

1. Go to [Azure Portal](https://portal.azure.com) > **Azure Active Directory** > **App registrations**
2. Click **New registration**
   - Name: `Software Catalog`
   - Supported account types: **Single tenant** (your org only)
   - Redirect URI: **Web** > `https://your-domain.com/callback/microsoft`
3. Note the **Application (client) ID** and **Directory (tenant) ID**
4. Go to **Certificates & secrets** > **New client secret** > copy the value
5. Go to **API permissions** > ensure `openid`, `email`, `profile` are granted
6. Add values to `.env`:
   ```
   MICROSOFT_CLIENT_ID=<application-id>
   MICROSOFT_CLIENT_SECRET=<client-secret>
   MICROSOFT_TENANT_ID=<tenant-id>
   ```

### Google Workspace

1. Go to [Google Cloud Console](https://console.cloud.google.com) > **APIs & Services** > **Credentials**
2. Click **Create Credentials** > **OAuth 2.0 Client ID**
   - Application type: **Web application**
   - Authorized redirect URI: `https://your-domain.com/callback/google`
3. Note the **Client ID** and **Client Secret**
4. Add values to `.env`:
   ```
   GOOGLE_CLIENT_ID=<client-id>
   GOOGLE_CLIENT_SECRET=<client-secret>
   ```

## Cloudflare Tunnel Setup

This app is designed to sit behind a Cloudflare tunnel for TLS termination.

1. Install `cloudflared` on your VPS
2. Create a tunnel: `cloudflared tunnel create software-catalog`
3. Configure the tunnel to route your hostname to `http://localhost:5000`
4. Update your OAuth redirect URIs to use your Cloudflare hostname

## Management Commands

**Re-seed the database** (resets all data from JSON):
```bash
docker compose exec catalog python seed.py
```

**View logs**:
```bash
docker compose logs -f catalog
```

**Restart**:
```bash
docker compose restart catalog
```

## Tech Stack

- **Backend**: Python Flask, SQLAlchemy, Flask-Login
- **Auth**: Authlib (OIDC)
- **Database**: SQLite
- **Frontend**: Jinja2 templates, vanilla JavaScript
- **Server**: Gunicorn
- **Deployment**: Docker
