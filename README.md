# cotc-client
A project to collect metrics from different sources (device metrics, weather data) and sends to a Flask web app

### To Run
To run this project, you will only be using the `collector` script. The other directories are dependencies.
First, navigate to the root directory of this project (`cotc-client`).

If you have `uv` installed, you can use:
```sh
uv venv
source ./.venv/bin/activate
uv pip install ./collector
```

If you do not have `uv` installed, you can use:
```sh
py -m venv .venv
source ./.venv/bin/activate
pip install ./collector
```

> [!NOTE]  
> It will probably be .\.venv\Scripts\activate (rather than `source ./.venv/bin/activate`) if you are on Windows.


You should then be able to run the `collector` script. For example:
```sh
collector -v
```
