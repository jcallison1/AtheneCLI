# Athene CLI

This is a CLI for [Athene](https://athenecurricula.org/) that allows sumbitting files for grading directly from your command line.

# Install

Installation is simple: download [athene.py](https://raw.githubusercontent.com/jcallison1/AtheneCLI/main/athene.py) to somewhere on your computer.

For the Lipscomb SoC tools server, you can install it by running this command:
```
curl -L -o ~/athene.py 'https://raw.githubusercontent.com/jcallison1/AtheneCLI/main/athene.py' && chmod +x ~/athene.py
```
Then you can run it with:
```
~/athene.py
```
Note that AtheneCLI requires the `requests` Python package. The SoC tools server already has this package, but for your local machine you can install it with:
```
pip3 install -U requests
```

# Usage

To submit a file for grading:
```
~/athene.py submit <file>
```
AtheneCLI will ask you for the assignment ID and your auth token. Both can be manuallly extracted from the Athene assignment page, or more easily copied by using the AtheneCLI browser extension. Once you have entered the ID and auth token once, they will be cached and you won't have to enter them again for the current directory unless the auth token expires.

You can see the results of your last submission using:
```
~/athene.py status
```

# Browser Extension

The browser extension allows you to copy the assignment ID and auth token for an Athene page by clicking on two links at the bottom of the page.

## Install on Firefox

1. Download the [extension ZIP file](https://raw.githubusercontent.com/jcallison1/AtheneCLI/main/browser-extension/athene-cli-browser-ext.zip).
2. Go to about:debugging in Firefox.
3. Click on "This Firefox".
4. Click "Load Temporary Add-on".
5. Select the ZIP file you downloaded.

The extension should now be installed. It may say that there's a warning, just ignore that. The warnings are due to the way I made the extension work for both Firefox and Chrome. Unfortunately, you will have to re-add the extension every time you restart Firefox. I'm looking for a way to prevent this in the future.

## Install on Chrome/Opera

1. Download the [extension ZIP file](https://raw.githubusercontent.com/jcallison1/AtheneCLI/main/browser-extension/athene-cli-browser-ext.zip).
2. Go to chrome://extensions if you're in Chrome, or opera://extensions if you're in Opera/Opera GX.
3. Click the toggle in the top-right corner to enable "Developer mode".
4. Drag the ZIP you downloaded into the browser window. It should say "Drop to install" when you drag the file over the window.

The extension should now be installed. It may say that there are errors, just ignore that. The errors are due to the way I made the extension work for both Firefox and Chrome.
