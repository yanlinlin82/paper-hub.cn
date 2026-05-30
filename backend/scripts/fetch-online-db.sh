#!/bin/bash

PROJECT_DIR=$(cd $(dirname $0)/../..; pwd)

rsync -avP yanlinlin.cn:/var/www/paper-hub.cn/backend/db.sqlite3 $PROJECT_DIR/backend/db.sqlite3
