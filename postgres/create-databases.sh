set -e
export SCRIPT_PATH=/docker-entrypoint-initdb.d/
export PGPASSWORD=pondoxo

psql -U kurush -d qrook -f "$SCRIPT_PATH/databases.sql"
psql -U kurush qrook_auth < $SCRIPT_PATH/init_qrook_auth.pgsql
psql -U kurush qrook_library < $SCRIPT_PATH/init_qrook_library.pgsql
psql -U kurush qrook_scout < $SCRIPT_PATH/init_qrook_scout.pgsql