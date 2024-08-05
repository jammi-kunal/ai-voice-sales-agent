train:
	rasa train --domain domain --config config.yml --fixed-model-name sales-model --debug

run-core:
	rasa run --enable-api --cors "*" --debug

run-actions:
	rasa run actions --actions actions.actions --debug

ngrok-api:
	ngrok http --domain=formally-closing-possum.ngrok-free.app 5006

ngrok-rasa:
	ngrok http --domain=marlin-upright-adversely.ngrok-free.app 5005

run-api:
	uvicorn voice_modules_fast_api:app --reload --host localhost --port 5006

train-docker:
	docker-compose run rasa train --domain domain --config config.yml --fixed-model-name sales-model --debug

run-docker:
	docker-compose up -d

ngrok-rasa-authtoken:
	ngrok config add-authtoken 1hqBgBczy6V8SQTdS97XMTI2Gtz_2s4QmpCBvAa4pEEkeXJYn

ngrok-api-authtoken:
	ngrok config add-authtoken 2Y9c98sS0ogEIjQhvxB4cSJ5hrM_7NbvrA6YBLr7PQb2EQJR5