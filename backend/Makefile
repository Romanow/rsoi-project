test: unit_tests integration_tests e2e_tests

unit_tests:
	pytest -m unit .
integration_tests:
	pytest -m integration .
e2e_tests:
	python3 test_e2e.py -n=100


version=3.0
docker_build:
	docker build -t kurushpondoxocrow/qrook_search:$(version) -f SearchServiceDockerfile .
	docker build -t kurushpondoxocrow/qrook_scout:$(version) -f ScoutServiceDockerfile .
	docker build -t kurushpondoxocrow/qrook_auth:$(version) -f AuthServiceDockerfile .
	docker build -t kurushpondoxocrow/qrook_file:$(version) -f FileServiceDockerfile .
	docker build -t kurushpondoxocrow/qrook_api:$(version) -f APIServiceDockerfile .
	docker build -t kurushpondoxocrow/qrook_postgres:$(version) -f PostgresDockerfile .

docker_push:
	docker push kurushpondoxocrow/qrook_search:$(version)
	docker push kurushpondoxocrow/qrook_scout:$(version)
	docker push  kurushpondoxocrow/qrook_auth:$(version)
	docker push kurushpondoxocrow/qrook_file:$(version)
	docker push kurushpondoxocrow/qrook_api:$(version)
	docker push kurushpondoxocrow/qrook_postgres:$(version)

docker_pull:
	docker pull kurushpondoxocrow/qrook_search:$(version)
	docker pull kurushpondoxocrow/qrook_scout:$(version)
	docker pull kurushpondoxocrow/qrook_auth:$(version)
	docker pull kurushpondoxocrow/qrook_file:$(version)
	docker pull kurushpondoxocrow/qrook_api:$(version)
	docker pull kurushpondoxocrow/qrook_postgres:$(version)