# Current implementation status

* Current template provides account in terms of *additions* and *deletions*, in teh future this can evolve to account for/detect *replacements, modifications and  movements*.
* Further adjustments are needed to synchronise with VB3-SKOS-AP or SKOS-AP (to be discussed what templates are needed).   
* Execution time ~ 5 minutes on Corporate Bodies table (queries for version and status seem to be slow)

# Initial requirements

We can aggregate based on concepts, on change type, on changed properties.

The set of questions to answer in the diff template are:
1. Statistical: number of added/deleted concepts, labels and other properties
2. Added/deleted/modified concepts
3. Added/deleted/modified labels (pref,alt,hidden)
4. Added/deleted/modified notations (the actual notation, identifiers, (to be added later))
5. Added/deleted/modified notes (definition, scope, editorial, (to be added later))
6. Other changed properties (successors, predecessors, start date, end date)

For the aforementioned 3,4 and 5 we must take into account that "simple/direct" and the reified version of these properties. We will start with the simple version at first and build on that. 

# Further reading:

https://www.w3.org/TR/skos-reference/

https://github.com/eu-vocabularies/skos-history-query-generator 

https://github.com/eu-vocabularies/skos-history