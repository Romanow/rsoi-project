postgresPod=$1

cat ../postgres/init_qrook_auth.pgsql        | kubectl exec -i $postgresPod -- psql -U kurush qrook_auth
cat ../postgres/init_qrook_library.pgsql        | kubectl exec -i $postgresPod -- psql -U kurush qrook_library
cat ../postgres/init_qrook_scout.pgsql        | kubectl exec -i $postgresPod -- psql -U kurush qrook_scout