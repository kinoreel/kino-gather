export-globals:
	python -c "import processes.GLOBALS as globals; globals.export()"

build-image:
	docker build -t kino-gather-api .

run-image:
	docker run -p 3002:5000 -d --name kino-gather kino-gather-api

push-image:
	docker tag kino-gather-api unrufflednightingale/kino-gather-api:latest
	docker push unrufflednightingale/kino-gather-api:latest

build-and-push-image: build-image push-image