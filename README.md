EA Tool
=======

A collection of purpose-built tools for the EA team. I enjoy automating things, but once this
monster gets too big we'll need to see if another team can take this on :-)

The `eatool indico` subcommand makes use of [indico-cli](https://github.com/DeeKay3/indico-cli).

Installation
============

First, here are the steps to get the package set up:
```bash
pip install git+https://github.com/DeeKay3/eatool.git

# If you get an error about "externally managed environment", run this instead:
apt install pipx
pipx install git+https://github.com/DeeKay3/eatool.git
pipx ensurepath

# If want to upgrade, simply run the respective pip install or pipx install command again:
pipx install git+https://github.com/DeeKay3/eatool.git
```

If you'd like to be able to change the sources or debug something with code, you can do this instead:
```bash
git clone https://github.com/DeeKay3/eatool
cd eatool
pipx install -e .[dev]

# This is how you can upgrade to the latest version
cd eatool
git pull
```

If you are getting errors including `KeyringLocked: Failed to unlock the collection`, you might need
to unlock your keyring. There may be more pretty ways to do this, but here is one way:

```bash
# Do this once. Paste everything including EOF into the command line
cat <<EOF >> ~/.bashrc
function unlock-keyring ()
{
    read -rsp "Password: " pass
    export $(echo -n "$pass" | gnome-keyring-daemon --replace --unlock)
    unset pass
}
EOF

# Afterwards, run this once to load the function, or start a new terminal.
source ~/.bashrc

# Do this any time you need to unlock the keyring
unlock-keyring
```


Now you should be able to run `eatool` from anywhere. On the first run you'll need to enter the
OAuth client secret. Reach out to me internally to get it.

Examples
========

Register attendees to an event or update their fields, taking the data from a Google Sheet
```
eatool gsuite sheetcsv https://docs.google.com/spreadsheets/.../edit | eatool indico regeditcsv 8 11 -
```


Update the attendees of a Google Calendar event using the email addresses from a certain sprint
```bash
# Find the id of the opening plenary
$ eatool gsuite list-events "Engineering Sprint" -q "Opening Plenary"
11lvgncouqpa4d5b65n61e7jnh: Opening Plenary (2022-02-28T08:30:00+01:00 to 2022-02-28T09:30:00+01:00)
6466imanh8nfi198448mfcb6qa: Opening Plenary (2022-10-31T08:30:00+01:00 to 2022-10-31T09:30:00+01:00)
3aav7lcef1ob6a8isp37913g0m: Opening Plenary (2023-05-01T08:00:00+02:00 to 2023-05-01T09:00:00+02:00)

# Update attendees. First command gets the email addresses, passes it on to the second command to
# add the attendees to the event. You can pass more than one event id.
$ eatool indico regquery 4 4 -q "Engineering Sprint" true |  eatool gsuite attendees -f - "Engineering Sprint" 3aav7lcef1ob6a8isp37913g0m

# Or do the same as the last command in two steps with an intermediate file, helps you verify you've
# got the right people, or to update multiple events with the same list.
$ eatool indico regquery 4 4 -q "Engineering Sprint" true > sprint_attendees.txt
$ eatool gsuite attendees "Engineering Sprint" 3aav7lcef1ob6a8isp37913g0m -f sprint_attendees.txt
$ rm sprint_attendees.txt # remove the intermediate file
```
