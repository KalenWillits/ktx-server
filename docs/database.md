# Database

## Parameters

### models : ModelManager 
Link to the model manager


### data : str , default './'
Path to data if loading or saving has been set.
Accepts a environment variable `DATA` or passed directly. 


### archive : str, default 'archive/'
Experimental, exports the query to lean in-memory data.



## Methods

### create(model_name: str, kwargs)
Creates a new model if the model name is valid with matching kwargs. 

### query(model_name: str, kwargs) -> DataFrame
Queries the database filtering on kwargs and returns a dataframe with matching rows.


### get(model_name: str, pk(optional): str, kwargs) -> Model
Gets a model from the corresponding table. If pk argument exists and matches a row in the query, returns that model.
If not filters on kwargs. An error gets thrown if more than one model is found.


### update(model_name: str, query: DataFrame, kwargs) -> DataFrame
Searches the table matching the model_name and query index. Then it updates all rows with kwargs.


### drop(model_name: str, query: DataFrame, cascade: list[str] = [])
Searches the table matching the model_name and query index and drops those rows. Foreign key fields must be specified in
the cascade list to cascade the drop to other tables.


### get_or_create(model_name: str, kwargs) -> Model
Same as get except if the model matching kwargs does not exists, one is created and returned.


### hydrate(model_name: str, query: DataFrame):
Returns a list of dictionaries with all nested foreign key values from the query.


### save():
Saves all tables to an individual json file at self.data.


### load():
Loads all tables from save.

