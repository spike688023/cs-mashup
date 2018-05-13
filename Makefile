default: run

pull:
	docker pull spike688023/cs-mashup && docker tag spike688023/cs-mashup cs50/mashup

build:
	docker build -t cs50/mashup .

rebuild:
	docker build --no-cache -t cs50/mashup .

run:
	#docker run -i --name server -p 8080:8080 -v "$(PWD)"/examples/flask:/var/www -d -t cs50/mashup
	docker run -i --name server_mashup -p 8081:8081 -d -t cs50/mashup

shell:
	docker exec -it server_mashup bash -l

logs:
	docker logs server_mashup

rm:
	docker rm -f server_mashup
