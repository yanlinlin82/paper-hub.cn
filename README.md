# Paper-Hub: An easy way to read and share papers for scientific research

## How to reset database

```sh
rm -fv db.sqlite3
rm -fvr view/migrations
python manage.py makemigrations view
python manage.py migrate
./scripts/001-import-excel.py XXX.xlsx
```
