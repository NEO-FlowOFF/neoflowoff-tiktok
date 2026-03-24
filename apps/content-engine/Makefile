.PHONY: setup mine run auto research-auto runtime-ls runtime-clean runtime-clean-keep-example

MINIO_USER ?= minioadmin
MINIO_PASS ?= minioadmin123
MINIO_BUCKET ?= tiktok-assets

setup:
	python3 -m venv .venv
	.venv/bin/python -m pip install -r requirements.txt

mine:
	.venv/bin/python scripts/mine_tiktok_shop.py

run:
	.venv/bin/python scripts/run_neo_tiktokshop.py

auto:
	docker start minio >/dev/null 2>&1 || docker run -d --name minio -p 9000:9000 -p 9001:9001 -e MINIO_ROOT_USER=$(MINIO_USER) -e MINIO_ROOT_PASSWORD=$(MINIO_PASS) -v minio-data:/data minio/minio server /data --console-address ":9001"
	docker run --rm --entrypoint /bin/sh minio/mc -c 'mc alias set local http://host.docker.internal:9000 $(MINIO_USER) $(MINIO_PASS) && mc mb --ignore-existing local/$(MINIO_BUCKET) && mc anonymous set download local/$(MINIO_BUCKET)'
	.venv/bin/python scripts/run_neo_tiktokshop.py

research-auto:
	.venv/bin/python scripts/mine_tiktok_shop.py
	docker start minio >/dev/null 2>&1 || docker run -d --name minio -p 9000:9000 -p 9001:9001 -e MINIO_ROOT_USER=$(MINIO_USER) -e MINIO_ROOT_PASSWORD=$(MINIO_PASS) -v minio-data:/data minio/minio server /data --console-address ":9001"
	docker run --rm --entrypoint /bin/sh minio/mc -c 'mc alias set local http://host.docker.internal:9000 $(MINIO_USER) $(MINIO_PASS) && mc mb --ignore-existing local/$(MINIO_BUCKET) && mc anonymous set download local/$(MINIO_BUCKET)'
	.venv/bin/python scripts/run_neo_tiktokshop.py

runtime-ls:
	@find runtime -type f | sort

runtime-clean:
	python3 ../../tools/clean_content_runtime.py --runtime-dir runtime

runtime-clean-keep-example:
	python3 ../../tools/clean_content_runtime.py --runtime-dir runtime --keep-example
