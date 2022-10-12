setup: requirements.txt
	pip install -r requirements.txt

.PHONY: deploy
deploy:
	kubectl apply -f kubernetes/mysql-deployment.yaml
	kubectl apply -f kubernetes/mysql-service.yaml
	kubectl apply -f kubernetes/mysql-pv.yaml
	kubectl apply -f kubernetes/mysql-pvc.yaml
	kubectl wait --for=condition=Available --timeout=32s deployment/mysql
	kubectl apply -f kubernetes/web-deployment.yaml
	kubectl apply -f kubernetes/web-service.yaml
	kubectl wait --for=condition=Available --timeout=32s deployment/web
	kubectl apply -f kubernetes/nginx-autoscaler.yaml
	kubectl apply -f kubernetes/nginx-deployment.yaml
	kubectl apply -f kubernetes/nginx-service.yaml
	kubectl apply -f kubernetes/nginx-autoscaler.yaml

.PHONY: clean
clean:
	kubectl delete deploy mysql
	kubectl delete deploy web
	kubectl delete deploy nginx
	kubectl delete service mysql
	kubectl delete service web
	kubectl delete service nginx
	kubectl delete hpa nginx
	rm -rf __pycache__


compose:
	docker-compose up --build -d

compose-down:
	docker-compose down

.PHONY: tests
tests:
	pytest tests