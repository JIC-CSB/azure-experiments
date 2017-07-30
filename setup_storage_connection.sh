export AZURE_STORAGE_CONNECTION_STRING=`az storage account show-connection-string --name dblueseastorage --resource-group test_resource_group_uk_west | jq .'connectionString'`
