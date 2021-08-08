## MOP Project - Scraping News & Fetching data REST API services

#### 1. Clone project from GitHub:

```sh
git clone https://github.com/YOUR-USERNAME/YOUR-REPOSITORY
```

#### 2. Build services

```sh
docker-compose build
```

#### 3. Environment variables

Are in .env.dev file.

#### 4. To run services

```sh
docker-compose up
```

When django service is started initial setup will be applyed

- superuser defined in .env.dev file will be created
- django-celery-beat will be configured to automatically start scraping news task every 10 minutes

