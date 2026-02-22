# Software Catalog

A searchable, filterable software catalog web application. Provides SSO authentication via Microsoft 365 and Google Workspace, with an admin panel for managing entries. Designed for school districts and other organizations that need to maintain an approved software directory for staff.

## Features

- **Search & Filter**: Real-time search by name/tagline, filter by DPA status, cost/school, rostering method, and more
- **Category Badges**: Color-coded badges for DPA status (green/yellow/red), cost (blue), rostering (purple), and access (orange)
- **SSO Authentication**: Microsoft 365 (Azure AD) and Google Workspace sign-in
- **Domain Restriction**: Only users from allowed email domains can access the catalog
- **Admin Panel**: Add, edit, and delete software entries; manage categories
- **Responsive Design**: Works on desktop and mobile devices
- **Dark Mode**: Automatic dark mode based on system preference
- **Docker Deployment**: Single container with SQLite, ready for Cloudflare tunnel

## Pre-Reqs: Gather Before You Begin

- **Microsoft365 or Google Workspace App Registration**: Create an app registration and copy down the following:
  - Microsoft
    - Tenant ID
    - App (Client) ID
    - Secret Value
    - Redirect URI
   
- **Create Flask Secret Key for .Env file**:
```bash
openssl rand -hex 32
```

- **Cloudflare Hostname Route**: More details [in this previous article](https://www.edtechirl.com/p/using-cloudflare-to-expose-local). 
- **Prepare Virtual Machine to Host**: for Cloud Deployments, I use Linode.
  - Recommended OS: [Ubuntu Server 24.04 LTS](https://ubuntu.com/download/server_) (Or current LTS at time of install)
  - [Install Cloudflare Tunnel](https://developers.cloudflare.com/cloudflare-one/networks/connectors/cloudflare-tunnel/get-started/create-remote-tunnel/)
  - [Install Docker](https://docs.docker.com/engine/install/ubuntu/) 

## Quick Start

### 1. Clone and Configure

```bash
git clone https://github.com/BardSec/software-catalog-public
cd software-catalog-public
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

- Catalog: `http://<serverIP>:5000`
- Admin: `http://<serverIP>:5000/admin` (requires admin email as configured in the .env file)... For what it's worth, you don't need to use the separate admin subdirectory for Admin access. If you are configured as an admin, there will be an Admin button in the regular UI.

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
4. Go to **Certificates & secrets** > **New client secret** > copy the secret value (you don't need the secret ID)
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

## Custom Login Logo

To display your organization's logo on the login page, place a logo file in `app/static/img/`:

```bash
cp /path/to/your-logo.png app/static/img/logo.png
```

Supported filenames: `logo.png`, `logo.svg`, `logo.jpg`, `logo.webp`. The first match found (in that order) will be used. Recommended size is around 200x200px; the image will display at a max height of 80px.

If no logo file is present, the login page displays without one — no configuration needed.

## Cloudflare Tunnel Setup

This app is designed to sit behind a Cloudflare tunnel for TLS termination. The basic steps:

1. Install `cloudflared` on your VPS (instructions inside of Cloudflare -> Zero Trust -> Networks -> Connectors)
2. Create a tunnel
3. Configure the tunnel to route your hostname to `http://<serverIP>:5000`
4. Update your OAuth redirect URIs to use your Cloudflare hostname (I usually configure this from the beginning, because Azure really like TLS encryption for redirect URIs). 

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

## Known Issues
- **Dark Mode**: This has been finicky so far... still tweaking.

## Pro Tip
- If editing in the GUI is a little slow for you. When you first spin up Software Catalog, there are a handful of sample software cards entered as placeholders. If you go to the admin panel and choose Export it will export a JSON file of those 10 pieces of software. For me, if I'm entering a ton of these in bulk, it goes MUCH faster to just manually edit the JSON, then re-import it from the admin panel. When you import, you can choose whether to dump all current cards and reinstall the new ones, OR you can choose to merge the new JSON with the existing. 
