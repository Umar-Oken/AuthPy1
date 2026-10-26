# AuthPy1

Django authentication project with email verification.

## Configuration

Copy `.env.example` to `.env` and replace every placeholder with environment-specific values. Generate a unique Django signing key and use dedicated database and SMTP credentials. Never commit `.env`.

The default configuration is production-oriented (`DJANGO_DEBUG=False`) and expects an HTTPS `PUBLIC_ORIGIN` and explicit `ALLOWED_HOSTS`. Configure HTTPS at the application or trusted proxy, then enable HSTS after confirming the deployment. For local HTTP development, set `DJANGO_DEBUG=True` and use local hostnames and an HTTP `PUBLIC_ORIGIN`; do not use development settings in production.

## Security

This project is a starter application, not a substitute for a deployment-specific security review. Keep dependencies patched, use HTTPS, rotate any credential that may have been exposed, and report vulnerabilities privately as described in [SECURITY.md](SECURITY.md). Do not put secrets, personal data, database dumps, or uploaded user files in the public repository.
