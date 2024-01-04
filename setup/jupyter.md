start jupyter:
```
jupyter notebook --NotebookApp.base_url=/jupyter/
```

config:
```
jupyter notebook --generate-config
```
```
c = get_config()  #noqa

c.NotebookApp.allow_origin = '*'
c.NotebookApp.port = 8888
c.NotebookApp.open_browser = False
c.NotebookApp.allow_remote_access = True
c.NotebookApp.trust_xheaders = True
```