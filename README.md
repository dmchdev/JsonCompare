# JsonCompare
## A library/application to compare two json blobs of the same schema 

Given 2 JSON structures, this will determine whether data in the expected is contained
in the actual. The list order is optional, ignored by default. This assumes the same schema for both JSON
blobs, so that values in expected can be reached using the same path as in actual. The only deviation is the 
list order which is ignored by default where present and is controlled by 'keeporder' parameter
