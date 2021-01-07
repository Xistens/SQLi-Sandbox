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
Remember to change the secret_key and flag_key.  
If `app.debug` is set to True, then the API will be enabled where it is possible to get all the flags for each challenge as a JSON object. Send a GET request to `/api/v1/getFlags` to  get the flags.  

**NB:** There is no authentication required to dump the flags, so ensure that `app.debug` is set to False to disable the API before releasing.

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


## Challenge Configuration

| Config | Description | Type  | Required | Default
|--------|-------------|-------|----------|--------
| name | Name of challenge folder/path. If the name is "challenge1", the URL will be http://<IP>/challenges/challenge1 | String |Yes| |
|title| The display name of the challenge |String |Yes| |
|tags| Currently not in use | List of strings | No| |
|difficulty| The difficulty of the challenge |String| Yes | |
| description | The challenge description shown to the user | String | No | |
|limier| Rate limiting for challenge | String | No | If not presented, rate limiting is disabled |
|database: drivername| Only supporting SQLite, but added incase support for other drivers should be needed | String | Yes| |
|track: track_id| ID of the track/group the challenge belongs to |Integer|Yes| |
|track: position_in_track| Used to order challenges inside the track|Integer|Yes| |
|enabled|Enable/disable challenge |Bool| no| Default enabled|
|allow_guidance| Enable/disable tutorial slides for challenge |Bool| no| Default enabled |
|allow_debug_query| Enable/disable SQL query display for challenge |Bool| no| Default enabled |
