#!/bin/bash

cd gearhead-caramel
git pull
cd ..

cp gearhead-caramel/credits.md build/
cp gearhead-caramel/README.md build/
cp gearhead-caramel/LICENSE build/
cp gearhead-caramel/history.txt build/
#git clone https://github.com/jwvhewitt/gearhead-caramel.git

sudo docker run -it -v /home/joseph/Documents/Programming/DockerExperimento/gearhead-caramel/:/src -v /home/joseph/Documents/Programming/DockerExperimento/:/util --name test-container --rm steam-amd64:latest /bin/bash /util/internal_use_only.sh

