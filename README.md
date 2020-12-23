## Install
1. `git clone https://github.com/Xistens/SQLi-Sandbox.git`
2. Navigate to the SQLi-Sandbox folder
3. Make the install script executable:  
`chmod +x install.sh`
4. Install the application:  
`./install.sh`

The install script will set up a service for the application that will start on boot. The script will also start the service after execution.

## Start
To start the server manually, navigate to the SQLi-Sandbox folder and execute:  
`python3 server.py`

## Configuration
Basic settings can be configured inside `sqli_platform/__init__.py`

Remember to change the secret_key and flag_key.  
If `app.debug` is set to True, then the API will be enabled where it is possible to get all the flags for each challenge as a JSON object. Send a GET request to `/api/v1/getFlags` to  get the flags.  

**NB:** There are no authentication required to dump the flags, so ensure that `app.debug` is set to False to disable the API if needed.

| Config | Description |Default
|--------|-------------|-------|
|enable_debug_query| Enable/Disable displaying executed SQL query (True/False) for the entire app | True|
|enable_guidance| Enable/Disable displaying guidance/tutorial (True/False) for the entire app | True|
|debug_query_default| Default value for debug query (If False, the user must enable it themselves)| True|
|guidance_default| Default value for guidance/tutorial (If False, the user must enable it themselves)|False|
|enable_download|Enable/disable the download page| True|
|flag_key|The key to use when generating challenge flags (MD5(key + challenge title))|xV6WxVghQ7fFxarqnyj5EYwPmrGZgt4Q|
|flag_format|"Format of the flag. {FLAG}" will be replaced with the MD5 sum of challenge title and flag_key|THM{{FLAG}}|
|LOG_FOLDER| The folder where logs will be stored|{_basedir}/logs|