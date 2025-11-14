# IRCC WebForm

This is a IRCC webform auto script, for people who searched and desperately needed this repo, 
may God grant you immediate passage to heaven—because you’ve clearly endured more than enough suffering from IRCC.
Amen.



this project uses uv so after git clone, do uv sync, then do one more for playwright: 
```
playwright install
```
Then it should work for you. create your config.yaml file from config_sample.yaml. if you want to make it more real compare to human, 
use_persistent_profile: true, then fill in your local file location. 

```commandline
uv run webform_runner.py --schedule-count 3
```
Please don't get pass 3 web forms per day, do it at your own risk