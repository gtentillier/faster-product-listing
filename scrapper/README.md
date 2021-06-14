
# Vestiaire Collective Scrapper

## Installation and requirements

1. Create a virtual environment, and activate it

   ```:bash
   conda create -n clipdrop-scrapper python=3.6.6
   conda activate clipdrop-scrapper
   ```

2. Install dependencies

   ```:bash
   python3 -m pip install -r requirements.txt
   ```

## Vestiaire Collective Requirements

1. Create an account on Vestiaire Collective

2. Get your payload which will be posted for logging-in to your account i.e {digest, email, password}
```:bash
Install Firefox and enable web developer tools
```
```:bash
Check the POST method request details against https://apiv2.vestiairecollective.com/sessions/ - API
```
3. Once you find your payload, replace the data values with yours, data = '{"email":"fkxav246@gmail.com","password":"123456789WwQ@!","digest":"v1fd4e3c2c18"}' <space><space>*<space>

4. You are all set, just run the start_scrapping one by one for all the categories but make sure to add some delay because vestiairecollective aborts the connection if the scrapping is done in huge amount.
