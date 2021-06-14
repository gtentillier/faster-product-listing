
# faster-product-listing Scrapper

## Some Requirements

1. Create an account on Vestiaire Collective

2. Get your payload which will be posted for logging-in to your account i.e {digest, email, password}
* Install Firefox and enable web developer tools <space><space>*<space>
* Check the POST method request details against https://apiv2.vestiairecollective.com/sessions/ API <space><space>*<space>

3. Once you find your payload, replace the data items with yours = '{"email":"fkxav246@gmail.com","password":"123456789WwQ@!","digest":"v1fd4e3c2c18"}' <space><space>*<space>

4. You are all set, just run the start_scrapping one by one for all the categories but make sure to add some delay because vestiairecollective aborts the connection if the scrapping is done in huge amount.
