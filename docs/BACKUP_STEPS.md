# Backup Steps (Mandatory Before Cleanup)

## 1) Project Backup
Run a dry-run first:

```bash
py -m tools.backup_project
```

Run the real backup:

```bash
py -m tools.backup_project --yes
```

Result:
- Creates `backups/project_backup_<timestamp>.zip`
- For SQLite, also creates `backups/sqlite_backup_<timestamp>.db`

## 2) Database Backup
### SQLite
- Default path is derived from `DATABASE_URL` in `.env`.
- The backup script copies the SQLite file automatically with `--yes`.

### Postgres (Neon/Supabase/other)
Use `pg_dump` manually:

```bash
pg_dump "$DATABASE_URL" > backups/postgres_backup.sql
```

Windows PowerShell example:

```powershell
pg_dump $env:DATABASE_URL | Out-File -Encoding utf8 backups\\postgres_backup.sql
```

## 3) Safety Rule
- Do not run `db_reset` with `--yes` before backup artifacts exist.
- Keep at least one project ZIP and one DB backup copy.
