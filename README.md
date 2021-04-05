# ESGI subjects database

The project is a web app database using ElasticSearch to easily create, access, update a database of subjects proposed by ESGI.

## Functionalities proposed by the web-app:
- **Log in** with a credential. Each credential is assigned a role allowing access to certain others functionalities. Roles available are: Manager, Professor, Student
- **Add** new subjects to the database 
- **Search** for subjects by criteria: 
    * Text keyword: Match any word that appears in *{Subject's name, Professor's Name, Category, Description}* (users can choose which fields to search).
    * Type of subject: Match all subject of a certain category
    * Coefficient: Match all subjects of a specified coefficient 
    * Course duration: Match any subjects whose duration is in a range 
    * Date: Match any subject being taught completely between a period
- **Sort** the returning results by any field 
- **Calculate** some aggregations:
    * Total hours to pass all the returned subjects
    * Total coefficients acquired after pass all the returned courses
    * The necessary period to pass all the returned courses
- **Delete** subjects matching a query


## Role ability:
- **Manager**: Read, Create, Insert, Modify, Delete
- **Professor**: Read, Modify *{Subject's Name, Description}* of subjects that he/she teaches
- **Student**: Read