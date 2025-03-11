# cotc-client
A project to collect metrics from different sources (device metrics, weather data) to send to a Flask app ([see here](https://github.com/darragh0/cotc-server)).

### To Run
To run this project, you will only be using the `collector` script. `sdk` is just a dependency.

First, navigate to the root directory of this project (`cotc-client`).

Then clone [this repo](https://github.com/darragh0/cotc-common) via:
```sh
git clone https://github.com/darragh0/cotc-common.git
```

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
> It will probably be .\\.venv\Scripts\activate (rather than `source ./.venv/bin/activate`) if you are on Windows.


You should then be able to run the `collector` script. For example:
```sh
collector -v
```

> [!NOTE]
> This project goes hand-in-hand w/ [this project](https://github.com/darragh0/cotc-server).
