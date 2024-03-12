#!/bin/bash

#
# Copyright 2023 OrdinaryRoad
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
export APP_VERSION=1.1.1

# 1 后端
cd ../barrage-fly
./gradlew clean bootJar
cd ../.docker/ordinaryroad-barrage-fly
docker build . -f Dockerfile -t ordinaryroad-barrage-fly:${APP_VERSION}
docker tag ordinaryroad-barrage-fly:${APP_VERSION} ordinaryroad-barrage-fly
docker build . -f Dockerfile-arm64 -t ordinaryroad-barrage-fly-arm64:${APP_VERSION}
docker tag ordinaryroad-barrage-fly-arm64:${APP_VERSION} ordinaryroad-barrage-fly-arm64

# 2 前端
cd ../../barrage-fly-ui
npm run copy
cd ../.docker/ordinaryroad-barrage-fly-ui/app
npm install
npm run build
cd ..

docker login ordinaryroad-docker.pkg.coding.net

# 构建并发布多平台版本
docker buildx build --platform linux/arm64,linux/amd64 --push . -f Dockerfile -t ordinaryroad-docker.pkg.coding.net/ordinaryroad-barrage-fly/docker-pub/ordinaryroad-barrage-fly-ui:${APP_VERSION}
docker buildx build --platform linux/arm64,linux/amd64 --push . -f Dockerfile -t ordinaryroad-docker.pkg.coding.net/ordinaryroad-barrage-fly/docker-pub/ordinaryroad-barrage-fly-ui

docker pull ordinaryroad-docker.pkg.coding.net/ordinaryroad-barrage-fly/docker-pub/ordinaryroad-barrage-fly-ui:${APP_VERSION}
docker tag ordinaryroad-docker.pkg.coding.net/ordinaryroad-barrage-fly/docker-pub/ordinaryroad-barrage-fly-ui:${APP_VERSION} ordinaryroad-barrage-fly-ui:${APP_VERSION}

docker pull ordinaryroad-docker.pkg.coding.net/ordinaryroad-barrage-fly/docker-pub/ordinaryroad-barrage-fly-ui
docker tag ordinaryroad-docker.pkg.coding.net/ordinaryroad-barrage-fly/docker-pub/ordinaryroad-barrage-fly-ui ordinaryroad-barrage-fly-ui

#docker logout ordinaryroad-docker.pkg.coding.net