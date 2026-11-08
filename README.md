# HSL Stop CLI

A small Python script for checking upcoming HSL departures from the terminal.

Uses the Digitransit API to look up stops by name or stop number and shows the next five departures, including real-time information when available.

No external Python packages needed.

## Setup

You'll need Python 3 and a [Digitransit API key](https://digitransit.fi/en/developers/).

Put your API key in a file called `api-secrets.txt` in the same directory as the script. The first line should contain your primary key. The file is ignored by Git.

## Usage

Run the script directly:

```bash
python3 hsl-stop.py 4057
python3 hsl-stop.py "Laajasalo"
```

I use a small zsh function to make it easier:

```bash
hsl() {
    if [[ -z "$1" ]]; then
        echo "Anna pysäkkinumero tai nimi"
        return 1
    fi
    python3 "$HOME/projektit/HSL-STOP/hsl-stop.py" "$*"
}
```

Add it to `.zshrc` and adjust the path if needed.

Then just type:

```bash
hsl 4057
hsl Laajasalo
```

## Notes

- Shows up to five departures per matching stop.
- A `•` next to the departure time means real-time information is available.
- Uses only Python's standard library.
- Transport data comes from [Digitransit](https://digitransit.fi/).

Just a small utility I made for my own use.
