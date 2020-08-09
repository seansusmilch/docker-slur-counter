docker build -t slur-counter:1.0 .

docker run -it --rm --name slur `
-v /home/sean/docker/slur/config:/config `
-v /home/sean/docker/slur/data:/data `
-v /home/sean/docker/slur/logs:/logs `
slur-counter