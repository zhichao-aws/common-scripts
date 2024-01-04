uninstall and install plugin
```
./bin/opensearch-plugin remove opensearch-ml && ./bin/opensearch-plugin install file:/home/ubuntu/olly/ml-commons/plugin/build/distributions/opensearch-ml-2.11.0.0-SNAPSHOT.zip
```

run integ test remote
```
./gradlew integTestRemote -Dtests.rest.cluster=localhost:9200 -Dtests.cluster=localhost:9200 -Dtests.clustername="opensearch" -Dhttps=true -Duser=admin -Dpassword=admin --tests "*NeuralSparseToolIT*"
```